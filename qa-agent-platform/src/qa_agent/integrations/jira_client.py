import requests
from typing import Dict, Any, Optional, List
from qa_agent.config.settings import settings
import os

class JiraClient:
    """
    Communicates with Jira Software Cloud API for defect and requirement traceability.
    """
    def __init__(self):
        self.host = settings.jira.host
        self.email = settings.jira.email
        self.api_token = settings.jira.api_token
        self._auth = (self.email, self.api_token)
        self._base_url = f"{self.host}/rest/api/3"

    def create_issue(self, project_key: str, summary: str, description: str, issue_type: str = "Bug") -> Dict[str, Any]:
        """Creates a Jira Issue (Bug/Task/Story)."""
        url = f"{self._base_url}/issue"
        
        # Payload for V3 API (Rich Text)
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": description}
                            ]
                        }
                    ]
                },
                "issuetype": {"name": issue_type}
            }
        }
        
        response = requests.post(url, json=payload, auth=self._auth)
        response.raise_for_status()
        return response.json()

    def add_comment(self, issue_key: str, body: str) -> Dict[str, Any]:
        url = f"{self._base_url}/issue/{issue_key}/comment"
        
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": body}
                        ]
                    }
                ]
            }
        }
        
        response = requests.post(url, json=payload, auth=self._auth)
        response.raise_for_status()
        return response.json()

    def add_attachment(self, issue_key: str, file_path: str) -> Dict[str, Any]:
        """Uploads a file and attaches it to a Jira Issue."""
        url = f"{self._base_url}/issue/{issue_key}/attachments"
        
        headers = {
            "X-Atlassian-Token": "no-check"
        }
        
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, auth=self._auth, headers=headers, files=files)
            
        response.raise_for_status()
        return response.json()

jira_client = JiraClient()
