import sys
import os
sys.path.append('src')

from qa_agent.artifacts.reports import ReportGenerator

def generate_sample():
    actions = [
        {'step_number': 1, 'action_type': 'navigate', 'target_locator': '', 'input_value': 'https://www.google.com', 'description': 'Navigating to search engine'},
        {'step_number': 2, 'action_type': 'type', 'target_locator': "role='searchbox'", 'input_value': 'Playwright Testing', 'description': 'Typing query'},
        {'step_number': 3, 'action_type': 'click', 'target_locator': "role='button' (name='Google Search')", 'input_value': '', 'description': 'Submitting form'},
        {'step_number': 4, 'action_type': 'verify', 'target_locator': "text='Results'", 'input_value': '', 'description': 'Verifying results page'}
    ]
    
    analytics = {
        'duration': 12.5,
        'total_tokens': 1450,
        'total_cost': 0.0075
    }
    
    html = ReportGenerator.generate_html(
        mission_input="Google Search for Playwright Framework testing docs",
        success=True,
        actions=actions,
        analytics=analytics,
        start_url="https://www.google.com"
    )
    
    os.makedirs('data/artifacts', exist_ok=True)
    with open('data/artifacts/sample_report.html', 'w') as f:
        f.write(html)
    print("Sample report generated at data/artifacts/sample_report.html")

if __name__ == "__main__":
    generate_sample()
