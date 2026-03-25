from qa_agent.graph.state import GraphState

def summarize_node(state: GraphState) -> GraphState:
    print("Generating final summary...")
    state.final_summary = "Mission successfully completed."
    return state
