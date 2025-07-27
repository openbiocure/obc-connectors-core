"""Main CLI module."""

import click

from .debug import debug


@click.group()
def cli():
    """OpenBioCure Ingestion CLI."""
    pass


cli.add_command(debug)
