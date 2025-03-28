import typer
from rich.console import Console
from typing import Optional

app = typer.Typer(help="Process operations")
console = Console()

@app.command()
def list():
    """
    List process items.
    """
    console.print("Listing process items")
    # Implementation will be added

@app.command()
def info(
    id: str = typer.Argument(..., help="ID to get info for"),
):
    """
    Get info about a specific process item.
    """
    console.print(f"Getting info for: [bold]{id}[/bold]")
    # Implementation will be added
