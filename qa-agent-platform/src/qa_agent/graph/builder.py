from langgraph.graph import StateGraph, END
from typing import TypedDict
from .state import GraphState
from .nodes.intake import intake_node
from .nodes.classify import classify_intent_node
from .nodes.plan import generate_plan_node
from .nodes.select_agents import select_agents_node
from .nodes.execute import execute_flow_node
from .nodes.validate import validate_node
from .nodes.retry_repair import retry_repair_node
from .nodes.summarize import summarize_node
from .nodes.persist import persist_node
from .edges import route_after_validation

def build_graph():
    workflow = StateGraph(GraphState)

    # Add Nodes
    workflow.add_node("intake", intake_node)
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("generate_plan", generate_plan_node)
    workflow.add_node("select_agents", select_agents_node)
    workflow.add_node("execute_flow", execute_flow_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("retry_repair", retry_repair_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("persist", persist_node)

    # Add Edges
    workflow.set_entry_point("intake")
    workflow.add_edge("intake", "classify_intent")
    workflow.add_edge("classify_intent", "generate_plan")
    workflow.add_edge("generate_plan", "select_agents")
    workflow.add_edge("select_agents", "execute_flow")
    workflow.add_edge("execute_flow", "validate")
    
    # Conditional edge after validation
    workflow.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "summarize": "summarize",
            "retry_repair": "retry_repair",
            "persist": "persist" # if max retries exceeded
        }
    )
    
    workflow.add_edge("retry_repair", "validate")
    workflow.add_edge("summarize", "persist")
    workflow.add_edge("persist", END)

    return workflow.compile()
