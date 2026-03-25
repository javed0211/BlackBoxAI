from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field

class MissionContext(BaseModel):
    mission_id: str
    user_input: str
    workspace: Optional[str] = None
    repo_path: Optional[str] = None
    dry_run: bool = False
    approval_mode: Literal["strict", "smart", "off"] = "smart"

class AgentTask(BaseModel):
    task_id: str
    agent_name: str
    goal: str
    status: Literal["pending", "running", "success", "failed"] = "pending"
    dependencies: List[str] = Field(default_factory=list)
    outputs: Dict[str, Any] = Field(default_factory=dict)

class ArtifactRef(BaseModel):
    artifact_id: str
    type: str
    path: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GraphState(BaseModel):
    mission: MissionContext
    intent: Optional[str] = None
    plan_summary: Optional[str] = None
    selected_agents: List[str] = Field(default_factory=list)
    execution_mode: Optional[Literal["single", "sequential", "parallel"]] = None
    tasks: List[AgentTask] = Field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    compacted_history: Optional[str] = None
    artifacts: List[ArtifactRef] = Field(default_factory=list)
    validation_passed: bool = False
    retries: int = 0
    final_summary: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
