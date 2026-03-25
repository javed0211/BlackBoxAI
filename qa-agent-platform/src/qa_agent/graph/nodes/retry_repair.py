from qa_agent.graph.state import GraphState

def retry_repair_node(state: GraphState) -> GraphState:
    print("Retrying / Repairing issues...")
    state.retries += 1
    return state
