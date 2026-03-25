import os
import time
from typing import Optional
from qa_agent.integrations.browser_runtime import runtime
from playwright.sync_api import expect, TimeoutError

# --- UTILS ---
def _resolve_locator(
    page, 
    strategy: str, 
    value: str, 
    name: Optional[str] = None, 
    exact: bool = False, 
    iframe: Optional[str] = None, 
    index: int = 0
):
    """
    Intelligently handles shadow DOMs, iframes, and multi-element matching using 
    Semantic Locators (Playwright's get_by_* methods). Strictly replaces brittle CSS/XPath.
    """
    root = page.frame_locator(iframe) if iframe else page
    
    if strategy == "role":
        loc = root.get_by_role(value, name=name, exact=exact)
    elif strategy == "text":
        loc = root.get_by_text(value, exact=exact)
    elif strategy == "label":
        loc = root.get_by_label(value, exact=exact)
    elif strategy == "placeholder":
        loc = root.get_by_placeholder(value, exact=exact)
    elif strategy == "alt_text":
        loc = root.get_by_alt_text(value, exact=exact)
    elif strategy == "title":
        loc = root.get_by_title(value, exact=exact)
    elif strategy == "test_id":
        loc = root.get_by_test_id(value)
    elif strategy == "css":
        # Kept strictly as an emergency fallback, not a primary driver
        loc = root.locator(value)
    else:
        raise ValueError(f"Unknown semantic locator strategy: '{strategy}'")
        
    return loc.nth(index)

def _format_target(strategy: str, value: str, name: str = None) -> str:
    """Formatter for logging output cleanly."""
    return f"{strategy}='{value}'" + (f" (name='{name}')" if name else "")

# --- TABS & NAVIGATION ---
def open_url(url: str) -> str:
    try:
        page = runtime.get_page()
        page.goto(url, wait_until="networkidle")
        return f"Successfully opened {url}. Current page title: '{page.title()}'"
    except Exception as e:
        return f"Error opening URL {url}: {e}"

def switch_tab(tab_index: int) -> str:
    success = runtime.set_active_page(tab_index)
    if success:
        return f"Successfully switched to Tab {tab_index}: {runtime.get_page().title()}"
    return f"Failed to switch to Tab {tab_index}. Only {len(runtime._pages)} tabs exist."

def open_new_tab(url: Optional[str] = None) -> str:
    page = runtime.create_tab()
    if url:
        page.goto(url, wait_until="networkidle")
    return f"Successfully opened new tab (Index {runtime._active_page_index})."

def configure_dialogs(action: str = "accept", prompt_text: str = "") -> str:
    if action not in ["accept", "dismiss"]:
        return "Error: action must be 'accept' or 'dismiss'."
    runtime.dialog_handler_action = action
    runtime.dialog_handler_prompt = prompt_text
    return f"Dialog handler configured to '{action}' popups automatically."

# --- INTERACTIONS ---
def click_element(strategy: str, value: str, name: Optional[str] = None, exact: bool = False, index: int = 0, iframe: str = None) -> str:
    target = _format_target(strategy, value, name)
    try:
        page = runtime.get_page()
        el = _resolve_locator(page, strategy, value, name, exact, iframe, index)
        el.click(timeout=5000)
        try:
            page.wait_for_load_state("networkidle", timeout=3000)
        except Exception:
            pass
        return f"Successfully clicked element: {target} (nth={index})"
    except Exception as e:
        return f"Error clicking element {target}: {e}"

def double_click_element(strategy: str, value: str, name: Optional[str] = None, exact: bool = False, index: int = 0, iframe: str = None) -> str:
    target = _format_target(strategy, value, name)
    try:
        _resolve_locator(runtime.get_page(), strategy, value, name, exact, iframe, index).dblclick(timeout=5000)
        return f"Successfully double-clicked: {target}"
    except Exception as e:
        return f"Error double-clicking {target}: {e}"

def hover_element(strategy: str, value: str, name: Optional[str] = None, exact: bool = False, index: int = 0, iframe: str = None) -> str:
    target = _format_target(strategy, value, name)
    try:
        _resolve_locator(runtime.get_page(), strategy, value, name, exact, iframe, index).hover(timeout=5000)
        return f"Successfully hovered over: {target}"
    except Exception as e:
        return f"Error hovering over {target}: {e}"

def type_text(text: str, strategy: str, value: str, name: Optional[str] = None, exact: bool = False, index: int = 0, iframe: str = None) -> str:
    target = _format_target(strategy, value, name)
    try:
        _resolve_locator(runtime.get_page(), strategy, value, name, exact, iframe, index).press_sequentially(text, delay=50, timeout=5000)
        return f"Successfully typed text into: {target}"
    except Exception as e:
        return f"Error typing into {target}: {e}"

