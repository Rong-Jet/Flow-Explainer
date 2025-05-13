from typing import Dict, List, Tuple, Any, TypedDict, Annotated
import json
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from .tools import parse_json_to_mermaid, validate_json, generate_svg_from_mermaid
from .config import OPENAI_API_KEY, DEFAULT_MODEL, TEMPERATURE

# Define state schema
class AgentState(TypedDict):
    json_data: Dict[Any, Any]
    messages: List[AnyMessage]
    valid_json: bool
    mermaid_code: str
    diagram_svg: str
    error: str
    error_node: str  # Track which node produced the error

# Initialize LLM
llm = ChatOpenAI(
    model=DEFAULT_MODEL,
    temperature=TEMPERATURE,
    openai_api_key=OPENAI_API_KEY
)

# Define nodes
def validate(state: AgentState) -> AgentState:
    """Validate the JSON input"""
    try:
        valid = validate_json(state["json_data"])
        return {"valid_json": valid}
    except Exception as e:
        error_message = str(e)
        context = "We couldn't validate your JSON structure. "
        if "too large" in error_message:
            context += "The file exceeds our size limits. Please try a smaller JSON file."
        else:
            context += "Please check that your JSON is properly formatted."
        return {"valid_json": False, "error": f"{context} Technical details: {error_message}", "error_node": "validate"}

def generate_mermaid(state: AgentState) -> AgentState:
    """Generate Mermaid code from JSON"""
    try:
        mermaid_code = parse_json_to_mermaid(state["json_data"])
        return {"mermaid_code": mermaid_code}
    except Exception as e:
        error_message = str(e)
        context = "We encountered an issue while converting your JSON to a diagram. "
        if "dict" in error_message or "list" in error_message:
            context += "Your JSON structure may be too complex or nested too deeply."
        else:
            context += "There might be elements in your JSON that we can't properly represent."
        return {"error": f"{context} Technical details: {error_message}", "error_node": "generate_mermaid"}

def render_diagram(state: AgentState) -> AgentState:
    """Render SVG diagram from Mermaid code"""
    try:
        # Our improved generate_svg_from_mermaid always returns an SVG
        # Either a real diagram or a fallback, without raising exceptions
        svg = generate_svg_from_mermaid(state["mermaid_code"])
        
        # Check if the SVG is likely a valid diagram (not a fallback or error message)
        if "Error Generating Diagram" in svg or "rendering services unavailable" in svg:
            # The SVG is a fallback/error SVG, but we'll still show it to the user
            # Just log a warning
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Using fallback SVG for diagram rendering")
        
        return {"diagram_svg": svg}
    except Exception as e:
        error_message = str(e)
        context = "We couldn't render the diagram from the generated Mermaid code. "
        if "syntax" in error_message.lower():
            context += "There might be a syntax issue in the generated diagram code."
        else:
            context += "This might be due to an internal rendering issue."
        return {"error": f"{context} Technical details: {error_message}", "error_node": "render_diagram"}

# Define router logic
def router(state: AgentState) -> str:
    """Route to the next node based on state"""
    if state.get("error"):
        return END
    if not state.get("valid_json", True):
        return END
    if not state.get("mermaid_code"):
        return "generate_mermaid"
    if not state.get("diagram_svg"):
        return "render_diagram"
    return END

# Create workflow
def create_agent_workflow():
    """Create the langgraph workflow"""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("validate", validate)
    workflow.add_node("generate_mermaid", generate_mermaid)
    workflow.add_node("render_diagram", render_diagram)
    
    # Add edges
    workflow.add_edge("validate", "generate_mermaid")
    workflow.add_edge("generate_mermaid", "render_diagram")
    
    # Set entrypoint
    workflow.set_entry_point("validate")
    
    # Add conditional edges
    workflow.add_conditional_edges("validate", router)
    workflow.add_conditional_edges("generate_mermaid", router)
    workflow.add_conditional_edges("render_diagram", router)
    
    return workflow.compile()

# Main agent function to be called from Django
async def process_json_with_agent(json_data: Dict[Any, Any]) -> Dict[str, Any]:
    """Process JSON data using the langgraph agent"""
    workflow = create_agent_workflow()
    
    # Initialize state
    initial_state = {
        "json_data": json_data,
        "messages": [],
        "valid_json": None,
        "mermaid_code": "",
        "diagram_svg": "",
        "error": "",
        "error_node": ""
    }
    
    # Run workflow
    result = await workflow.ainvoke(initial_state)
    
    # Return results
    if result.get("error"):
        return {
            "success": False,
            "error": result["error"],
            "error_node": result.get("error_node", "unknown")
        }
    
    return {
        "success": True,
        "mermaid_code": result["mermaid_code"],
        "diagram_image": result["diagram_svg"]
    }
