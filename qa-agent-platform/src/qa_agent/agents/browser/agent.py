from typing import Any, List
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from qa_agent.graph.state import GraphState
from qa_agent.agents.base import BaseAgent
from qa_agent.tools.registry import global_registry
from qa_agent.models.provider import get_llm
from qa_agent.config.settings import Settings
from qa_agent.artifacts.reports import ReportGenerator
from qa_agent.agents.browser.repair import failure_analyst
import time



# --- Langchain Wrapped Tools hooking into our Secure Registry ---
@tool
def _open_url(url: str) -> str:
    """Navigates the internal browser to a specific URL."""
    return global_registry.execute("open_url", url=url)

@tool
def _get_dom_summary() -> str:
    """Reads the semantic interactive layout of the current webpage. Absolutely required before clicking."""
    return global_registry.execute("get_dom_summary")

@tool
def _click_element(strategy: str, value: str, name: str = None, exact: bool = False, index: int = 0) -> str:
    """Instructs Playwright to click an element using Semantic mapping."""
    return global_registry.execute("click_element", strategy=strategy, value=value, name=name, exact=exact, index=index)

@tool
def _type_text(text: str, strategy: str, value: str, name: str = None, exact: bool = False, index: int = 0) -> str:
    """Instructs Playwright to securely fill an input target."""
    return global_registry.execute("type_text", text=text, strategy=strategy, value=value, name=name, exact=exact, index=index)

@tool
def _assert_state(state: str, strategy: str, value: str, expected_text: str = None, name: str = None, exact: bool = False, index: int = 0) -> str:
    """Verifies that an element state ('visible', 'hidden', 'text_matches') is valid."""
    return global_registry.execute("assert_state", state=state, expected_text=expected_text, strategy=strategy, value=value, name=name, exact=exact, index=index)

@tool
def _press_key(key: str) -> str:
    """Presses a physical keyboard key (e.g. 'Enter', 'Escape', 'Tab'). Useful for submitting forms after typing."""
    return global_registry.execute("press_key", key=key)

@tool
def _upload_file(file_path: str, strategy: str, value: str, name: str = None, exact: bool = False, index: int = 0) -> str:
    """
    Uploads a file by setting it into a target file-input element.
    Ensure you have a valid path for the file you intend to upload (e.g., 'data/artifacts/some_file.pdf').
    """
    return global_registry.execute("upload_file", file_path=file_path, strategy=strategy, value=value, name=name, exact=exact, index=index)

@tool
def _accessibility_audit() -> str:
    """Performs a lightweight ARIA and semantic audit of the current page. Returns a list of violations."""
    return global_registry.execute("accessibility_audit")

@tool
def _visual_verify(baseline_name: str) -> str:
    """Compares current screen to a baseline image. Use for UI regression checks."""
    return global_registry.execute("visual_compare", baseline_path=f"data/baselines/{baseline_name}.png")



@tool
def _terminate_workflow(success: bool, final_summary: str, failure_analysis: str = None) -> str:
    """
    Call this tool when you have fully completed the task or definitively failed. 
    If success=False, you MUST provide a detailed failure_analysis explaining exactly why the UI blocked the goal.
    """
    return f"TERMINATING. Success: {success}.\nSummary: {final_summary}\nFailure Analysis: {failure_analysis}"

BROWSER_SYSTEM_PROMPT = """You are the Browser Agent inside a QA-First AI Platform.
Your mission is to navigate the web automatically, understand semantic DOMs, and execute precise Playwright actions to solve the user's QA request.

CRITICAL INSTRUCTIONS:
1. NEVER guess or hallucinate extraction data. You must extract EXACT strings from the DOM. If a price is £2,489, do not hallucinate £3,099.
2. ALWAYS use the `_get_dom_summary` tool the second a page loads. You cannot guess semantic mapping. You must read it.
3. The summary array will explicitly hand you `(strategy='role', value='button')` arrays. Copy them EXPLICITLY into the execution tools. DO NOT use Xpaths or loose queries.
4. If you have already read the DOM recently and nothing has changed on the page, DO NOT call `_get_dom_summary` endlessly. Proceed with executing your physical tools immediately to save tokens.
5. `_type_text` does NOT press Enter automatically. You must use `_press_key("Enter")` or click a Search button.
6. ALWAYS use `_assert_state` to verify your action worked. CRITICAL: To assert text exists on the page, NEVER use `strategy='role'` with `state='text_matches'` because `.nth(0)` will check the wrong heading. ALWAYS use `_assert_state(state='visible', strategy='text', value='Expected Text')` to natively verify text visibility.
7. CRITICAL: If your `_assert_state` returns **Assertion FAILED**, you MUST either fix the locator and try again, OR call `_terminate_workflow` with `success=False`. You are NOT permitted to say the mission was successful if the assertion fails!
8. When the goal is completed, end the sequence by calling the `_terminate_workflow` tool!
"""