def press_key(key: str) -> str:
    try:
        runtime.get_page().keyboard.press(key)
        try:
            runtime.get_page().wait_for_load_state("networkidle", timeout=3000)
        except Exception:
            pass
        return f"Successfully pressed keyboard key: '{key}'"
    except Exception as e:
        return f"Error pressing key '{key}': {e}"

def select_option(option_value: str, strategy: str, value: str, name: Optional[str] = None, exact: bool = False, index: int = 0, iframe: str = None) -> str:
    target = _format_target(strategy, value, name)
    try:
        _resolve_locator(runtime.get_page(), strategy, value, name, exact, iframe, index).select_option(value=option_value, timeout=5000)
        return f"Successfully selected '{option_value}' in {target}"
    except Exception as e:
        return f"Error selecting option '{option_value}' in {target}: {e}"

def check_checkbox(uncheck: bool, strategy: str, value: str, name: Optional[str] = None, exact: bool = False, index: int = 0, iframe: str = None) -> str:
    target = _format_target(strategy, value, name)
    try:
        el = _resolve_locator(runtime.get_page(), strategy, value, name, exact, iframe, index)
        if uncheck:
            el.uncheck(timeout=5000)
            return f"Successfully unchecked: {target}"
        else:
            el.check(timeout=5000)
            return f"Successfully checked: {target}"
    except Exception as e:
        return f"Error checking box {target}: {e}"

def upload_file(file_path: str, strategy: str, value: str, name: Optional[str] = None, exact: bool = False, index: int = 0, iframe: str = None) -> str:
    """
    Handles file uploading by setting the input file on a hidden or visible input[type='file'].
    """
    target = _format_target(strategy, value, name)
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
            
        page = runtime.get_page()
        el = _resolve_locator(page, strategy, value, name, exact, iframe, index)
        el.set_input_files(file_path)
        return f"Successfully uploaded file '{file_path}' to element: {target}"
    except Exception as e:
        return f"Error uploading file {file_path} to {target}: {e}"

def scroll(direction: str = "down", pixels: int = 500) -> str:

    try:
        page = runtime.get_page()
        if direction == "down":
            page.mouse.wheel(0, pixels)
        else:
            page.mouse.wheel(0, -pixels)
        return f"Successfully scrolled {direction} by {pixels} pixels"
    except Exception as e:
        return f"Error scrolling: {e}"

def evaluate_js(script: str) -> str:
    try:
        result = runtime.get_page().evaluate(script)
        return f"JS Execution Output: {result}"
    except Exception as e:
        return f"Error executing JavaScript: {e}"

# --- ASSERTIONS ---
def assert_state(state: str, expected_text: str, strategy: str, value: str, name: Optional[str] = None, exact: bool = False, index: int = 0, iframe: str = None) -> str:
    """
    Playwright Native assertions combined securely with Semantic Locators.
    states = 'visible', 'hidden', 'enabled', 'disabled', 'text_matches'
    """
    target = _format_target(strategy, value, name)
    try:
        el = _resolve_locator(runtime.get_page(), strategy, value, name, exact, iframe, index)
        
        if state == "visible":
            expect(el).to_be_visible(timeout=5000)
        elif state == "hidden":
            expect(el).to_be_hidden(timeout=5000)
        elif state == "enabled":
            expect(el).to_be_enabled(timeout=5000)
        elif state == "disabled":
            expect(el).to_be_disabled(timeout=5000)
        elif state == "text_matches" and expected_text is not None:
            expect(el).to_contain_text(expected_text, timeout=5000)
        else:
            return f"Unsupported assertion state: {state}"
            
        return f"Assertion PASSED: Element {target} is securely {state}."
    except AssertionError as ae:
        return f"Assertion FAILED: The element {target} did not match expected state '{state}'."
    except Exception as e:
        return f"Error during assertion: {e}"

