from qa_agent.graph.state import GraphState
from qa_agent.agents.orchestrator.agent import OrchestratorAgent
from qa_agent.agents.qa.agent import QAAgent
from qa_agent.agents.browser.agent import BrowserAgent
from qa_agent.agents.workitems.agent import WorkItemAgent


def execute_flow_node(state: GraphState) -> GraphState:
    print(f"Executing flow using {state.execution_mode} strategy...")
    print(f"Agents involved: {state.selected_agents}")
    
    # Initialize agents
    orchestrator = OrchestratorAgent()
    qa_agent = QAAgent()
    browser_agent = BrowserAgent()
    workitem_agent = WorkItemAgent()

    
    for agent_name in state.selected_agents:
        if agent_name == "Orchestrator Agent":
            state = orchestrator.run(state)
        elif agent_name == "QA Agent":
            state = qa_agent.run(state)

        elif agent_name == "Browser Agent":
            from qa_agent.agents.browser.agent import browser_agent
            state = browser_agent.run(state)
        elif agent_name == "Coding Agent":
            print(f"[{agent_name}] Agent is either not online or not configured properly.")
            state.errors.append(f"{agent_name} is either not online or not configured properly.")
            state.validation_passed = False
        elif agent_name == "ADO/Jira Agent":
            state = workitem_agent.run(state)

        else:
            print(f"Agent {agent_name} is not available in Phase 1.")

    # ------------------
    # Memory Optimization
    # ------------------
    from qa_agent.memory.compactor import compactor
    if compactor.should_compact(state):
        try:
            state = compactor.compact(state)
        except Exception as e:
            print(f"[MemoryCompactor] Warning: Failed to compact state: {e}")

    return state
