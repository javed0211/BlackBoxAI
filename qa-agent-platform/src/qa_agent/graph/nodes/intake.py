from qa_agent.graph.state import GraphState

def intake_node(state: GraphState) -> GraphState:
    print(f"Intake Node executing. Mission ID: {state.mission.mission_id}")
    return state
