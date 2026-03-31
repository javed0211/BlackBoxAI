# 🌍 Browser Agent CLI & Workflow Guide

The Browser Agent is an autonomous, agentic engine built on Playwright and LangChain. It specializes in navigating complex web applications, performing semantic DOM analysis, and converting successful interactions into permanent automation artifacts.

---

## 🚀 Getting Started

To use the Browser Agent, you can either trigger it via the global `run` command (as part of a multi-agent orchestrated mission) or access it directly for specific browser tasks.

### 🔌 1. General Mission Execution
The most common way to invoke the Browser Agent is by giving the platform a natural language mission. If the orchestrator detects the mission requires web navigation, it will engage the Browser Agent.

```bash
qa-agent run "Navigate to https://example.com, click the 'Get Started' button, and verify the title is 'Introduction'"
```

**Options:**
- `--workspace PATH`: Path to your repository (default: `./repo`).
- `--approval-mode strict|smart|off`: Controls whether the agent asks for permission before destructive actions.
- `--model-profile fast|balanced|deep`: Selects the LLM intelligence level.

---

## 🛠️ Browser Agent Specialized CLI

The `browser` sub-command provides tools specifically for web-based testing.

### `test` command
Runs a browser-only mission. This skips the orchestrator and sends the prompt directly to the Browser agent.

```bash
qa-agent browser test "Go to google.com and search for 'OpenAI' and verify results"
```

---

## 🧠 Continuous Learning & Memory

The Browser Agent features a **Long-Term Memory Bank** (Knowledge Store). 

1. **Iteration 1**: If you ask for a task for the first time (e.g., "Login to Salesforce"), the agent uses the LLM to dynamically explore the UI using Playwright.
2. **Artifact Generation**: Upon success, it automatically generates:
   - A **YAML Workflow** (`test_TIMESTAMP.yml`): A high-level description of the steps.
   - A **Playwright Script** (`test_TIMESTAMP.spec.ts`): Ready-to-use TypeScript code for your CI/CD.
   - An **HTML Report**: A visual walkthrough with screenshots and console logs.
3. **Optimized Execution**: The next time you run the *same mission*, the agent retrieves the successful YAML script from its memory and executes it natively in Python—**saving 100% of LLM token costs**.

---

## 📁 Artifact Locations

All results are saved in the `data/` directory:
- `data/artifacts/`: Contains generated `.ts`, `.yml`, and `.html` reports.
- `data/knowledge/`: Contains the `workflows.json` memory bank.
- `data/baselines/`: Stores images for visual regression testing.

---

## 🧪 Advanced Tips

- **Assertions**: Always include the word "verify" or "assert" in your prompt. The agent will automatically use `_assert_state` to ensure the UI is in the correct state.
- **Self-Healing**: If a script in memory fails (e.g., due to a UI change), the agent automatically kicks back into LLM mode, repairs the path, and updates its memory bank with the new version.
- **Parallel Execution**: Use the `--parallel` flag on the `run` command to execute multiple browser steps simultaneously if the mission allows.

```bash
qa-agent run "Verify 3 different product pages on the staging site" --parallel
```
