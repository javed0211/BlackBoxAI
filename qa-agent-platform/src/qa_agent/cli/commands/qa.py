import typer
app = typer.Typer(help="QA Agent Commands")

@app.command()
def analyze_failure(input: str = typer.Option(..., "--input")):
    typer.echo(f"Analyzing QA failure from: {input}")

@app.command()
def generate_tests(story: str = typer.Option(..., "--story")):
    typer.echo(f"Generating tests for: {story}")

