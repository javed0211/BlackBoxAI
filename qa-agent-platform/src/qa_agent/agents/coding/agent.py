from qa_agent.graph.state import GraphState
from qa_agent.agents.base import BaseAgent

class CodingAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Coding Agent")

    def run(self, state: GraphState) -> GraphState:
        print("[Coding Agent] Understanding failing paths and proposing code changes...")
        return state
