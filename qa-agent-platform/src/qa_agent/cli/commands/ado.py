import typer
app = typer.Typer(help="ADO Agent Commands")

@app.command()
def create_bug(from_file: str = typer.Option(..., "--from")):
    typer.echo(f"Creating ADO bug from: {from_file}")

