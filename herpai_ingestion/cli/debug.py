"""Debug CLI commands for testing connectors."""

import click
import asyncio
import logging
from typing import Optional

from herpai_connector_sdk.utils.connector_loader import ConnectorLoader

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@click.group(name='debug')
def debug():
    """Debug commands for testing connectors."""
    pass

@debug.command(name='test')
@click.argument('connector_name')
@click.option('--query', '-q', help='Search query')
@click.option('--id', '-i', help='Document ID to fetch')
@click.option('--api-key', envvar='HERPAI_API_KEY', help='API key', default='')
@click.option('--limit', '-l', type=int, default=10, help='Number of results')
@click.option('--version', '-v', help='Connector version to use')
def test_connector(connector_name: str, query: Optional[str], id: Optional[str], 
         api_key: Optional[str], limit: int, version: Optional[str]):
    """Test a connector's functionality.
    
    CONNECTOR_NAME: Name of the connector to test (e.g., 'pubmed')
    """
    async def run():
        try:
            async with ConnectorLoader.managed_connector(connector_name, version) as connector:
                # Configure with API key if provided
                if api_key:
                    await connector.authenticate({"api_key": api_key})
                
                if query:
                    # Test search
                    click.echo(f"Searching {connector_name} v{version if version else 'latest'}...")
                    results = await connector.search(query, limit=limit)
                    if results and 'total_results' in results:
                        click.echo(f"Found {results['total_results']} results")
                        if 'document_ids' in results:
                            for doc_id in results['document_ids'][:limit]:
                                click.echo(f"- {doc_id}")
                        else:
                            click.echo("No document IDs found in response")
                    else:
                        click.echo("No results found")
                
                if id:
                    # Test document retrieval
                    click.echo(f"\nFetching document {id}...")
                    doc = await connector.get_by_id(id)
                    if doc:
                        click.echo(f"Title: {doc.get('title', 'No title')}")
                        click.echo(f"Abstract: {doc.get('abstract', 'No abstract')[:200]}...")
                    else:
                        click.echo("Document not found")
        except Exception as e:
            logger.error(f"Error testing connector: {str(e)}")
            raise click.ClickException(str(e))
    
    asyncio.run(run()) 