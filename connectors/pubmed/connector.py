"""PubMed Connector Implementation."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, AsyncIterator

from obc_connector_sdk.base_connector import BaseConnector
from obc_connector_sdk.i_connector import IConnector, ConnectorCapability

logger = logging.getLogger(__name__)


class PubMedConnector(BaseConnector, IConnector):
    """PubMed connector implementing the IConnector interface."""

    def __init__(self):
        super().__init__(
            base_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
            rate_limit=3,  # PubMed rate limit
        )
        self.api_key = None

    @property
    def name(self) -> str:
        """Get the connector name."""
        return "pubmed"

    @property
    def capabilities(self) -> Dict[str, bool]:
        """Get the connector capabilities."""
        return {
            "supports_document_content": True,
            "supports_json_content": True,
            "supports_advanced_search": True,
            "supports_date_filtering": True,
            "requires_authentication": False,
            "supports_native_pagination": True,
            "supports_fulltext": True,
            "supports_string_content": True,
            "supports_binary_content": False
        }

    async def install(self) -> None:
        """Install connector dependencies or set up resources."""
        # PubMed doesn't require special installation
        logger.info("PubMed connector installed successfully")

    async def uninstall(self) -> None:
        """Clean up connector resources."""
        # Close HTTP client if it exists
        if hasattr(self, 'http_client') and self.http_client:
            await self.http_client.close()
        logger.info("PubMed connector uninstalled successfully")

    async def search(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """Search PubMed for papers."""
        # Validate inputs
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        if limit < 0:
            raise ValueError("Limit cannot be negative")
        
        params = {"db": "pubmed", "term": query, "retmax": limit, "retmode": "json"}

        try:
            response = await self.make_request("esearch.fcgi", params)

            # Extract paper IDs
            paper_ids = self.extract_list(response, "esearchresult.idlist")
            total_count = int(self.extract_text(response, "esearchresult.count") or 0)

            return {
                "query": query,
                "total_results": total_count,
                "document_ids": paper_ids,
                "metadata": {"db": "pubmed"},
            }
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "query": query,
                "total_results": 0,
                "document_ids": [],
                "metadata": {"db": "pubmed", "error": str(e)},
            }

    async def get_by_id(self, paper_id: str) -> Dict[str, Any]:
        """Get paper by ID."""
        # Validate inputs
        if not paper_id or not paper_id.strip():
            raise ValueError("Paper ID cannot be empty")
        
        params = {"db": "pubmed", "id": paper_id, "retmode": "xml"}

        try:
            # For XML responses, we need to handle them differently
            url = f"{self.base_url}efetch.fcgi"
            async with self.http_client.get(url, params=params) as response:
                response.raise_for_status()
                xml_content = await response.text()

            # Simple XML parsing - for now return basic info
            # TODO: Implement proper XML parsing with xml.etree.ElementTree
            return {
                "id": paper_id,
                "title": f"Paper {paper_id}",
                "abstract": "Abstract not parsed yet",
                "authors": [],
                "publication_date": None,
                "doi": None,
                "source": "pubmed",
                "xml_content": xml_content[:500] + "..." if len(xml_content) > 500 else xml_content,
            }
        except Exception as e:
            logger.error(f"Failed to get paper {paper_id}: {e}")
            return {
                "id": paper_id,
                "source": "pubmed",
                "error": str(e)
            }

    def extract_authors(self, response: Dict[str, Any]) -> List[str]:
        """Extract authors from response."""
        authors = self.extract_list(response, "PubmedArticle.Article.AuthorList.Author")
        return [
            f"{author.get('LastName', '')}, {author.get('ForeName', '')}".strip()
            for author in authors
            if author
        ]

    def extract_publication_date(self, response: Dict[str, Any]) -> Optional[str]:
        """Extract publication date from response."""
        pub_date = self.extract_text(response, "PubmedArticle.Article.Journal.JournalIssue.PubDate")
        if pub_date:
            try:
                return datetime.strptime(pub_date, "%Y %b %d").isoformat()
            except ValueError:
                return pub_date
        return None

    async def authenticate(self, config: Dict[str, Any]) -> None:
        """Configure the connector with authentication."""
        # Simple authentication - just store API key if provided
        if config.get("api_key"):
            self.api_key = config["api_key"]
            logger.info("PubMed connector configured with API key")

    async def get_updates(self, since: datetime) -> AsyncIterator[Dict[str, Any]]:
        """Get updates since a specific date."""
        # Convert date to PubMed format (YYYY/MM/DD)
        date_str = since.strftime("%Y/%m/%d")

        # Search for papers published since the date
        query = f'("{date_str}"[DP] : "3000"[DP])'
        search_result = await self.search(query, limit=1000)
        
        # Yield each document ID as a separate update
        for doc_id in search_result.get("document_ids", []):
            yield {
                "id": doc_id,
                "query": query,
                "source": "pubmed",
                "metadata": search_result.get("metadata", {})
            }
