# 🌍 Browser Agent: High-Level Engineering Guide

The **Browser Agent** is an autonomous, agentic engine designed for high-precision UI interaction. It combines the deterministic execution of Playwright with the reasoning capabilities of Large Language Models (LLMs). This guide provides deep-dive technical steps for developers looking to integrate, extend, and debug the browser agent.

---

## 🏛️ Technical Architecture

The Browser Agent operates within a **LangGraph** state machine. At its core, it is a `ReAct` (Reason-Action) agent that interacts with a secure **Cross-Agent Tool Registry**.

### Key Components:
- **`GraphState`**: The source of truth for the mission context, including user input, validation flags, and error logs.
- **`global_registry`**: A secure abstraction layer that wraps Playwright methods, allowing for pre-execution hooks (e.g., security filtering) and post-execution observation recording.
- **`KnowledgeStore`**: A JSON/Vector-based memory bank that stores `LearnedWorkflows` to minimize LLM inference costs during regression runs.

---

## 🛠️ Step-by-Step CLI Execution (Developer Workflow)

### 1. Environment Setup & Initialization
Ensure you have the development environment correctly linked and the system dependencies (Playwright) installed.

```bash
# Clone and install in editable mode
pip install -e .
# Install Playwright browser binaries
playwright install chromium
```

### 2. High-Precision Direct Mission Execution
Use the `browser test` command for targeted UI interaction. This bypasses the global orchestrator and focuses entirely on the browser's reasoning loop.

```bash
qa-agent browser test "Navigate to https://demo.portal.com, perform a 'Role-based' search for 'Admin', and verify the results count"
```

**Developer Insight**: Behind the scenes, this command:
1. Instantiates a `MissionContext` with a unique UUID.
2. Initializes the `BrowserAgent` class.
3. Triggers the `run()` method, which first checks the **KnowledgeStore** for historical intent matches.

### 3. Analyzing the "Zero-Cost" Execution (The Learning Loop)
If an identical mission has succeeded previously, the agent enters **Memory Native Mode**:
- It retrieves the `LearnedWorkflow` JSON.
- It executes steps via `workflow_runner.run_workflow()` without calling the LLM API.
- **Self-Healing Trigger**: If an element locator fails (e.g., a CSS class changed), the native runner raises a `HealRequest` exception. This kicks the agent back into LLM mode, where it re-analyzes the DOM, repairs the path, and updates its memory.

---

## 🏗️ Extending the Agent: Adding Custom Tools

As a developer, you may need the agent to perform actions like "Capture Performance Trace" or "Inject Custom JS".

1. **Register the Core Action**: Add your Playwright logic to `src/qa_agent/tools/playwright.py`.
2. **Hook into Global Registry**: Expose it in `src/qa_agent/tools/registry.py`.
3. **Expose LangChain Wrapper**: Define a `@tool` in `src/qa_agent/agents/browser/agent.py`.
4. **Update System Prompt**: Inform the agent of the new capability in `BROWSER_SYSTEM_PROMPT`.

```python
# Example: Adding a performance capture tool
@tool
def _capture_performance(trace_name: str) -> str:
    """Captures a browser performance trace and saves it to data/traces/."""
    return global_registry.execute("performance_trace", name=trace_name)
```

---

## 📊 Debugging & Post-Execution Analysis

The agent generates high-fidelity debug artifacts after every run.

### 1. The Interactive HTML Report
Located in `data/artifacts/report_TIMESTAMP.html`. It contains:
- **Execution Timeline**: Step-by-step mapping of NL intent to physical locators.
- **Network Telemetry**: A JSON log of failed XHR/Fetch requests that occurred during navigation.
- **Visual Evidence**: Screenshots capturing the exact state before and after critical interactions.

### 2. The Auto-Generated Playwright Test
The agent translates its successful reasoning path into a **Typescript Playwright Test** (`.spec.ts`).
- **Use Case**: Export these scripts directly into your existing CI/CD pipelines to replace fragile manual recording tools.

### 3. Token Economy Monitoring
Detailed telemetry is printed to the console (tokens used, total cost, and LLM latency). Use this to optimize your prompts and tool usage.

---

## 🧪 Advanced Unit Testing for Developers

To verify changes to the agent's reasoning or memory logic, use the pre-built test suite:

```bash
# Run unit tests with PYTHONPATH mapping
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
pytest tests/unit/test_browser_agent.py -vv
```

**Testing Categories:**
- **Schema Validation**: Ensures Pydantic models correctly translate into YAML/TS.
- **Prompt Integrity**: Guards against "mission drift" in the system prompts.
- **Knowledge Recall**: Validates the persistence layer of the KnowledgeStore.

---

## 🏗️ Internals: The "Schema Bridge"

A unique feature of this agent is its ability to translate fuzzy LLM reasoning into structured Playwright code. 

### Step-to-Action Mapping:
When the agent finishes its `AgentExecutor` loop, it parses the `intermediate_steps` (LangChain `AgentAction` objects) and maps them to the `BrowserAction` Pydantic model:

1.  **Normalization**: It converts tool names like `_open_url`, `_navigate_to`, and `_go_to` into a unified `navigate` `action_type`.
2.  **Locator Extraction**: It extracts semantic strategies (e.g., `role`, `text`, `label`) and values into structured fields.
3.  **Template Generation**: The `LearnedWorkflow.to_playwright_ts()` method then uses a regex-based **Semantic Locator Converter** to generate valid Playwright Typescript syntax (e.g., `page.getByRole('button')`).

### Artifact Generation Workflow:
1.  **JSON Trace**: The raw tool output is serialized to a `LearnedWorkflow` JSON object.
2.  **LLM Refinement**: The agent makes a high-precision, low-token count LLM call to "clean up" the raw tool log into elegant, readable code.
3.  **Local Persistence**: Results are burned into `data/artifacts/` using the `global_registry.execute("write_file")` hook.
