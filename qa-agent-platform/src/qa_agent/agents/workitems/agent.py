from typing import List, Any
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from qa_agent.graph.state import GraphState
from qa_agent.agents.base import BaseAgent
from qa_agent.tools.registry import global_registry
from qa_agent.models.provider import get_llm
from langchain_core.tools import tool

@tool
def _create_ado_bug(title: str, description: str, area_path: str = None) -> str:
    """Creates a new Bug work item in Azure DevOps."""
    return global_registry.execute("create_ado_bug", title=title, description=description, area_path=area_path)

@tool
def _attach_to_ado_bug(bug_id: int, file_path: str, comment: str = "Evidence attached") -> str:
    """Attaches a file to an existing ADO Bug."""
    return global_registry.execute("attach_to_ado_bug", bug_id=bug_id, file_path=file_path, comment=comment)

@tool
def _create_jira_bug(project_key: str, summary: str, description: str) -> str:
    """Creates a new Bug issue in Jira."""
    return global_registry.execute("create_jira_bug", project_key=project_key, summary=summary, description=description)

@tool
def _attach_to_jira_bug(issue_key: str, file_path: str) -> str:
    """Attaches a file to a Jira issue."""
    return global_registry.execute("attach_to_jira_bug", issue_key=issue_key, file_path=file_path)

@tool
def _comment_on_jira_issue(issue_key: str, comment: str) -> str:
    """Adds a comment to a Jira issue."""
    return global_registry.execute("comment_on_jira_issue", issue_key=issue_key, comment=comment)

WORKITEM_SYSTEM_PROMPT = """You are the Enterprise Integration Agent for a QA Platform.
Your mission is to map successful or failed QA missions to their respective issue trackers (Jira or Azure DevOps).

MISSION SUMMARY:
{mission_summary}

FAILURE ANALYSIS:
{failure_analysis}

TARGET REPOSITORY:
{workspace}

INSTRUCTIONS:
1. If the mission failed, your priority is to CREATE A BUG.
2. Use the detailed failure analysis to populate the Bug description.
3. Attach the latest HTML report or screenshot if you have the file path.
4. If the user didn't specify between Jira or ADO, check for presence of project keys or org URLs in context.
5. Provide a summary of the ticket created.
"""

class WorkItemAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ADO/Jira Agent")

    def get_tools(self) -> List[Any]:
        return [_create_ado_bug, _attach_to_ado_bug, _create_jira_bug, _attach_to_jira_bug, _comment_on_jira_issue]

    def run(self, state: GraphState) -> GraphState:
        print("[WorkItemAgent] Synchronizing QA results with Enterprise Trackers...")
        
        # If the mission passed and no reporting was requested, we can skip
        if state.validation_passed and "ticket" not in state.mission.user_input.lower():
            print("[WorkItemAgent] Mission passed and no ticket requested. Skipping sync.")
            return state

        llm = get_llm()
        tools = self.get_tools()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", WORKITEM_SYSTEM_PROMPT),
            ("user", "Action: Synchronize the latest findings now."),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        mission_summary = state.final_summary or "Mission completed."
        failure_analysis = "\n".join(state.errors) if state.errors else "No errors detected."
        
        try:
            result = agent_executor.invoke({
                "mission_summary": mission_summary,
                "failure_analysis": failure_analysis,
                "workspace": state.mission.workspace
            })
            
            output = result.get('output', '')
            state.final_summary += f"\n\n[Enterprise Sync]: {output}"
            
        except Exception as e:
            print(f"[WorkItemAgent] Error during sync: {e}")
            state.errors.append(f"Enterprise Sync Failed: {str(e)}")
            
        return state
