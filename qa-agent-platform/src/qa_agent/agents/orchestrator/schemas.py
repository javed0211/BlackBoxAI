from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class OrchestratorDecision(BaseModel):
    intent: Literal[
        "code_fix", 
        "browser_validation", 
        "qa_analysis", 
        "work_item_create", 
        "multi_step_repro_and_fix", 
        "test_generation", 
        "bug_triage", 
        "release_readiness"
    ] = Field(description="The primary intent of the user's mission.")
    
    plan_summary: str = Field(description="A 1-2 sentence high-level summary of the execution plan.")
    
    selected_agents: List[Literal["QA Agent", "Browser Agent", "Coding Agent", "ADO/Jira Agent"]] = Field(
        description="The agents required to fulfill the mission. Choose only from the available agents."
    )
    
    execution_mode: Literal["single", "sequential", "parallel"] = Field(
        description="How the agents should be executed. Single if 1 agent, sequential or parallel if multiple."
    )
    
    confidence_score: float = Field(description="Confidence from 0.0 to 1.0 in this classification.")
