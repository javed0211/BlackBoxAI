from qa_agent.graph.state import GraphState
from qa_agent.memory.run_store import SQLiteRunStore

def persist_node(state: GraphState) -> GraphState:
    print("Persisting graph state + artifacts...")
    store = SQLiteRunStore()
    status = "success" if state.validation_passed else "failed"
    store.save_run(state, status)
    return state
