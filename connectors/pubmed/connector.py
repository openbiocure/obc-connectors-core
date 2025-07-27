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

    async def search(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search PubMed for papers."""
        params = {"db": "pubmed", "term": query, "retmax": limit, "retmode": "json"}

        response = await self.make_request("esearch.fcgi", params)

        # Extract paper IDs
        paper_ids = self.extract_list(response, "esearchresult.idlist")

        # Get full papers
        papers = []
        for paper_id in paper_ids:
            paper = await self.get_by_id(paper_id)
            if paper:
                papers.append(paper)

        return papers

    async def get_by_id(self, paper_id: str) -> Dict[str, Any]:
        """Get paper by ID."""
        params = {"db": "pubmed", "id": paper_id, "retmode": "xml"}

        response = await self.make_request("efetch.fcgi", params)

        # Simple XML parsing (you can use xml.etree.ElementTree for more complex parsing)
        return {
            "id": paper_id,
            "title": self.extract_text(response, "PubmedArticle.Article.ArticleTitle"),
            "abstract": self.extract_text(response, "PubmedArticle.Article.Abstract.AbstractText"),
            "authors": self.extract_authors(response),
            "publication_date": self.extract_publication_date(response),
            "doi": self.extract_text(response, "PubmedArticle.Article.ELocationID"),
            "source": "pubmed",
        }

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
