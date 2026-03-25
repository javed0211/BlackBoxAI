import typer
from .commands import run, code, browser, qa, ado, jira

app = typer.Typer(help="QA-first Agentic CLI Platform")

@app.command(name="run")
def run_command(
    mission: str = typer.Argument(..., help="The mission to execute"),
    workspace: str = typer.Option("./repo", "--workspace", help="Path to workspace"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Enable dry run mode"),
    approval_mode: str = typer.Option("smart", "--approval-mode", help="strict|smart|off"),
    parallel: bool = typer.Option(False, "--parallel", help="Enable parallel flow"),
    max_retries: int = typer.Option(2, "--max-retries", help="Max retry attempts"),
    model_profile: str = typer.Option("fast", "--model-profile", help="fast|balanced|deep"),
    output: str = typer.Option("markdown", "--output", help="json|table|markdown")
):
    """
    Run an end-to-end agentic mission based on natural language intent.
    """
    run.execute_run(
        mission=mission,
        workspace=workspace,
        dry_run=dry_run,
        approval_mode=approval_mode,
        parallel=parallel,
        max_retries=max_retries,
        model_profile=model_profile,
        output_format=output
    )

app.add_typer(code.app, name="code", help="Code agent commands")
app.add_typer(browser.app, name="browser", help="Browser agent commands")
app.add_typer(qa.app, name="qa", help="QA agent commands")
app.add_typer(ado.app, name="ado", help="ADO agent commands")
app.add_typer(jira.app, name="jira", help="Jira agent commands")

if __name__ == "__main__":
    app()
