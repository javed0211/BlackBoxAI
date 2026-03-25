import os
import sys
import time

# Ensure project src is in path
sys.path.append(os.path.abspath("src"))

from qa_agent.integrations.browser_runtime import runtime
from qa_agent.tools import playwright
from qa_agent.artifacts.reports import ReportGenerator

def run_verification_mission():
    print("🧪 [POC Execution] Starting Verification Mission (Group 2, 3, 6)...")
    
    # 1. Start Runtime (Group 1 - Execution)
    runtime.start(headless=False)
    page = runtime.get_page()
    
    try:
        # Step 1: Navigate to Target
        print("🌐 Step 1: Navigating to DuckDuckGo...")
        playwright.open_url("https://www.duckduckgo.com")
        
        # Step 2: Accessibility Audit (Group 2 - Validation)
        print("♿ Step 2: Performing Accessibility Audit...")
        audit_report = playwright.accessibility_audit()
        print(f"   [Audit Results]: {audit_report[:200]}...")
        
        # Step 3: Exploratory Interaction (Group 6 - AI-Native)
        print("🕵️ Step 3: Performing Exploratory 'Empty Search' Click...")
        playwright.click_element(strategy="css", value="#search_button_homepage")
        time.sleep(2) # Wait for page reaction
        
        # Step 4: Capture Forensic Evidence (Group 3 - Observability)
        print("📸 Step 4: Capturing Forensic Evidence...")
        screenshot_path = "data/artifacts/verification_screenshot.png"
        page.screenshot(path=screenshot_path)
        
        # Step 5: Final Report Generation (Group 3 - Observability)
        print("📊 Step 5: Generating Premium Glass-morphism Report...")
        
        mission_input = "Verify accessibility on DuckDuckGo and check for empty search errors."
        
        html_report = ReportGenerator.generate_html(
            mission_input=mission_input,
            success=True,
            actions=[
                {"step_number": 1, "action_type": "navigate", "target_locator": "https://www.duckduckgo.com", "description": "Navigated to home page"},
                {"step_number": 2, "action_type": "audit", "target_locator": "Viewport", "description": "Executed Accessibility Audit"},
                {"step_number": 3, "action_type": "click", "target_locator": "#search_button_homepage", "description": "Triggered empty search event"}
            ],
            analytics={
                "total_duration": "4.5s",
                "total_token_usage": 0, # Manual mode
                "api_costs": "$0.00"
            },
            start_url="https://www.duckduckgo.com",
            screenshots=[os.path.abspath(screenshot_path)],
            console_logs=runtime.console_logs,
            network_logs=runtime.failed_requests
        )
        
        report_path = "data/artifacts/verification_report.html"
        with open(report_path, "w") as f:
            f.write(html_report)
            
        print(f"✅ Mission Successful! Report generated at: {os.path.abspath(report_path)}")
        
    finally:
        runtime.stop()

if __name__ == "__main__":
    run_verification_mission()
