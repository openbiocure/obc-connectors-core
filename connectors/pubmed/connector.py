"""Simple PubMed Connector Implementation."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from obc_connector_sdk.base_connector import BaseConnector

logger = logging.getLogger(__name__)


class PubMedConnector(BaseConnector):
    """Simple PubMed connector without YAML complexity."""

    def __init__(self):
        super().__init__(
            base_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
            rate_limit=3,  # PubMed rate limit
        )

    async def search(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """Search PubMed for papers."""
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
            return {"id": paper_id, "error": str(e)}

    def extract_authors(self, response: Dict[str, Any]) -> List[str]:
        """Extract authors from response."""
        authors = self.extract_list(response, "PubmedArticle.Article.AuthorList.Author")
        return [
            f"{author.get('LastName', '')} {author.get('ForeName', '')}".strip()
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

    async def get_updates(self, since: datetime) -> List[Dict[str, Any]]:
        """Get updates since a specific date."""
        # Convert date to PubMed format (YYYY/MM/DD)
        date_str = since.strftime("%Y/%m/%d")

        # Search for papers published since the date
        query = f'("{date_str}"[DP] : "3000"[DP])'
        return await self.search(query, limit=1000)