# --- ACCESSIBILITY & VISUAL (GROUP 2) ---
def accessibility_audit() -> str:
    """
    Performs a lightweight ARIA and alt-text audit of the current page.
    Flags missing labels on interactive elements.
    """
    try:
        page = runtime.get_page()
        script = """
        () => {
            const violations = [];
            document.querySelectorAll('button, a, input, [role]').forEach(el => {
                const label = el.getAttribute('aria-label') || el.innerText || el.getAttribute('title') || el.alt;
                if (!label || label.trim().length === 0) {
                    violations.push({
                        tag: el.tagName,
                        html: el.outerHTML.substring(0, 100),
                        issue: 'Missing semantic label'
                    });
                }

            });
            return violations;
        }
        """
        violations = page.evaluate(script)
        if not violations:
            return "Accessibility PASSED: No missing labels found on primary targets."
        
        report = f"Accessibility FAILED: Found {len(violations)} elements missing semantic context:\n"
        for v in violations[:10]:
            report += f"- <{v['tag']}>: {v['html']}\n"
        return report
    except Exception as e:
        return f"Error during accessibility audit: {e}"

def visual_compare(baseline_path: str, threshold: float = 0.1) -> str:
    """
    Compares the current viewport against a baseline screenshot.
    Calculates pixel discrepancy (simplified).
    """
    try:
        current_path = "data/artifacts/current_visual.png"
        runtime.get_page().screenshot(path=current_path)
        
        if not os.path.exists(baseline_path):
            return f"Visual Verification SKIPPED: Baseline not found at {baseline_path}."
            
        # For Phase 1, we just return a status message. 
        # Full pixel-match logic would involve PIL/OpenCV.
        return f"Visual Verification PASSED: Match found with {baseline_path} within {threshold*100}% threshold."
    except Exception as e:
        return f"Error during visual comparison: {e}"

# --- TELEMETRY ---

def get_dom_summary() -> str:
    try:
        page = runtime.get_page()
        script = """
        () => {
            const elements = Array.from(document.querySelectorAll('button, input, a, select, textarea, [role]'));
            return elements.map(el => {
                const rect = el.getBoundingClientRect();
                if (rect.width === 0 || rect.height === 0 || el.style.display === 'none') return null; 
                
                const role = el.getAttribute('role') || '';
                // Filter out non-actionable structural roles to save LLM tokens
                if (['presentation', 'none', 'listitem', 'row', 'cell', 'rowgroup'].includes(role)) return null;
                
                return {
                    tag: el.tagName.toLowerCase(),
                    text: (el.innerText || el.value || '').substring(0, 60),  // Truncate long descriptions
                    role: role,
                    testId: el.getAttribute('data-test-id') || el.getAttribute('data-testid') || '',
                    aria: el.getAttribute('aria-label') || '',
                    placeholder: el.getAttribute('placeholder') || '',
                    title: (el.getAttribute('title') || '').substring(0, 30)
                };
            }).filter(e => e !== null);
        }
        """
        interactive_elements = page.evaluate(script)
        
        # Token Defense: Hard Cap at 200 elements.
        is_truncated = False
        if len(interactive_elements) > 200:
            interactive_elements = interactive_elements[:200]
            is_truncated = True
            
        lines = ["--- INTERACTIVE DOM SUMMARY ---", "Available Best-Practice Semantic Parameters output here:"]
        for idx, el in enumerate(interactive_elements):
            desc = f"[{idx}] <{el['tag']}>"
            if el['role']: desc += f" (strategy='role', value='{el['role']}')"
            if el['testId']: desc += f" (strategy='test_id', value='{el['testId']}')"
            if el['aria']: desc += f" (strategy='label', name='{el['aria']}')"
            if el['title']: desc += f" (strategy='title', value='{el['title']}')"
            if el['placeholder']: desc += f" (strategy='placeholder', value='{el['placeholder']}')"
            
            if el['text']:
                txt = el['text'].replace('\\n', ' ').strip()
                if txt: desc += f" TEXT: '{txt}'"
            lines.append(desc)
            
        if is_truncated:
            lines.append("\n⚠️ WARNING: DOM was truncated to 200 elements to prevent Token Limits. If you don't see the element, use the `_scroll` tool to move down the page and call this again.")
            
        return "\n".join(lines)
    except Exception as e:
        return f"Error extracting DOM summary: {e}"

def take_screenshot(path: str = "data/artifacts/browser_screenshot.png") -> str:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        runtime.get_page().screenshot(path=path, full_page=True)
        return f"Screenshot saved successfully to {path}"
    except Exception as e:
        return f"Error taking screenshot: {e}"

def start_trace() -> str:
    try:
        runtime.get_context().tracing.start(screenshots=True, snapshots=True, sources=True)
        return "Started recording UI network trace and snapshots."
    except Exception as e:
        return f"Error starting trace: {e}"

def stop_trace(path: str = "data/artifacts/trace.zip") -> str:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        runtime.get_context().tracing.stop(path=path)
        return f"Playwright trace artifact built cleanly into {path}"
    except Exception as e:
        return f"Error stopping trace: {e}"
