from typing import List, Dict, Any, Optional
from qa_agent.agents.browser.schemas import LearnedWorkflow, BrowserAction
from qa_agent.memory.knowledge_store import brain

class SkillsLibrary:
    """
    Enterprise Reusable Action Store (Group 4).
    Enables 'Login as admin' or 'Reset Password' as a single reusable building block.
    """
    def __init__(self):
        self.library: Dict[str, LearnedWorkflow] = {}
        self._load_core_skills()

    def _load_core_skills(self):
        """Pre-seeds the knowledge base with common QA workflows."""
        # For now, we load them from the existing brain directory
        workflows = brain.load_all_workflows()
        for w in workflows:
            # Categorize as 'common' if they match high-value intents
            if any(term in w.intent_match.lower() for term in ["login", "search", "checkout", "signup"]):
                self.library[w.intent_match] = w

    def save_skill(self, workflow: LearnedWorkflow):
        """Saves a successfully recorded workflow as a reusable skill."""
        brain.save_workflow(workflow)
        self.library[workflow.intent_match] = workflow

    def find_skill(self, intent: str) -> Optional[LearnedWorkflow]:
        """
        Uses semantic similarity to find the most relevant common skill 
        (e.g., if intent is 'Sign into Bupa', it finds 'Login to site').
        """
        # For Phase 1, we use basic keyword matching
        for key, workflow in self.library.items():
            if intent.lower() in key.lower() or key.lower() in intent.lower():
                return workflow
        return None

    def list_skills(self) -> List[str]:
        return list(self.library.keys())

skills_library = SkillsLibrary()
