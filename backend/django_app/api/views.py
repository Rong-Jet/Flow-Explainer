from django.shortcuts import render
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import requests
from mermaid import Mermaid
import asyncio
from typing import Dict, Any
import logging

# Set up logging
logger = logging.getLogger(__name__)

class HomeView(View):
    def get(self, request):
        return HttpResponse("""
        <html>
            <head>
                <title>Flow Explainer API</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                    h1 { color: #333; }
                    .endpoint { background: #f4f4f4; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
                    code { background: #eee; padding: 2px 4px; border-radius: 3px; }
                </style>
            </head>
            <body>
                <h1>Flow Explainer API</h1>
                <p>This is the backend API for the Flow Explainer application.</p>
                <h2>Available Endpoints:</h2>
                <div class="endpoint">
                    <p><strong>POST /api/generate-diagram/</strong> - Generate a Mermaid diagram from JSON</p>
                </div>
                <div class="endpoint">
                    <p><strong>POST /api/process-json/</strong> - Process JSON file for diagram generation</p>
                </div>
                <p>The React frontend should be running on <a href="http://localhost:3000">http://localhost:3000</a></p>
            </body>
        </html>
        """)

def process_with_langgraph(json_data: Dict[Any, Any]) -> Dict[str, Any]:
    """
    Process JSON data with LangGraph agent and return the result.
    
    Args:
        json_data: The JSON data to process
        
    Returns:
        A dictionary with the processing result
    """
    from langgraph_app.agent import process_json_with_agent
    
    # Run the async function in a synchronous context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(process_json_with_agent(json_data))
        return result
    finally:
        loop.close()

def check_origin(request):
    """
    Check if the request origin is allowed.
    This adds a security layer even when CSRF protection is disabled.
    """
    allowed_origins = [
        'http://localhost:3000',  # Development React server
        'http://127.0.0.1:3000',
        # Add production origins here
    ]
    
    origin = request.META.get('HTTP_ORIGIN', '')
    referer = request.META.get('HTTP_REFERER', '')
    
    # Check origin header first
    if origin and any(origin.startswith(allowed) for allowed in allowed_origins):
        return True
    
    # Check referer as fallback
    if referer and any(referer.startswith(allowed) for allowed in allowed_origins):
        return True
    
    # Default to False
    return False

@method_decorator(csrf_exempt, name='dispatch')
class GenerateDiagramView(View):
    def post(self, request):
        try:
            # Security check for allowed origins
            if not check_origin(request):
                logger.warning(f"Rejected request from unauthorized origin: {request.META.get('HTTP_ORIGIN', '')} / {request.META.get('HTTP_REFERER', '')}")
                return JsonResponse({
                    "success": False,
                    "error": "Unauthorized origin"
                }, status=403)
            
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            
            # Process with LangGraph
            result = process_with_langgraph(data)
            
            if not result.get("success", False):
                return JsonResponse({
                    "success": False,
                    "error": result.get("error", "Unknown error")
                }, status=400)
            
            return JsonResponse({
                "success": True,
                "mermaid_code": result.get("mermaid_code", ""),
                "diagram_image": result.get("diagram_image", "")
            })
        
        except Exception as e:
            logger.error(f"Error in GenerateDiagramView: {str(e)}", exc_info=True)
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class ProcessJsonView(View):
    def post(self, request):
        try:
            # Security check for allowed origins
            if not check_origin(request):
                logger.warning(f"Rejected request from unauthorized origin: {request.META.get('HTTP_ORIGIN', '')} / {request.META.get('HTTP_REFERER', '')}")
                return JsonResponse({
                    "success": False,
                    "error": "Unauthorized origin"
                }, status=403)
            
            # Check if the request has a file
            if 'file' in request.FILES:
                file = request.FILES['file']
                # Read and parse JSON file
                json_content = file.read().decode('utf-8')
                data = json.loads(json_content)
            else:
                # Try to parse the body as JSON
                data = json.loads(request.body)
            
            # Process with LangGraph
            result = process_with_langgraph(data)
            
            if not result.get("success", False):
                return JsonResponse({
                    "error": result.get("error", "Unknown error")
                }, status=400)
            
            # Return the mermaid code and SVG diagram
            response_data = {
                "mermaid_code": result.get("mermaid_code", ""),
                "diagram_image": result.get("diagram_image", "")
            }
            
            # If there's no diagram_image but we have mermaid_code, generate a fallback message
            if not response_data["diagram_image"] and response_data["mermaid_code"]:
                response_data["diagram_image"] = f"""<svg xmlns="http://www.w3.org/2000/svg" width="500" height="200">
                    <rect width="100%" height="100%" fill="#f8f9fa" />
                    <text x="50%" y="80" font-family="Arial" font-size="16" text-anchor="middle">
                        JSON data was processed successfully, but no diagram could be generated.
                    </text>
                    <text x="50%" y="120" font-family="Arial" font-size="14" text-anchor="middle">
                        You can view the Mermaid code in the application.
                    </text>
                </svg>"""
            
            return JsonResponse(response_data)
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON file"}, status=400)
        except Exception as e:
            logger.error(f"Error in ProcessJsonView: {str(e)}", exc_info=True)
            return JsonResponse({"error": f"Error processing request: {str(e)}"}, status=400)
