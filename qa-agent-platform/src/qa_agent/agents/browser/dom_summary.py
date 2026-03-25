from typing import List, Dict, Any
from qa_agent.tools.registry import global_registry
from qa_agent.models.provider import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

class SemanticDOMAnalyzer:
    """
    Advanced AI-Native DOM Intelligence (Group 6A).
    Transforms raw Interactive DOM summaries into high-level business components.
    """
    def __init__(self):
        self.llm = get_llm()

    def analyze_page(self) -> Dict[str, Any]:
        """
        Reads the DOM and extracts high-level Business Semantics.
        'Login Form', 'Product Search Grid', 'Pagination Controls', etc.
        """
        raw_summary = global_registry.execute("get_dom_summary")
        
        prompt = ChatPromptTemplate.from_template(
            "You are a DOM Intelligence Agent.\n"
            "Analyze the following raw interactive element summary and group elements into logical Business Components.\n\n"
            "RAW DOM:\n{dom}\n\n"
            "Your output must be a valid JSON dictionary mapping a 'Component Name' to its constituent 'Element Indices' and 'Business Purpose'.\n"
            "Example: {{'AuthForm': {{'indices': [2, 3, 4], 'purpose': 'Login and password entry'}}}}"
        )
        
        try:
            chain = prompt | self.llm | JsonOutputParser()
            analysis = chain.invoke({"dom": raw_summary})
            return {
                "raw": raw_summary,
                "components": analysis
            }
        except Exception as e:
            return {"raw": raw_summary, "error": str(e)}

dom_analyzer = SemanticDOMAnalyzer()
