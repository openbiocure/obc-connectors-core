import typer
from rich.console import Console
from typing import Optional

app = typer.Typer(help="Storage operations")
console = Console()

@app.command()
def list():
    """
    List storage items.
    """
    console.print("Listing storage items")
    # Implementation will be added

@app.command()
def info(
    id: str = typer.Argument(..., help="ID to get info for"),
):
    """
    Get info about a specific storage item.
    """
    console.print(f"Getting info for: [bold]{id}[/bold]")
    # Implementation will be added
