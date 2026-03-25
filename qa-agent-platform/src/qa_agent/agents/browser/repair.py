from typing import Dict, Any, List
from qa_agent.models.provider import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

class FailureAnalyst:

    """
    Advanced Root-Cause Reasoning (Group 3, 6F).
    Analyzes telemetry patterns (Console/Network/DOM) to provide human-readable defect summaries.
    """
    def __init__(self):
        self.llm = get_llm()

    def analyze_failure(
        self, 
        mission: str, 
        error: str, 
        console_logs: List[Dict[str, Any]] = [], 
        network_logs: List[Dict[str, Any]] = [],
        dom_context: str = ""
    ) -> Dict[str, Any]:
        """
        Synthesizes multiple evidence streams into a single Root Cause and Suggested Fix.
        """
        prompt = ChatPromptTemplate.from_template(
            "You are a Senior QA Failure Analyst.\n"
            "An automated mission just failed. Analyze all evidence streams below to deduce the root cause.\n\n"
            "MISSION: {mission}\n"
            "PRIMARY ERROR: {error}\n\n"
            "EVIDENCE (JS CONSOLE):\n{console}\n\n"
            "EVIDENCE (NETWORK LOGS):\n{network}\n\n"
            "EVIDENCE (DOM FRAGMENT):\n{dom}\n\n"
            "Output a structured JSON response exactly like this:\n"
            "{{\n"
            "  'root_cause_type': 'UI Bug | Backend Error | Auth Failure | Flaky Locator',\n"
            "  'technical_diagnosis': 'Brief technical explanation',\n"
            "  'impact': 'Low|Medium|High',\n"
            "  'repro_steps': '1. ... 2. ...',\n"
            "  'suggested_fix': 'Recommendation for the developer'\n"
            "}}"
        )
        
        try:
            chain = prompt | self.llm | JsonOutputParser()
            analysis = chain.invoke({
                "mission": mission,
                "error": error,
                "console": str(console_logs),
                "network": str(network_logs),
                "dom": dom_context[:1000] # Token economy: truncate DOM
            })
            return analysis
        except Exception as e:
            return {"error": str(e), "technical_diagnosis": "AI Analyst failed to parse evidence."}

failure_analyst = FailureAnalyst()
