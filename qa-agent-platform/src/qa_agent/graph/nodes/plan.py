from qa_agent.graph.state import GraphState

def generate_plan_node(state: GraphState) -> GraphState:
    # Orchestrator already generated the plan in the classify node
    # Here we could theoretically expand it into step-by-step tasks
    print(f"Planning Execution: {state.plan_summary}")
    return state
