from .state import GraphState

def route_after_validation(state: GraphState) -> str:
    """Route after validation is complete"""
    if state.validation_passed:
        return "summarize"
    else:
        # Check if max retries exceeded
        # e.g., max_retries could be config-based or pulled from state
        max_retries = 2
        if state.retries >= max_retries:
            return "persist"
        return "retry_repair"
