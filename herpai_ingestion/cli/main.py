import typer
from rich.console import Console
from typing import Optional
import logging
import os

from herpai_lib.core.engine import engine
from herpai_lib.core.config import YamlConfig

# Import subcommands
from src.cli import ingest, process, catalog, scheduler, sources, storage
from src.config import BiomedicalAppConfig

app = typer.Typer(
    name="herpai",
    help="HerpAI-Ingestion: A toolkit for biomedical data ingestion",
    add_completion=False,
)

console = Console()

# Add subcommands
app.add_typer(ingest.app, name="ingest")
app.add_typer(process.app, name="process") 
app.add_typer(catalog.app, name="catalog")
app.add_typer(scheduler.app, name="scheduler")
app.add_typer(sources.app, name="sources")
app.add_typer(storage.app, name="storage")

@app.callback()
def main(
    config: str = typer.Option(
        "config.yaml", "--config", "-c", help="Path to configuration file"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """
    HerpAI-Ingestion: A toolkit for biomedical data ingestion.
    
    This tool provides functionality for ingesting, processing, and storing biomedical
    data from various sources like PubMed, Europe PMC, and ClinicalTrials.gov.
    """
    # Set up logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create data directories if they don't exist
    os.makedirs("data/pdfs", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    # Initialize engine and load configuration
    engine.initialize()
    
    # Load the biomedical app config (extending base AppConfig)
    app_config = BiomedicalAppConfig.from_yaml(config)
    
    # Register the app config as a singleton
    engine.register_instance(BiomedicalAppConfig, app_config)
    
    if verbose:
        console.print(f"Loaded configuration from [bold]{config}[/bold]")

if __name__ == "__main__":
    app()
