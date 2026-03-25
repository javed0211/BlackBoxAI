from typing import Dict, Any, Optional
from qa_agent.integrations.ado_client import ado_client

def create_ado_bug(title: str, description: str, area_path: str = None) -> str:
    """
    Creates a new Bug work item in Azure DevOps.
    Useful for reporting failed QA missions with evidence.
    """
    try:
        bug = ado_client.create_bug(title, description, area_path)
        bug_id = bug.get("id")
        bug_url = bug.get("_links", {}).get("html", {}).get("href", "")
        return f"Successfully created ADO Bug #{bug_id}: {bug_url}"
    except Exception as e:
        return f"Error creating ADO Bug: {e}"

def attach_to_ado_bug(bug_id: int, file_path: str, comment: str = "Evidence attached by Nexus AI") -> str:
    """
    Attaches a forensic artifact (screenshot, video, trace) to an ADO Bug.
    """
    try:
        ado_client.add_attachment(bug_id, file_path, comment)
        return f"Successfully attached file {file_path} to ADO Bug #{bug_id}"
    except Exception as e:
        return f"Error attaching to ADO Bug: {e}"

def update_ado_test_result(run_id: int, case_id: int, outcome: str, comment: str) -> str:
    """
    Updates the execution result for a test case in an ADO Test Run.
    Outcome must be 'Passed', 'Failed', or 'Blocked'.
    """
    try:
        ado_client.update_test_result(run_id, case_id, outcome, comment)
        return f"Successfully updated ADO Test Case #{case_id} in Run #{run_id} to {outcome}."
    except Exception as e:
        return f"Error updating ADO Test Result: {e}"
