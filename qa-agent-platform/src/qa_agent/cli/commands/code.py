import typer
app = typer.Typer(help="Code Agent Commands")

@app.command()
def fix(mission: str, workspace: str = "./repo"):
    typer.echo(f"Code fix: {mission}")

