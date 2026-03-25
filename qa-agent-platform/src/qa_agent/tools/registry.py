from typing import Callable, Any, Dict, List
from .hooks import ToolHook, AgentShieldHook, GitIntegrityHook, ConfigProtectionHook, QualityGateHook

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        # Preload Security and Quality Hooks globally
        self._hooks: List[ToolHook] = [
            AgentShieldHook(), 
            GitIntegrityHook(), 
            ConfigProtectionHook(), 
            QualityGateHook()
        ]
        
        self.register_core_tools()
        
    def register_tool(self, name: str, func: Callable):
        """Registers a tool function logic to be used by the LLC."""
        self._tools[name] = func

    def register_core_tools(self):
        """Imports and registers the underlying system tools"""
        from . import filesystem, shell, playwright, ado, jira

        
        # OS / CLI
        self.register_tool("read_file", filesystem.read_file)
        self.register_tool("write_file", filesystem.write_file)
        self.register_tool("delete_file", filesystem.delete_file)
        self.register_tool("list_dir", filesystem.list_dir)
        self.register_tool("search_files", filesystem.search_files)
        self.register_tool("run_command", shell.run_command)
        
        # Automator (Browser Navigation/State)
        self.register_tool("open_url", playwright.open_url)
        self.register_tool("open_new_tab", playwright.open_new_tab)
        self.register_tool("switch_tab", playwright.switch_tab)
        self.register_tool("configure_dialogs", playwright.configure_dialogs)
        self.register_tool("evaluate_js", playwright.evaluate_js)

        # Automator (Interactions)
        self.register_tool("click_element", playwright.click_element)
        self.register_tool("double_click_element", playwright.double_click_element)
        self.register_tool("hover_element", playwright.hover_element)
        self.register_tool("type_text", playwright.type_text)
        self.register_tool("press_key", playwright.press_key)
        self.register_tool("select_option", playwright.select_option)
        self.register_tool("check_checkbox", playwright.check_checkbox)
        self.register_tool("upload_file", playwright.upload_file)
        self.register_tool("scroll", playwright.scroll)

        
        # Automator (Testing / Assertions)
        self.register_tool("assert_state", playwright.assert_state)

        # Telemetry & DOM
        self.register_tool("get_dom_summary", playwright.get_dom_summary)
        self.register_tool("take_screenshot", playwright.take_screenshot)
        self.register_tool("start_trace", playwright.start_trace)
        self.register_tool("stop_trace", playwright.stop_trace)
        
        # Enterprise Integrations (Azure DevOps)
        self.register_tool("create_ado_bug", ado.create_ado_bug)
        self.register_tool("attach_to_ado_bug", ado.attach_to_ado_bug)
        self.register_tool("update_ado_test_result", ado.update_ado_test_result)
        
        # Enterprise Integrations (Jira)
        self.register_tool("create_jira_bug", jira.create_jira_bug)
        self.register_tool("attach_to_jira_bug", jira.attach_to_jira_bug)
        self.register_tool("comment_on_jira_issue", jira.comment_on_jira_issue)
        
        # Validation Engine (Group 2)
        self.register_tool("accessibility_audit", playwright.accessibility_audit)
        self.register_tool("visual_compare", playwright.visual_compare)


        
    def add_hook(self, hook: ToolHook):
        """Dynamically attach new validation layers at runtime"""
        self._hooks.append(hook)
        
    def execute(self, tool_name: str, **kwargs) -> Any:
        """Executes the tool wrapped securely inside the pre and post hooks"""
        if tool_name not in self._tools:
            raise KeyError(f"Tool '{tool_name}' is not registered in the system.")
            
        # Run Pre-execution Hooks (e.g. AgentShield Security Analysis)
        for hook in self._hooks:
            hook.before_execute(tool_name, **kwargs)
            
        # Run Internal Tool
        try:
            result = self._tools[tool_name](**kwargs)
        except Exception as e:
            raise e
            
        # Run Post-execution Hooks
        for hook in self._hooks:
            hook.after_execute(tool_name, str(result))
            
        return result

# Expose global instance to be used across the graph
global_registry = ToolRegistry()
