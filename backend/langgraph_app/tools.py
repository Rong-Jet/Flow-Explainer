# Import necessary libraries
import json
from typing import Dict, Any, List

def parse_json_to_mermaid(json_data: Dict[Any, Any]) -> str:
    """
    Parse JSON data and convert it to Mermaid diagram syntax.
    This will be called by the LangGraph agent.
    """
    # Basic implementation - improve based on your requirements
    mermaid_code = "graph TD;\n"
    
    # Keep track of nodes to avoid duplicates
    nodes = set()
    edges = []
    
    def sanitize_label(label):
        """Sanitize labels to avoid Mermaid syntax issues"""
        # Convert to string and escape special characters
        if not isinstance(label, str):
            label = str(label)
        
        # Replace characters that could cause issues in Mermaid
        label = label.replace('"', '\\"')
        label = label.replace(':', ' -')
        label = label.replace(';', ',')
        
        # Truncate very long labels
        if len(label) > 50:
            label = label[:47] + "..."
            
        return label
    
    def sanitize_id(node_id):
        """Create a sanitized node ID for Mermaid diagrams"""
        return f'"{node_id}"'
    
    def process_value(key, value, parent_id=None, depth=0):
        """Recursively process JSON values, creating nodes and edges"""
        if depth > 5:  # Limit recursion depth to prevent overly complex diagrams
            return
        
        node_id = f"N{len(nodes)}"
        key_label = sanitize_label(key)
        
        # Add node
        node_def = f"    {sanitize_id(node_id)}[{key_label}]\n"
        if node_def not in nodes:
            nodes.add(node_def)
            mermaid_code_parts.append(node_def)
        
        # Add edge from parent if exists
        if parent_id is not None:
            edge = f"    {sanitize_id(parent_id)} --> {sanitize_id(node_id)}\n"
            if edge not in edges:
                edges.append(edge)
                mermaid_code_parts.append(edge)
        
        # Process children based on type
        if isinstance(value, dict):
            for k, v in value.items():
                process_value(k, v, node_id, depth + 1)
        elif isinstance(value, list):
            # For arrays, create child nodes for each item
            if len(value) > 10:  # Limit number of array items to prevent diagram overload
                array_node_id = f"A{len(nodes)}"
                array_node = f"    {sanitize_id(array_node_id)}[Array with {len(value)} items]\n"
                if array_node not in nodes:
                    nodes.add(array_node)
                    mermaid_code_parts.append(array_node)
                
                array_edge = f"    {sanitize_id(node_id)} --> {sanitize_id(array_node_id)}\n"
                if array_edge not in edges:
                    edges.append(array_edge)
                    mermaid_code_parts.append(array_edge)
            else:
                for i, item in enumerate(value):
                    item_label = f"Item {i}"
                    if isinstance(item, dict) and len(item) == 1:
                        # If it's a single property dict, use the property name
                        item_label = list(item.keys())[0]
                    
                    process_value(item_label, item, node_id, depth + 1)
        else:
            # For primitive values, add a value node
            if value is not None:  # Skip None values
                value_id = f"V{len(nodes)}"
                value_label = sanitize_label(value)
                value_node = f"    {sanitize_id(value_id)}[{value_label}]\n"
                
                if value_node not in nodes:
                    nodes.add(value_node)
                    mermaid_code_parts.append(value_node)
                
                value_edge = f"    {sanitize_id(node_id)} --> {sanitize_id(value_id)}\n"
                if value_edge not in edges:
                    edges.append(value_edge)
                    mermaid_code_parts.append(value_edge)
    
    # Initialize the mermaid code parts
    mermaid_code_parts = [mermaid_code]
    
    # Root level processing
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            process_value(key, value)
    elif isinstance(json_data, list):
        for i, item in enumerate(json_data):
            item_label = f"Item {i}"
            if isinstance(item, dict) and len(item) == 1:
                item_label = list(item.keys())[0]
            process_value(item_label, item)
    else:
        # Handle primitive types
        process_value("Value", json_data)
    
    # Join all parts
    return "".join(mermaid_code_parts)

def validate_json(json_data: Dict[Any, Any]) -> bool:
    """
    Validate if the JSON can be processed for diagram generation.
    """
    # Check if json_data is a dictionary
    if not isinstance(json_data, dict) and not isinstance(json_data, list):
        raise ValueError("JSON data must be an object or array")
    
    # Check if the JSON is too large
    json_str = json.dumps(json_data)
    if len(json_str) > 100000:  # Limit to 100KB
        raise ValueError("JSON data is too large")
    
    return True

def generate_svg_from_mermaid(mermaid_code: str) -> str:
    """
    Generate SVG from Mermaid code.
    Uses the Mermaid.ink service to render the diagram.
    """
    import base64
    import requests
    import urllib.parse
    import logging
    
    # Configure logging for easier debugging
    logger = logging.getLogger(__name__)
    
    try:
        # Clean up the Mermaid code to ensure it's valid
        mermaid_code = mermaid_code.strip()
        
        # Log the Mermaid code for debugging
        logger.info(f"Generating SVG from Mermaid code:\n{mermaid_code}")
        
        # URL-safe base64 encoding
        encoded = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
        
        # First attempt: Use the Mermaid.ink service to render the SVG
        url = f"https://mermaid.ink/svg/{encoded}"
        logger.info(f"Requesting SVG from: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.text
        
        # Second attempt: Try the alternative service quickchart.io
        logger.warning(f"Mermaid.ink failed with status {response.status_code}, trying fallback service")
        
        # Prepare the request to quickchart.io
        quickchart_url = "https://quickchart.io/graphviz"
        payload = {
            "graph": "digraph { " + 
                     " ".join([line.strip() for line in mermaid_code.split('\n') 
                              if '-->' in line or '-.->' in line]) + " }"
        }
        
        response = requests.post(quickchart_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return response.text
        
        # Third attempt: Generate a simple SVG placeholder
        logger.error(f"All rendering services failed. Creating placeholder SVG.")
        simple_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="500" height="300">
            <rect width="100%" height="100%" fill="#f8f9fa" />
            <text x="50%" y="50%" font-family="Arial" font-size="16" text-anchor="middle">
                JSON Visualization (rendering services unavailable)
            </text>
            <foreignObject x="50" y="100" width="400" height="150">
                <body xmlns="http://www.w3.org/1999/xhtml">
                    <pre style="font-size: 10px; overflow: hidden;">
                    {mermaid_code[:1000] if len(mermaid_code) > 1000 else mermaid_code}
                    </pre>
                </body>
            </foreignObject>
        </svg>"""
        return simple_svg
        
    except Exception as e:
        logger.exception("Error generating SVG")
        
        # Generate a fallback SVG with the error message
        error_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="500" height="200">
            <rect width="100%" height="100%" fill="#f8f9fa" />
            <text x="50%" y="50" font-family="Arial" font-size="16" text-anchor="middle" fill="red">
                Error Generating Diagram
            </text>
            <text x="50%" y="80" font-family="Arial" font-size="12" text-anchor="middle">
                {str(e)[:100]}
            </text>
            <text x="50%" y="120" font-family="Arial" font-size="14" text-anchor="middle">
                Your JSON data was successfully processed,
            </text>
            <text x="50%" y="140" font-family="Arial" font-size="14" text-anchor="middle">
                but we couldn't render it as a diagram.
            </text>
        </svg>"""
        return error_svg
