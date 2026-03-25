from qa_agent.graph.state import GraphState

def validate_node(state: GraphState) -> GraphState:
    print("Validating execution results...")
    if not state.errors:
        state.validation_passed = True
    else:
        state.validation_passed = False
        for error in state.errors:
            print(f"Validation FAILS: {error}")
    return state
