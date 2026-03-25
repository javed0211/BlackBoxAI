import subprocess

def run_command(command: str, cwd: str = None) -> str:
    """
    Executes a bash shell command locally. 
    Strictly wrapped by the AgentShield hooking engine to block destructive logic natively.
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            text=True,
            capture_output=True,
            timeout=120  # Critical for autonomous LLM runs to prevent blocking
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n--- STDERR ---\n{result.stderr}"
            
        return output.strip() if output.strip() else f"Command '{command}' executed successfully with no output."
        
    except subprocess.TimeoutExpired:
        return f"Error: Command '{command}' timed out after 120 seconds."
    except Exception as e:
        return f"Error executing command '{command}': {e}"
