import typer
from rich.console import Console
from rich.panel import Panel

console = Console()
app = typer.Typer(help="Run Missions")

def execute_run(
    mission: str,
    workspace: str,
    dry_run: bool,
    approval_mode: str,
    parallel: bool,
    max_retries: int,
    model_profile: str,
    output_format: str
):
    from qa_agent.graph.builder import build_graph
    from qa_agent.graph.state import MissionContext, GraphState
    import uuid

    console.print(Panel(f"[bold green]Starting Mission:[/bold green] {mission}"))
    
    # Initialize state
    context = MissionContext(
        mission_id=str(uuid.uuid4()),
        user_input=mission,
        workspace=workspace,
        dry_run=dry_run,
        approval_mode=approval_mode  # type: ignore
    )
    
    initial_state = GraphState(
        mission=context
    )
    
    console.print("[cyan]Initializing Graph Engine...[/cyan]")
    graph = build_graph()
    config = {"configurable": {"thread_id": context.mission_id}}
    
    console.print("[cyan]Executing Mission...[/cyan]")
    result = graph.invoke(initial_state.model_dump(), config=config)
    
    console.print(Panel(f"[bold blue]Final Summary:[/bold blue]\n{result.get('final_summary', 'No summary generated.')}"))

