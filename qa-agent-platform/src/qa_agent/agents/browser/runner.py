import time
import re
import json
from typing import Optional
from qa_agent.agents.browser.schemas import LearnedWorkflow, BrowserAction
from qa_agent.tools.registry import global_registry
from qa_agent.memory.knowledge_store import brain
from qa_agent.models.provider import get_llm
from qa_agent.config.settings import Settings
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers.json import SimpleJsonOutputParser

class WorkflowRunner:
    """
    Executes a previously learned workflow instantly in native Python.
    If a layout change breaks a step, it triggers an LLM Self-Healing routine.
    """
    
    def run_workflow(self, workflow: LearnedWorkflow) -> bool:
        print(f"▶️ [WorkflowRunner] Executing learned workflow: {workflow.intent_match}")
        
        try:
            # Start at the top of the workflow automatically
            global_registry.execute("open_url", url=workflow.start_url)
            time.sleep(1)
            
            repaired_workflow_mutated = False
            for idx, action in enumerate(workflow.actions):
                print(f"  Step {action.step_number}: {action.description} ...")
                
                # Parse "strategy='role'"
                strategy = "css"
                value = action.target_locator or ""
                match = re.search(r"(\w+)='([^']+)'", value)
                
                s_dict = {}
                if match:
                    s_dict["strategy"] = match.group(1)
                    s_dict["value"] = match.group(2)
                
                try:
                    # Execute natively bypassing LLM tokens
                    self._execute_native_action(action, s_dict)
                    time.sleep(0.5)
                except Exception as e:
                    print(f"⚠️ [Self-Healing] Step {action.step_number} FAILED! Element missing/changed: {e}")
                    print("🏥 [Self-Healing] Invoking BrowserAgent LLM to analyze DOM and heal workflow...")
                    
                    healed_action = self._heal_step(action, s_dict)
                    
                    if healed_action:
                        # Success! Overwrite the broken action inside the workflow object
                        workflow.actions[idx] = healed_action
                        repaired_workflow_mutated = True
                    else:
                        print("❌ [Self-Healing] Agent failed to heal the step. Aborting sequence.")
                        return False
                        
            if repaired_workflow_mutated:
                print("💾 [Self-Healing] Updating Artificial Memory with newly healed UI selectors...")
                brain.save_workflow(workflow)
                
                # Overwrite the artifacts on disk using the global registry's filesystem tools
                timestamp = int(time.time())
                global_registry.execute("write_file", path=f"data/artifacts/healed_test_{timestamp}.yml", content=workflow.to_yaml())
                global_registry.execute("write_file", path=f"data/artifacts/healed_test_{timestamp}.spec.ts", content=workflow.to_playwright_ts())
                
            print(f"✅ [WorkflowRunner] Finished complete execution of workflow: {workflow.intent_match}")
            return True
            
        except Exception as e:
            print(f"❌ [WorkflowRunner] Fatal error executing workflow: {e}")
            return False

    def _execute_native_action(self, action: BrowserAction, s_dict: dict):
        """Passes arguments natively into the secure global registry Tool pipeline."""
        t = action.action_type.lower()
        if t == "clickelement" or t == "click":
            global_registry.execute("click_element", **s_dict)
        elif t == "typetext" or t == "type":
            global_registry.execute("type_text", text=action.input_value, **s_dict)
        elif t == "upload":
            global_registry.execute("upload_file", file_path=action.input_value, **s_dict)
        elif t == "assertstate" or t == "verify":

            global_registry.execute("assert_state", state="visible", expected_text=None, **s_dict)

    def _heal_step(self, broken_action: BrowserAction, criteria: dict) -> Optional[BrowserAction]:
        """
        The Core Healing Logic.
        Spins up a targeted, single-shot LLM instance to find the NEW locator on the live screen.
        """
        dom_summary = global_registry.execute("get_dom_summary")
        llm = get_llm()
        
        prompt = ChatPromptTemplate.from_template(
            "You are a Self-Healing QA Agent.\n"
            "An automated Playwright test script just crashed due to a Semantic Layout change.\n\n"
            "BROKEN ACTION INFO:\n"
            "Goal: {description}\n"
            "Old Target Strategy: {loc}\n\n"
            "{dom}\n\n"
            "Your job is to read the DOM summary above and find the NEW valid semantic parameters (strategy + value) that map to the intended goal.\n"
            "Respond ONLY with a raw JSON dictionary exactly structured like this: {{\"strategy\": \"role\", \"value\": \"button\"}}"
        )
        
        try:
            # Enforce structured mapping
            chain = prompt | llm | SimpleJsonOutputParser()
            result = chain.invoke({
                "description": broken_action.description,
                "loc": broken_action.target_locator,
                "dom": dom_summary
            })
            
            new_strat = result.get("strategy")
            new_val = result.get("value")
            
            if not new_strat or not new_val:
                raise ValueError("LLM returned incomplete JSON.")
                
            print(f"💡 [Self-Healing] LLM discovered new valid locator -> strategy='{new_strat}', value='{new_val}'")
            
            # Re-attempt the physical execution with the explicitly healed parameters
            s_dict = {"strategy": new_strat, "value": new_val}
            self._execute_native_action(broken_action, s_dict)
            
            # Mutate the broken action cleanly
            broken_action.target_locator = f"{new_strat}='{new_val}'"
            broken_action.description += " (Healed autonomously)"
            
            return broken_action
            
        except Exception as e:
            print(f"💥 [Self-Healing] Agent encountered error parsing new locator JSON: {e}")
            return None

workflow_runner = WorkflowRunner()
