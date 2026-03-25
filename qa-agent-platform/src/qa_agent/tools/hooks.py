import re
from typing import Any

class ToolHook:
    def before_execute(self, tool_name: str, **kwargs_input) -> None:
        pass
        
    def after_execute(self, tool_name: str, result: str) -> None:
        pass

class AgentShieldHook(ToolHook):
    """
    Mimics 'everything-claude-code' AgentShield security by analyzing tool arguments
    for dangerous bash commands or restricted paths BEFORE they run on the CLI.
    """
    DANGEROUS_PATTERNS = [
        re.compile(r'\brm\s+-r?[fF]?\b'),  
        re.compile(r'\bmkfs\b'),         
        re.compile(r'\bsudo\b'),         
        re.compile(r'>\s*/dev/sd[a-z]+') 
    ]
    
    def before_execute(self, tool_name: str, **kwargs_input) -> None:
        if tool_name == "run_command":
            cmd = kwargs_input.get("command", "")
            for pattern in self.DANGEROUS_PATTERNS:
                if pattern.search(cmd):
                    raise ValueError(f"🚨 [AgentShield] Dangerous shell command detected: '{cmd}'. Action prevented!")
        elif tool_name in ["write_file", "delete_file"]:
            path = kwargs_input.get("path", "")
            if ".git/" in path or "/etc/" in path:
                raise ValueError(f"🚨 [AgentShield] Agent attempted to mutate protected path: {path}")

class GitIntegrityHook(ToolHook):
    """
    Mimics 'block-no-verify' from hooks.json to protect pre-commit mechanisms.
    """
    def before_execute(self, tool_name: str, **kwargs_input) -> None:
        if tool_name in ["run_command", "shell"]:
            cmd = kwargs_input.get("command", "")
            if "--no-verify" in cmd:
                raise ValueError("🚨 [Git Integrity] Do not bypass git hooks. Fix the code instead of using --no-verify.")

class ConfigProtectionHook(ToolHook):
    """
    Mimics 'config-protection.js' to prevent the LLM from simply turning off linters
    when it gets frustrated with failing tests.
    """
    PROTECTED_CONFIGS = [".eslintrc", "pyproject.toml", ".flake8", ".prettierrc"]
    
    def before_execute(self, tool_name: str, **kwargs_input) -> None:
        if tool_name in ["write_file", "replace_file_content", "delete_file"]:
            path = kwargs_input.get("path", "")
            for config in self.PROTECTED_CONFIGS:
                if config in path:
                    raise ValueError(f"🚨 [Config Protection] Blocked modification to {config}. Do not weaken repository linters to solve a problem. Fix the problem instead.")

class QualityGateHook(ToolHook):
    """
    Mimics 'post-edit-console-warn.js' checking for debugging statements left behind.
    """
    def before_execute(self, tool_name: str, **kwargs_input) -> None:
        if tool_name in ["write_file", "replace_file_content"]:
            content = kwargs_input.get("content", "") + kwargs_input.get("replacement", "")
            if "console.log" in content or "print(\"debug" in content.lower():
                print("⚠️ [Quality Gate] Warning: You are leaving a debug print statement in the file.")
