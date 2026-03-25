from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class BrowserAction(BaseModel):
    """Represents a single successful interaction in the browser."""
    step_number: int
    action_type: Literal["navigate", "click", "type", "select", "wait", "verify", "extract"]
    target_locator: Optional[str] = Field(None, description="The CSS/XPath or Role used to find the element")
    input_value: Optional[str] = Field(None, description="Text typed or value selected")
    description: str = Field(..., description="Human-readable description of what this step did")
    success: bool = True

class LearnedWorkflow(BaseModel):
    """A fully validated, end-to-end browser workflow that the agent successfully completed."""
    intent_match: str = Field(..., description="The user intent this workflow solves (e.g. 'login to portal')")
    start_url: str
    actions: List[BrowserAction] = Field(default_factory=list)
    
    def to_yaml(self) -> str:
        """Helper to convert the Pydantic schema into a readable YAML test script."""
        yaml_lines = [f"name: {self.intent_match}", f"start_url: {self.start_url}", "steps:"]
        for action in self.actions:
            yaml_lines.append(f"  - step: {action.step_number}")
            yaml_lines.append(f"    action: {action.action_type}")
            yaml_lines.append(f"    description: {action.description}")
            if action.target_locator:
                yaml_lines.append(f"    locator: '{action.target_locator}'")
            if action.input_value:
                yaml_lines.append(f"    input: '{action.input_value}'")
        return "\n".join(yaml_lines)

    def to_playwright_ts(self) -> str:
        """Helper to convert the workflow into a functioning Playwright TypeScript test."""
        # Clean intent match from quotes so it doesn't break TS string wrapping
        clean_intent = self.intent_match.replace("'", "").replace('"', "")
        ts_lines = [
            "import { test, expect } from '@playwright/test';",
            "",
            f"test('Auto-generated test: {clean_intent}', async ({{ page }}) => {{",
        ]
        
        for action in self.actions:
            ts_lines.append(f"  // Step {action.step_number}: {action.description}")
            loc = action.target_locator
            
            # Semantic Locator Converter
            ts_loc = "page"
            if loc:
                import re
                match = re.search(r"(\w+)='([^']+)'", loc)
                if match:
                    strat = match.group(1)
                    val = match.group(2)
                    if strat == "role": ts_loc = f"page.getByRole('{val}')"
                    elif strat == "text": ts_loc = f"page.getByText('{val}')"
                    elif strat == "label": ts_loc = f"page.getByLabel('{val}')"
                    elif strat == "placeholder": ts_loc = f"page.getByPlaceholder('{val}')"
                    elif strat == "test_id": ts_loc = f"page.getByTestId('{val}')"
                    elif strat == "title": ts_loc = f"page.getByTitle('{val}')"
                    elif strat == "alt_text": ts_loc = f"page.getByAltText('{val}')"
                    else: ts_loc = f"page.locator(\"{val}\")"
                else: 
                    ts_loc = f"page.locator(\"{loc}\")"
            
            if action.action_type == "click" and loc:
                ts_lines.append(f"  await {ts_loc}.first().click();")
            elif action.action_type == "type" and loc:
                ts_lines.append(f"  await {ts_loc}.first().fill('{action.input_value}');")
            elif action.action_type == "navigate" and action.input_value:
                ts_lines.append(f"  await page.goto('{action.input_value}');")
            elif action.action_type == "verify" and loc:
                ts_lines.append(f"  await expect({ts_loc}.first()).toBeVisible();")
            elif action.action_type == "wait":
                timeout = action.input_value or "3000"
                ts_lines.append(f"  await page.waitForTimeout({timeout});")
                
        ts_lines.append("});")
        return "\n".join(ts_lines)
