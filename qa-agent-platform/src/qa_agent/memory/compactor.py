from typing import Dict, Any, List
from qa_agent.graph.state import GraphState
from qa_agent.models.provider import get_llm
from qa_agent.config.settings import Settings
from langchain_core.prompts import PromptTemplate

class MemoryCompactor:
    """
    Optimizes context limits dynamically by taking sprawling and expensive tool_call 
    history arrays (like massive Playwright outputs) and aggressively squashing them 
    into a high-density, low-token string using an LLM. 
    
    Prevents Context Window Exhaustion (OOM) during long QA agent test suites.
    """
    def __init__(self, action_threshold: int = 5):
        # Number of tool calls allowed in state before compaction triggers
        self.action_threshold = action_threshold
        self.llm = get_llm()
        self.prompt = PromptTemplate.from_template(
            "You are a Memory Optimizer Agent. Your job is Context Compaction.\n"
            "Synthesize the following raw tool execution logs into a highly dense, bulleted summary of EXACTLY WHAT was found and WHAT was done.\n"
            "Drop trivial noise, error spam, and timestamps. Keep critical facts, discovered bugs, and state changes.\n\n"
            "Current Active Memory:\n{current}\n\n"
            "Raw Tool Logs to Compact:\n{logs}\n\n"
            "Output only the optimized memory summary."
        )

    def should_compact(self, state: GraphState) -> bool:
        """Determines if the state has grown bloated enough to require compression."""
        return len(state.tool_calls) >= self.action_threshold

    def compact(self, state: GraphState) -> GraphState:
        """Performs aggressive memory compression if required."""
        if not self.should_compact(state):
            return state

        print(f"📦 [Memory Optimization] Compacting {len(state.tool_calls)} raw tool outputs to save tokens...")
        
        # Serialize only the expensive raw tool logs dumping into the graph
        raw_logs = "\n".join([str(t) for t in state.tool_calls])
        current_memory = state.compacted_history or "Clean memory. No previous compactions."
        
        # Squeeze everything through the Azure Provider LLM
        compressed_summary = self.llm.invoke(
            self.prompt.format(current=current_memory, logs=raw_logs)
        ).content
        
        # Overwrite the state gracefully
        state.compacted_history = compressed_summary
        
        # Danger zone: clear out the giant memory arrays to free the context window!
        state.tool_calls = []  
        
        print("✅ [Memory Optimization] Compaction successful. History condensed and tokens freed!")
        return state

# Global instance
compactor = MemoryCompactor()
