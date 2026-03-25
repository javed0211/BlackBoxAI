from qa_agent.graph.state import GraphState

def select_agents_node(state: GraphState) -> GraphState:
    # Agents were selected by LLM in classify node
    print(f"Agents LLM Selected: {state.selected_agents} (Mode: {state.execution_mode})")
    
    if not state.selected_agents:
        # Fallback if somehow empty
        state.selected_agents = ["Orchestrator Agent"]
        state.execution_mode = "single"
        
    return state
