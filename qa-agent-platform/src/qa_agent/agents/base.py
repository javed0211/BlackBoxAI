from abc import ABC, abstractmethod
from typing import Any, List
from qa_agent.graph.state import GraphState

class BaseAgent(ABC):
    """
    The Base Class that all specialized agents must inherit from.
    Enforces the Graph-driven, State-driven patterns required by the architecture.
    """
    
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, state: GraphState) -> GraphState:
        """
        Execute the agent's core capability. 
        Must accept a GraphState and return the updated GraphState.
        """
        pass
        
    def get_tools(self) -> List[Any]:
        """
        Return a list of Typed Tools available to this agent for the TOOL EXECUTION LAYER.
        """
        return []
