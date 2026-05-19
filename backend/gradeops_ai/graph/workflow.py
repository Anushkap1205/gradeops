from langgraph.graph import StateGraph, END
from gradeops_ai.graph.state import GraphState
from gradeops_ai.graph.nodes import extract_text_node, parse_text_node, evaluate_node

def route_after_ocr(state: GraphState) -> str:
    if state.get("error"):
        return END
    return "parse"

def route_after_parse(state: GraphState) -> str:
    if state.get("error"):
        return END
    return "evaluate"

def build_workflow():
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("ocr", extract_text_node)
    workflow.add_node("parse", parse_text_node)
    workflow.add_node("evaluate", evaluate_node)
    
    # Set entry point
    workflow.set_entry_point("ocr")
    
    # Add edges with conditional routing
    workflow.add_conditional_edges("ocr", route_after_ocr)
    workflow.add_conditional_edges("parse", route_after_parse)
    workflow.add_edge("evaluate", END)
    
    return workflow.compile()
