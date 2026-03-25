import time
from typing import List, Dict, Any, Set
from qa_agent.tools.registry import global_registry
from qa_agent.integrations.browser_runtime import runtime
from qa_agent.models.provider import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

class ExploratoryAgent:
    """
    Advanced AI-Native Exploratory Testing Agent (Group 6C).
    Autonomously navigates and discovers application flows, flagging suspicious behavior.
    """
    def __init__(self, max_depth: int = 3, max_interactions: int = 15):
        self.max_depth = max_depth
        self.max_interactions = max_interactions
        self.visited_urls: Set[str] = set()
        self.interacted_elements: Set[str] = set()
        self.findings: List[Dict[str, Any]] = []
        self.llm = get_llm()

    def explore(self, start_url: str) -> List[Dict[str, Any]]:
        """
        Main entry point for autonomous exploration.
        """
        print(f"🕵️  [ExploratoryAgent] Starting reconnaissance mission on {start_url}...")
        global_registry.execute("open_url", url=start_url)
        runtime.reset_logs() # Clear previous session logs
        
        self.visited_urls.add(start_url)
        interaction_count = 0
        
        while interaction_count < self.max_interactions:
            # 1. Inspect current page
            print(f"  [Depth={len(self.visited_urls)}] Inspecting page: {runtime.get_page().url}")
            dom_summary = global_registry.execute("get_dom_summary")
            
            # 2. Ask AI to pick the next "high-value" exploratory action
            # Avoid repeating the same button click forever
            decision = self._decide_next_move(dom_summary)
            
            if not decision or decision.get("action") == "STOP":
                print("  [ExploratoryAgent] No more high-value interactions discovered.")
                break
                
            # 3. Execute the move
            print(f"  ⚡ [Action {interaction_count+1}] Attempting to {decision['action']} targets: {decision['target']}...")
            self._execute_move(decision)
            interaction_count += 1
            
            # 4. Catch any immediate errors/logs
            if runtime.console_logs or runtime.failed_requests:
                self.findings.append({
                    "step": interaction_count,
                    "url": runtime.get_page().url,
                    "action": decision["action"],
                    "logs": list(runtime.console_logs),
                    "network": list(runtime.failed_requests)
                })
                # Re-reset so we only catch DELTA per step
                runtime.reset_logs()
                
            # Avoid getting stuck in simple redirects
            new_url = runtime.get_page().url
            self.visited_urls.add(new_url)

        return self.findings

    def _decide_next_move(self, dom_summary: str) -> Dict[str, Any]:
        """
        Uses LLM to decide the most 'interesting' next click/type for risk discovery.
        """
        prompt = ChatPromptTemplate.from_template(
            "You are an Advanced Exploratory QA Agent.\n"
            "Your objective is to DISCOVER bugs, non-standard behaviors, and new flows.\n\n"
            "CURRENT INTERACTIVE DOM:\n{dom}\n\n"
            "PREVIOUSLY INTERACTED TARGETS (DO NOT REPEAT):\n{history}\n\n"
            "Choose the most 'high-risk' next interaction (e.g. submit a form, navigate to a complex module, click an edge-case button).\n"
            "Respond ONLY with a raw JSON dictionary: {{\"action\": \"click|type|select\", \"strategy\": \"role|text|...\", \"value\": \"...\", \"data\": \"optional_input\", \"reasoning\": \"brief explanation\"}}\n"
            "If nothing interesting remains, return: {{\"action\": \"STOP\"}}"
        )
        
        try:
            chain = prompt | self.llm | JsonOutputParser()
            result = chain.invoke({
                "dom": dom_summary,
                "history": list(self.interacted_elements)
            })
            
            if result.get("action") != "STOP":
                # Track what we clicked to avoid infinite loops
                target_key = f"{result.get('strategy')}={result.get('value')}"
                self.interacted_elements.add(target_key)
                
            return result
        except:
            return {"action": "STOP"}

    def _execute_move(self, decision: Dict[str, Any]):
        action = decision.get("action", "").lower()
        strategy = decision.get("strategy")
        value = decision.get("value")
        data = decision.get("data", "")
        
        try:
            if action == "click":
                global_registry.execute("click_element", strategy=strategy, value=value)
            elif action == "type":
                global_registry.execute("type_text", text=data or "NexusExploratoryInput", strategy=strategy, value=value)
                global_registry.execute("press_key", key="Enter") # Common exploration pattern
            elif action == "select":
                # Fallback to click if select is not fully parameterized
                global_registry.execute("click_element", strategy=strategy, value=value)
        except Exception as e:
            print(f"  ⚠️ Action failed: {e}")

exploratory_agent_worker = ExploratoryAgent()
