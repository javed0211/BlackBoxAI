from typing import List, Any
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from qa_agent.graph.state import GraphState
from qa_agent.agents.base import BaseAgent
from qa_agent.tools.registry import global_registry
from qa_agent.models.provider import get_llm
from qa_agent.agents.workitems.mapper import test_mapper
from langchain_core.tools import tool

@tool
def _fetch_jira_issue(issue_key: str) -> str:
    """Fetches full issue details from Jira."""
    from qa_agent.integrations.jira_client import jira_client
    try:
        issue = jira_client.get_issue(issue_key)
        summary = issue.get("fields", {}).get("summary", "")
        desc = issue.get("fields", {}).get("description", "")
        return f"Issue {issue_key}: {summary}\n\nDescription: {desc}"
    except Exception as e:
        return f"Failed to fetch Jira issue {issue_key}: {e}"

@tool
def _fetch_ado_bug(bug_id: int) -> str:
    """Fetches full bug details from Azure DevOps."""
    from qa_agent.integrations.ado_client import ado_client
    try:
        bug = ado_client.get_work_item(bug_id)
        summary = bug.get("fields", {}).get("System.Title", "")
        desc = bug.get("fields", {}).get("System.Description", "")
        return f"Bug {bug_id}: {summary}\n\nDescription: {desc}"
    except Exception as e:
        return f"Failed to fetch ADO bug {bug_id}: {e}"

QA_SYSTEM_PROMPT = """You are the Senior QA Analyst (Group 4 Test Authoring).
Your job is to translate high-level requirements or manual test cases (from Jira/ADO) into structured automation plans.

REUSABLE SKILLS AVAILABLE:
- Login to Admin
- Search Product
- Submit Checkout

INSTRUCTIONS:
1. If the user provided a ticket ID, use the fetch tools to get the manual steps.
2. Call the 'test_mapper' logic (internal) to synthesize steps.
3. Your final output should be a clear, step-by-step automation mission that the Browser Agent can execute.
"""

class QAAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="QA Agent")

    def get_tools(self) -> List[Any]:
        return [_fetch_jira_issue, _fetch_ado_bug]

    def run(self, state: GraphState) -> GraphState:
        print("[QAAgent] Synthesizing test cases from plain English & work items (Group 4)...")
        
        # If the intent is test generation, we perform Group 4 logic
        if state.intent == "test_generation":
            llm = get_llm()
            tools = self.get_tools()
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", QA_SYSTEM_PROMPT),
                ("user", "Mission: {input}"),
                ("placeholder", "{agent_scratchpad}"),
            ])
            
            agent = create_tool_calling_agent(llm, tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            
            try:
                result = agent_executor.invoke({"input": state.mission.user_input})
                output = result.get('output', '')
                
                # We update the mission input for the next agent (Browser Agent) to be the synthesized plan
                state.mission.user_input = f"Execute this synthesized test plan: {output}"
                print(f"✅ [QAAgent] New automation plan generated: {output[:100]}...")
                
            except Exception as e:
                print(f"[QAAgent] Error during test synthesis: {e}")
                state.errors.append(f"QA Agent Synthesis Failed: {str(e)}")
        
        return state
