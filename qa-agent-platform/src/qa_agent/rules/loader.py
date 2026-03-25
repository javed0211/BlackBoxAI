import os
from pathlib import Path
from typing import List

def load_rules(categories: List[str] = ["common"]) -> str:
    """
    Simulates the everything-claude-code Rules system.
    Dynamically loads all .md rules from configured directories to be injected
    into the System Prompts of running LangChain Agents.
    
    Example: load_rules(["common", "python"])
    """
    base_dir = Path(__file__).parent
    rules_text = []
    
    # Header block
    rules_text.append("============ GLOBAL SYSTEM RULES ============")
    rules_text.append("You MUST strictly follow these principles:")
    
    for category in categories:
        cat_dir = base_dir / category
        if cat_dir.exists() and cat_dir.is_dir():
            for file_path in sorted(cat_dir.glob("*.md")):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    rules_text.append(f"\n--- Context: {category}/{file_path.name} ---")
                    rules_text.append(content)
                    
    rules_text.append("\n=============================================")
    return "\n".join(rules_text)
