import typer
from rich.console import Console
from typing import Optional, List

app = typer.Typer(help="Run ingestion from a specific source")
console = Console()

@app.command()
def run(
    source: str = typer.Argument(..., help="Source to ingest from (pubmed, europepmc, clinicaltrials)"),
    query: str = typer.Option(..., "--query", "-q", help="Search query for the source"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum number of records to ingest"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory for downloaded files"),
    batch_size: int = typer.Option(0, "--batch-size", "-b", help="Batch size for requests (0 = use config default)"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-download of existing documents"),
    tags: Optional[List[str]] = typer.Option(None, "--tag", help="Tags to assign to ingested documents"),
):
    """
    Run an ingestion job from a specific source.
    """
    console.print(f"Running ingestion from [bold]{source}[/bold] with query: [italic]{query}[/italic]")
    console.print(f"Limit: {limit}, Batch size: {batch_size or 'default'}")
    # Implementation will be added
