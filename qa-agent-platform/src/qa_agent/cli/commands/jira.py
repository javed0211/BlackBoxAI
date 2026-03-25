import typer
app = typer.Typer(help="Jira Agent Commands")

@app.command()
def create_bug(from_file: str = typer.Option(..., "--from")):
    typer.echo(f"Creating Jira bug from: {from_file}")

