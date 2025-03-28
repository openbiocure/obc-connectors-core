import typer
from rich.console import Console
from typing import Optional

app = typer.Typer(help="Catalog operations")
console = Console()

@app.command()
def list():
    """
    List catalog items.
    """
    console.print("Listing catalog items")
    # Implementation will be added

@app.command()
def info(
    id: str = typer.Argument(..., help="ID to get info for"),
):
    """
    Get info about a specific catalog item.
    """
    console.print(f"Getting info for: [bold]{id}[/bold]")
    # Implementation will be added
