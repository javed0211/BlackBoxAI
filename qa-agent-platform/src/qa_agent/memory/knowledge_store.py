import os
import json
from pathlib import Path
from typing import List, Optional
from qa_agent.agents.browser.schemas import LearnedWorkflow

class KnowledgeStore:
    """
    Continuous Learning Memory Bank.
    Permanently persists and retrieves highly optimized LearnedWorkflows 
    to stop the LLM from Hallucinating previously solved UI navigations.
    """
    def __init__(self, db_dir: str = "data/knowledge"):
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.workflows_file = self.db_dir / "workflows.json"
        
        # Initialize flat file JSON database if not exists
        if not self.workflows_file.exists():
            with open(self.workflows_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def save_workflow(self, workflow: LearnedWorkflow) -> bool:
        """Appends a new successful script to the brain's memory bank."""
        try:
            with open(self.workflows_file, "r", encoding="utf-8") as f:
                memory = json.load(f)
                
            memory.append(workflow.model_dump())
            
            with open(self.workflows_file, "w", encoding="utf-8") as f:
                json.dump(memory, f, indent=2)
                
            return True
        except Exception as e:
            print(f"[KnowledgeStore] Error retaining memory: {e}")
            return False

    def find_workflow(self, intent_query: str) -> Optional[LearnedWorkflow]:
        """
        Retrieves a workflow by performing a fuzzy local search against the intent string.
        (A sophisticated system would use Vector Embeddings here, but strict sub-string 
        matching is highly robust for Phase 1.)
        """
        try:
            with open(self.workflows_file, "r", encoding="utf-8") as f:
                memory = json.load(f)
                
            results = []
            query = intent_query.lower()
            
            for script in memory:
                # Basic sub-string match on the intent
                if query in script.get("intent_match", "").lower():
                    results.append(LearnedWorkflow.model_validate(script))
                    
            if results:
                # Return the most applicable historical workflow
                return results[0]
            return None
        except Exception as e:
            print(f"[KnowledgeStore] Error accessing memory: {e}")
            return None

# Global instance exposed to LangGraph Agents
brain = KnowledgeStore()