@tool
def _scroll(direction: str = "down", pixels: int = 800) -> str:
    """Scrolls the page down or up to load more elements into the truncated DOM summary."""
    return global_registry.execute("scroll", direction=direction, pixels=pixels)

class BrowserAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Browser Agent")

    def get_tools(self) -> List[Any]:
        """Provides Langchain Tool Wrappers perfectly bound to the pre-hooked Custom Registry!"""
        return [_open_url, _get_dom_summary, _click_element, _type_text, _assert_state, _press_key, _scroll, _upload_file, _accessibility_audit, _visual_verify, _terminate_workflow]



    def run(self, state: GraphState) -> GraphState:
        print("🌐 [BrowserAgent] Analyzing mission request...")
        
        # --- LONG-TERM MEMORY RETRIEVAL (ZERO COST RUN) ---
        from qa_agent.memory.knowledge_store import brain
        from qa_agent.agents.browser.runner import workflow_runner
        
        known_workflow = brain.find_workflow(state.mission.user_input)
        if known_workflow:
            print(f"🧠 [BrowserAgent Memory Bank] Exact match found! I previously learned how to do '{known_workflow.intent_match}'.")
            print(f"⏭️ Skipping Azure LLM loop to execute natively from YAML memory...")
            
            # Execute the remembered script natively using Python Playwright Tools (Includes Self-Healing)
            success = workflow_runner.run_workflow(known_workflow)
            
            if success:
                state.validation_passed = True
                state.errors = []
                return state
            else:
                print("⚠️ [BrowserAgent] Stored memory execution completely failed despite healing attempts. Falling back to fresh LLM iteration...")
                
        # --- FULL AZURE LLM RE-ACT LOOP (IF NO MEMORY EXISTS) ---
        print("💡 [BrowserAgent] No memory found. Awaking Playwright QA Intelligence Loop...")
        start_time = time.time()
        
        from qa_agent.integrations.browser_runtime import runtime
        runtime.reset_logs()
        
        llm = get_llm()


        tools = self.get_tools()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", BROWSER_SYSTEM_PROMPT),
            ("user", "Mission Request: {input}\n\nProceed safely and autonomously."),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        agent = create_tool_calling_agent(llm, tools, prompt)
        
        # return_intermediate_steps is CRITICAL for our Continuous Learning Memory Pipeline!
        agent_executor = AgentExecutor(
            agent=agent, 
            tools=tools, 
            verbose=True, 
            max_iterations=15, 
            return_intermediate_steps=True
        )
        
        from langchain_community.callbacks.manager import get_openai_callback
        try:
            # Wrap execution completely in the OpenAI Tracker context
            with get_openai_callback() as cb:
                result = agent_executor.invoke({"input": state.mission.user_input})
                
            # Telemetry readout 
            print("\n📊 --- API Telemetry & Token Economy ---")
            print(f"🪙 Tokens Consumed: {cb.total_tokens:,} (Prompt: {cb.prompt_tokens:,} | Completion: {cb.completion_tokens:,})")
            print(f"⏱️ Azure LLM API Calls: {cb.successful_requests}")
            print(f"💰 Total API Cost: ${cb.total_cost:.5f}")
            print("-----------------------------------------")
            
            output = result.get('output', '')
            
            # Did the AI fail the test? Print its Failure Analysis!
            if "Success: False" in output or "Success: false" in output:
                print(f"❌ [AI Test Reporter] Test Failed with Failure Analysis:\n\n{output}\n")
                state.validation_passed = False
                state.errors.append(f"Browser Execution Failed: {output}")
                return state
                
            state.validation_passed = True
            
            # --- CONTINUOUS LEARNING & ARTIFACT GENERATION ---
            print("💽 [BrowserAgent] Analyzing successful tool execution path to generate artifacts...")
            from qa_agent.agents.browser.schemas import BrowserAction, LearnedWorkflow
            from qa_agent.memory.knowledge_store import brain
            timestamp = int(time.time())

            
            actions = []
            steps = result.get("intermediate_steps", [])
            for i, (action_obj, observation) in enumerate(steps):
                # Ignore observation tracking tools in the test scripts
                if action_obj.tool in ["_get_dom_summary", "_terminate_workflow"]:
                    continue
                    
                target = action_obj.tool_input.get("value", "")
                if action_obj.tool_input.get("strategy"):
                    target = f"{action_obj.tool_input.get('strategy')}='{target}'"
                    
                # Strictly map Langchain Tool Names back to valid Pydantic Literals
                t_name = action_obj.tool.lower()
                act_type = "wait" # Fallback
                if "open" in t_name or "navigate" in t_name: act_type = "navigate"
                elif "click" in t_name: act_type = "click"
                elif "type" in t_name: act_type = "type"
                elif "upload" in t_name: act_type = "upload"
                elif "select" in t_name: act_type = "select"
                elif "audit" in t_name: act_type = "audit"
                elif "visual" in t_name: act_type = "visual"
                elif "assert" in t_name: act_type = "verify"

                
                actions.append(BrowserAction(
                    step_number=len(actions) + 1,
                    action_type=act_type,
                    target_locator=target,
                    input_value=action_obj.tool_input.get("text") or action_obj.tool_input.get("url") or "",
                    description=f"Autonomously executed {action_obj.tool}"
                ))

            if actions:
                workflow = LearnedWorkflow(
                    intent_match=state.mission.user_input,
                    start_url=actions[0].input_value if actions[0].action_type == "navigate" else "Unknown",
                    actions=actions
                )
                
                # 1. Save to Long-Term Brain Mapping
                brain.save_workflow(workflow)
                
                # --- 2. LLM SCRIPT GENERATION (Replacing Regex) ---
                print("🧠 [BrowserAgent] Asking LLM to translate workflow into elegant Playwright TypeScript...")
                script_prompt = ChatPromptTemplate.from_template(
                    "You are an Expert QA Automation Engineer.\n"
                    "Translate the following successful JSON browser interaction log into a robust Playwright TypeScript test script.\n\n"
                    "JSON LOG:\n{json_log}\n\n"
                    "CRITICAL RULES:\n"
                    "- Output strictly the raw TypeScript code. Do NOT wrap in ```typescript markdown blocks.\n"
                    "- Use native Playwright locators brilliantly (e.g. `page.getByRole('button', {{ name: 'Submit' }})` or `page.getByLabel('Search')`).\n"
                    "- If a component might be duplicate, do NOT use `.first()`. Instruct Playwright to filter properly via `.filter({{ hasText: '...' }})` or `.nth(X)` based on the context.\n"
                    "- Incorporate `expect().toBeVisible()` seamlessly for assertions.\n"
                )
                ts_chain = script_prompt | llm
                ts_content = ts_chain.invoke({"json_log": workflow.model_dump_json(indent=2)}).content
                
                # Clean up markdown output if the LLM ignores the prompt
                ts_content = ts_content.replace("```typescript", "").replace("```ts", "").replace("```", "").strip()
            else:
                workflow = None
                ts_content = ""

            # --- 3. DYNAMIC HTML EXECUTION REPORT ---

            screenshot_path = f"data/artifacts/screenshot_{timestamp}.png"
            global_registry.execute("take_screenshot", path=screenshot_path)
            
            # Fetch video path if available
            video_path = None
            try:
                from qa_agent.integrations.browser_runtime import runtime
                page = runtime.get_page()
                if page and page.video:
                    video_path = page.video.path()
            except:
                pass

            analytics = {
                "total_tokens": cb.total_tokens,
                "total_cost": cb.total_cost,
                "duration": round(time.time() - start_time, 2)
            }

            # Map BrowserAction list to dicts for ReportGenerator
            report_actions = [a.model_dump() for a in actions]

            failure_analysis = None
            if "Success: False" in output or "Success: false" in output:
                # 1. Start with the agent's own surface analysis
                initial_analysis = output.split("Failure Analysis:")[1].strip() if "Failure Analysis:" in output else output
                
                # 2. PERFORM DEEP ROOT-CAUSE REASONING (GROUP 6F)
                raw_dom = global_registry.execute("get_dom_summary")
                deep_reasoning = failure_analyst.analyze_failure(
                    mission=state.mission.user_input,
                    error=initial_analysis,
                    console_logs=runtime.console_logs,
                    network_logs=runtime.failed_requests,
                    dom_context=raw_dom
                )
                
                # Format deep analysis into a human-readable bundle
                diagnosis = f"Technical Diagnosis: {deep_reasoning.get('technical_diagnosis', 'No diagnosis found.')}\n\n"
                diagnosis += f"Reproduction Steps: {deep_reasoning.get('repro_steps', 'Not provided.')}\n\n"
                diagnosis += f"Suggested Fix: {deep_reasoning.get('suggested_fix', 'Not provided.')}"
                
                failure_analysis = diagnosis
            else:
                failure_analysis = None


            html_report = ReportGenerator.generate_html(
                mission_input=state.mission.user_input,
                success=True if not failure_analysis and workflow else False,
                actions=report_actions,
                analytics=analytics,
                start_url=workflow.start_url if workflow else "N/A",
                failure_analysis=failure_analysis,
                screenshots=[screenshot_path],
                video_path=video_path,
                console_logs=runtime.console_logs,
                network_logs=runtime.failed_requests
            )



            # 4. Burn artifacts to disk locally
            if workflow:
                global_registry.execute("write_file", path=f"data/artifacts/test_{timestamp}.yml", content=workflow.to_yaml())
                global_registry.execute("write_file", path=f"data/artifacts/test_{timestamp}.spec.ts", content=ts_content)
            
            global_registry.execute("write_file", path=f"data/artifacts/report_{timestamp}.html", content=html_report)
            print(f"✅ [BrowserAgent] Successfully compiled artifacts and HTML Report into artifacts/ !")

            state.errors = []

            
        except Exception as e:
            state.validation_passed = False
            state.errors.append(f"BrowserAgent Fatal Error: {str(e)}")
            
        return state

# Expose global instance for execute.py
browser_agent = BrowserAgent()
