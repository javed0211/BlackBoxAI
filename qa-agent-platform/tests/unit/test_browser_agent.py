import pytest
from qa_agent.agents.browser.schemas import BrowserAction, LearnedWorkflow
from qa_agent.agents.browser.agent import BrowserAgent, BROWSER_SYSTEM_PROMPT
from qa_agent.memory.knowledge_store import KnowledgeStore
import json
import os
from pathlib import Path

def test_browser_action_schema_validation():
    """
    Test 1: Verify that BrowserAction and LearnedWorkflow schemas 
    correctly validate inputs and generate expected outputs.
    """
    action = BrowserAction(
        step_number=1,
        action_type="navigate",
        target_locator=None,
        input_value="https://google.com",
        description="Navigate to Google"
    )
    
    assert action.step_number == 1
    assert action.action_type == "navigate"
    assert action.input_value == "https://google.com"

    workflow = LearnedWorkflow(
        intent_match="search on google",
        start_url="https://google.com",
        actions=[action]
    )

    yaml_out = workflow.to_yaml()
    assert "name: search on google" in yaml_out
    assert "start_url: https://google.com" in yaml_out
    assert "action: navigate" in yaml_out

    ts_out = workflow.to_playwright_ts()
    assert "await page.goto('https://google.com');" in ts_out
    assert "test('Auto-generated test: search on google'" in ts_out


def test_browser_agent_system_prompt_integrity():
    """
    Test 2: Verify that the BROWSER_SYSTEM_PROMPT contains critical technical instructions.
    """
    # Ensure critical safety and extraction instructions are present
    assert "NEVER guess or hallucinate extraction data" in BROWSER_SYSTEM_PROMPT
    assert "ALWAYS use the `_get_dom_summary` tool" in BROWSER_SYSTEM_PROMPT
    assert "_terminate_workflow" in BROWSER_SYSTEM_PROMPT
    assert "Assertion FAILED" in BROWSER_SYSTEM_PROMPT


def test_knowledge_store_workflow_matching(tmp_path):
    """
    Test 3: Verify that KnowledgeStore correctly saves and retrieves workflows 
    by performing a fuzzy search on intent.
    """
    # Setup temporary directory for testing
    db_dir = tmp_path / "data/knowledge"
    db_dir.mkdir(parents=True)
    
    store = KnowledgeStore(db_dir=str(db_dir))
    
    workflow = LearnedWorkflow(
        intent_match="Login to Azure Portal",
        start_url="https://portal.azure.com",
        actions=[]
    )
    
    # Save the workflow
    saved = store.save_workflow(workflow)
    assert saved is True
    
    # Retrieve it with exact match
    retrieved = store.find_workflow("Login to Azure Portal")
    assert retrieved is not None
    assert retrieved.intent_match == "Login to Azure Portal"
    
    # Retrieve it with fuzzy match (case-insensitive substring)
    fuzzy_retrieved = store.find_workflow("azure portal")
    assert fuzzy_retrieved is not None
    assert fuzzy_retrieved.intent_match == "Login to Azure Portal"
    
    # Ensure no match for unrelated query
    no_match = store.find_workflow("google search")
    assert no_match is None
