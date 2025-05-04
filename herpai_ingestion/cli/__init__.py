"""CLI commands for HerpAI ingestion system."""

import click
from .debug import debug

@click.group()
def cli():
    """HerpAI ingestion system CLI."""
    pass

cli.add_command(debug) 