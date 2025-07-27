"""CLI commands for OpenBioCure ingestion system."""

import click
from .debug import debug


@click.group()
def cli():
    """OpenBioCure ingestion system CLI."""
    pass


cli.add_command(debug)
