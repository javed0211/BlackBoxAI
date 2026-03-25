from qa_agent.graph.state import GraphState
from qa_agent.agents.orchestrator.prompt import orchestrator_prompt
from qa_agent.agents.orchestrator.schemas import OrchestratorDecision
from qa_agent.models.provider import get_llm

def classify_intent_node(state: GraphState) -> GraphState:
    print(f"Classifying intent with LLM for: {state.mission.user_input}")
    
    llm = get_llm()
    structured_llm = llm.with_structured_output(OrchestratorDecision)
    chain = orchestrator_prompt | structured_llm
    
    from qa_agent.rules.loader import load_rules
    rules_context = load_rules(["common"])

    try:
        decision = chain.invoke({
            "rules": rules_context,
            "mission": state.mission.user_input,
            "workspace": state.mission.workspace,
            "dry_run": state.mission.dry_run,
            "approval_mode": state.mission.approval_mode
        })
        
        # Hydrate state with LLM decisions
        state.intent = decision.intent
        state.plan_summary = decision.plan_summary
        state.selected_agents = decision.selected_agents
        state.execution_mode = decision.execution_mode
        
        print(f"-> Intent Classified: {state.intent} (Confidence: {decision.confidence_score})")
    except Exception as e:
        print(f"Error classifying intent: {e}")
        # Fallback defaults
        state.intent = "code_fix"
        state.plan_summary = "Fallback plan due to API error."
        state.selected_agents = ["QA Agent"]
        state.execution_mode = "single"
        
    return state
