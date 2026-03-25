from typing import List, Dict, Any, Optional
from qa_agent.models.provider import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

class WorkItemToTestMapper:
    """
    Test Authoring Intelligence (Group 4).
    Maps unstructured Jira/ADO manual steps into a structured BrowserAction plan.
    """
    def __init__(self):
        self.llm = get_llm()

    def convert_to_actions(self, title: str, description: str) -> List[Dict[str, Any]]:
        """
        Translates 'Manual Repo Steps' into JSON-serializable Playwright instructions.
        """
        prompt = ChatPromptTemplate.from_template(
            "You are a Senior Test Automation Architect.\n"
            "Translate the following manual test case into a structured sequence of Browser Actions.\n\n"
            "TITLE: {title}\n"
            "STEPS/DESCRIPTION:\n{description}\n\n"
            "Output ONLY a raw JSON list of dictionaries exactly like this:\n"
            "[{{\"step_number\": 1, \"action_type\": \"navigate|click|type|select|verify\", \"target_locator\": \"description of what to find\", \"input_value\": \"data or URL\", \"description\": \"human readable explanation\"}}]"
        )
        
        try:
            chain = prompt | self.llm | JsonOutputParser()
            actions = chain.invoke({"title": title, "description": description})
            return actions
        except Exception as e:
            print(f"[WorkItemMapper] Warning: AI failed to parse manual steps: {e}")
            return []

test_mapper = WorkItemToTestMapper()
