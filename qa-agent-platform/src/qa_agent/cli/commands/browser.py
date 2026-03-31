import typer
from rich.console import Console
from qa_agent.graph.state import GraphState, MissionContext
from qa_agent.agents.browser.agent import browser_agent
import uuid

console = Console()
app = typer.Typer(help="Browser Agent Commands")

@app.command()
def test(
    mission: str = typer.Argument(..., help="The browser mission to execute"),
    workspace: str = typer.Option("./repo", "--workspace", help="Path to workspace")
):
    """
    Directly execute a browser mission using the AI Browser Agent.
    """
    console.print(f"[bold blue]🌍 Browser Mission:[/bold blue] {mission}")
    
    # Initialize state for the agent
    context = MissionContext(
        mission_id=str(uuid.uuid4()),
        user_input=mission,
        workspace=workspace
    )
    
    state = GraphState(mission=context)
    
    # Execute BrowserAgent directly
    result_state = browser_agent.run(state)
    
    if result_state.validation_passed:
        console.print("[bold green]✅ Mission Completed successfully![/bold green]")
    else:
        console.print("[bold red]❌ Mission Failed.[/bold red]")
        for err in result_state.errors:
            console.print(f"  - {err}")

