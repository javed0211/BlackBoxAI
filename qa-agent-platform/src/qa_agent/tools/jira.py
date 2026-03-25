from typing import Dict, Any, Optional
from qa_agent.integrations.jira_client import jira_client

def create_jira_bug(project_key: str, summary: str, description: str) -> str:
    """
    Creates a new Bug issue in Jira Software Cloud.
    Useful for tracking defects found during QA missions.
    """
    try:
        issue = jira_client.create_issue(project_key, summary, description, "Bug")
        issue_key = issue.get("key")
        issue_url = f"{jira_client.host}/browse/{issue_key}"
        return f"Successfully created Jira Bug {issue_key}: {issue_url}"
    except Exception as e:
        return f"Error creating Jira Bug: {e}"

def attach_to_jira_bug(issue_key: str, file_path: str) -> str:
    """
    Attaches a forensic artifact (screenshot, video, report) to a Jira Issue.
    """
    try:
        jira_client.add_attachment(issue_key, file_path)
        return f"Successfully attached file {file_path} to Jira Issue {issue_key}."
    except Exception as e:
        return f"Error attaching to Jira Bug: {e}"

def comment_on_jira_issue(issue_key: str, comment: str) -> str:
    """
    Updates a Jira issue with new execution details or a summary.
    """
    try:
        jira_client.add_comment(issue_key, comment)
        return f"Successfully posted comment to Jira Issue {issue_key}."
    except Exception as e:
        return f"Error commenting on Jira Issue: {e}"
