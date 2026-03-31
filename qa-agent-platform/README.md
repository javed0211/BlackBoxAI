# 🚀 QA-First Agentic CLI Platform

A powerful, enterprise-grade AI QA Automation platform that builds, executes, and heals end-to-end browser and api tests.

## 🌟 Key Features

- **Agentic Multi-Agent Graph**: Uses LangGraph to orchestrate between Specialized Browser, Code, and QA agents.
- **Continuous Learning Memory**: Automatically remembers successful UI navigations and generates native Playwright artifacts.
- **Self-Healing Automation**: If a test fails due to a UI change, the Browser Agent automatically repairs the path using LLM intelligence.
- **Deep Failure Analysis**: Generates technical diagnoses, repro steps, and suggested fixes for complex bugs.

---

## 🌎 Browser Agent (Web Automation)

The Browser Agent is the core of our web automation engine. It understands semantic DOMs and generates robust Playwright scripts.

### **📖 [Learn How To Use The Browser Agent In CLI](./BROWSER_AGENT_CLI.md)**

---

## 🛠️ Quick Start

### Installation
Execute from the project root:
```bash
# 1. Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -e .
playwright install
```

### Run a Mission
```bash
qa-agent run "Login to our staging site, click 'Dashboard', and verify 3 metrics are visible"
```

## 📂 Project Structure

- `src/qa_agent/agents/`: Specialized agent implementations (Browser, Code, QA, etc.).
- `src/qa_agent/graph/`: LangGraph orchestration logic.
- `src/qa_agent/memory/`: The knowledge store (Long-term memory bank).
- `data/`: Artifacts, logs, and knowledge storage.

## 🧪 Running Tests

To verify the platform integrity:

```bash
pytest tests/unit
```
