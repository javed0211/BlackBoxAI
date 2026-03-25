import typer
app = typer.Typer(help="Browser Agent Commands")

@app.command()
def test(mission: str, workspace: str = "./repo"):
    typer.echo(f"Browser test: {mission}")

