import base64
import requests
from typing import Dict, Any, Optional, List
from qa_agent.config.settings import settings

class AzureDevOpsClient:
    """
    Communicates with Azure DevOps REST API for Bug tracking and Test Management.
    """
    def __init__(self):
        self.org_url = settings.ado.org_url
        self.project = settings.ado.project
        self.pat = settings.ado.pat
        self._auth = ("", self.pat)
        self._base_url = f"{self.org_url}/{self.project}/_apis"

    def create_bug(self, title: str, description: str, area_path: str = None, iteration_path: str = None) -> Dict[str, Any]:
        """Creates a Bug in Azure DevOps and returns the work item JSON."""
        url = f"{self._base_url}/wit/workitems/$Bug?api-version=7.1"
        
        operations = [
            {"op": "add", "path": "/fields/System.Title", "value": title},
            {"op": "add", "path": "/fields/System.Description", "value": description},
            {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority", "value": 1},
            {"op": "add", "path": "/fields/System.Reason", "value": "New"}
        ]
        
        if area_path:
            operations.append({"op": "add", "path": "/fields/System.AreaPath", "value": area_path})
        if iteration_path:
            operations.append({"op": "add", "path": "/fields/System.IterationPath", "value": iteration_path})

        headers = {"Content-Type": "application/json-patch+json"}
        response = requests.post(url, json=operations, auth=self._auth, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_work_item(self, work_item_id: int) -> Dict[str, Any]:
        url = f"{self._base_url}/wit/workitems/{work_item_id}?api-version=7.1"
        response = requests.get(url, auth=self._auth)
        response.raise_for_status()
        return response.json()

    def add_attachment(self, work_item_id: int, file_path: str, comment: str = "Attached by Nexus AI Agent") -> Dict[str, Any]:
        """Uploads a file and links it to an existing work item."""
        # 1. Upload the file to Azure DevOps
        file_name = os.path.basename(file_path)
        upload_url = f"{self.org_url}/_apis/wit/attachments?fileName={file_name}&api-version=7.1"
        
        with open(file_path, "rb") as f:
            upload_response = requests.post(upload_url, data=f, auth=self._auth, headers={"Content-Type": "application/octet-stream"})
        
        upload_response.raise_for_status()
        attachment_url = upload_response.json()["url"]

        # 2. Link the attachment to the work item
        link_url = f"{self._base_url}/wit/workitems/{work_item_id}?api-version=7.1"
        operations = [
            {
                "op": "add", 
                "path": "/relations/-", 
                "value": {
                    "rel": "AttachedFile",
                    "url": attachment_url,
                    "attributes": {"comment": comment}
                }
            }
        ]
        
        link_response = requests.patch(link_url, json=operations, auth=self._auth, headers={"Content-Type": "application/json-patch+json"})
        link_response.raise_for_status()
        return link_response.json()

    def update_test_result(self, test_run_id: int, test_case_id: int, outcome: str, comment: str) -> Dict[str, Any]:
        """Updates the status of a specific test run point."""
        url = f"{self._base_url}/test/runs/{test_run_id}/results?api-version=7.1"
        
        payload = [{
            "testCase": {"id": str(test_case_id)},
            "outcome": outcome, # 'Passed', 'Failed', 'Blocked'
            "comment": comment,
            "state": "Completed"
        }]
        
        response = requests.post(url, json=payload, auth=self._auth)
        response.raise_for_status()
        return response.json()

import os
ado_client = AzureDevOpsClient()
