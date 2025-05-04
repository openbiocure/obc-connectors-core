"""PubMed Connector Implementation.

This module implements the PubMed connector using the NCBI E-utilities API.
"""

import os
import logging
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional, Any, AsyncIterator
from urllib.parse import urlencode

from herpai_connector_sdk.base import BaseConnector
from herpai_connector_sdk.models import Document, Author
from herpai_connector_sdk.utils.http import HTTPClient
from herpai_connector_sdk.utils.rate_limiter import RateLimiter
from herpai_connector_sdk.exceptions import (
    AuthenticationError,
    RateLimitExceeded,
    FetchError,
    ParseError
)

logger = logging.getLogger(__name__)

class PubMedConnector(BaseConnector):
    """Connector for the PubMed/NCBI E-utilities API."""
    
    def __init__(self):
        super().__init__()
        
        # Load connector specification
        spec_path = os.path.join(os.path.dirname(__file__), "connector.yaml")
        self._spec = self.load_specification(spec_path)
        
        # Initialize HTTP client
        base_url = self._spec.get("api", {}).get("base_url", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/")
        self._http_client = HTTPClient(base_url)
        
        # Set up rate limiter based on specification
        requests_per_second = self._spec.get("api", {}).get("rate_limit", {}).get("requests_per_second", 3)
        self._rate_limiter = RateLimiter(requests_per_second)
    
    @property
    def name(self) -> str:
        """Get the connector name."""
        return "pubmed"
    
    async def install(self) -> None:
        """Install PubMed connector."""
        await super().install()
        logger.info("Installing PubMed connector...")
        # No additional installation steps needed
    
    async def uninstall(self) -> None:
        """Uninstall PubMed connector."""
        await super().uninstall()
        logger.info("Uninstalling PubMed connector...")
        if self._http_client:
            await self._http_client.close()
    
    async def authenticate(self, config: Dict[str, Any]) -> None:
        """Authenticate with the PubMed API."""
        api_key = config.get("api_key")
        
        if api_key:
            # Update rate limit if API key is provided
            requests_per_second = self._spec.get("api", {}).get("rate_limit", {}).get("with_api_key", 10)
            self._rate_limiter = RateLimiter(requests_per_second)
            
            # Store API key for later use
            self._config["api_key"] = api_key
            logger.info("PubMed connector authenticated with API key")
        else:
            logger.info("PubMed connector using unauthenticated access (lower rate limits)")
    
    async def search(self, query: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Search PubMed with the given query."""
        await self._rate_limiter.acquire()
        
        # Prepare search parameters
        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": limit or 20
        }
        
        # Add API key if available
        if self._config.get("api_key"):
            params["api_key"] = self._config["api_key"]
        
        try:
            # Perform the search
            response = await self._http_client.get("esearch.fcgi", params)
            
            # Extract document IDs
            result = response.get("esearchresult", {})
            document_ids = result.get("idlist", [])
            total_count = int(result.get("count", 0))
            
            return {
                "query": query,
                "total_results": total_count,
                "document_ids": document_ids,
                "metadata": {"db": "pubmed"}
            }
            
        except Exception as e:
            logger.error(f"Error searching PubMed: {str(e)}")
            raise
    
    async def get_by_id(self, id: str) -> Dict[str, Any]:
        """Retrieve a specific document from PubMed by ID."""
        await self._rate_limiter.acquire()
        
        # Prepare fetch parameters
        params = {
            "db": "pubmed",
            "id": id,
            "retmode": "xml"
        }
        
        # Add API key if available
        if self._config.get("api_key"):
            params["api_key"] = self._config["api_key"]
        
        try:
            # Fetch the document
            response = await self._http_client.get("efetch.fcgi", params)
            
            # Parse XML response
            root = ET.fromstring(response)
            article = root.find(".//PubmedArticle")
            
            if article is None:
                raise FetchError(id, "Document not found or invalid format")
            
            # Extract document data
            title = article.findtext(".//ArticleTitle") or "Untitled"
            abstract = article.findtext(".//AbstractText")
            
            # Extract publication date
            pub_date_elem = article.find(".//PubDate")
            if pub_date_elem is not None:
                year = pub_date_elem.findtext("Year")
                month = pub_date_elem.findtext("Month") or "1"
                day = pub_date_elem.findtext("Day") or "1"
                
                # Convert month name to number if needed
                if not month.isdigit():
                    month_map = {
                        "Jan": "1", "Feb": "2", "Mar": "3", "Apr": "4",
                        "May": "5", "Jun": "6", "Jul": "7", "Aug": "8",
                        "Sep": "9", "Oct": "10", "Nov": "11", "Dec": "12"
                    }
                    month = month_map.get(month[:3], "1")
                
                try:
                    publication_date = datetime(int(year), int(month), int(day))
                except (ValueError, TypeError):
                    publication_date = None
            else:
                publication_date = None
            
            # Extract DOI
            doi = None
            article_id_list = article.find(".//ArticleIdList")
            if article_id_list is not None:
                for article_id in article_id_list.findall("ArticleId"):
                    if article_id.get("IdType") == "doi":
                        doi = article_id.text
                        break
            
            # Extract authors
            authors = []
            author_list = article.find(".//AuthorList")
            if author_list is not None:
                for author_elem in author_list.findall("Author"):
                    last_name = author_elem.findtext("LastName") or ""
                    fore_name = author_elem.findtext("ForeName") or ""
                    initials = author_elem.findtext("Initials") or ""
                    
                    name = f"{last_name}, {fore_name}".strip()
                    if not name:
                        name = initials
                    
                    # Extract affiliation
                    affiliation = author_elem.findtext(".//Affiliation")
                    
                    authors.append(Author(
                        name=name,
                        affiliation=affiliation
                    ).__dict__)
            
            # Extract keywords
            keywords = []
            keyword_list = article.find(".//KeywordList")
            if keyword_list is not None:
                for keyword in keyword_list.findall("Keyword"):
                    if keyword.text:
                        keywords.append(keyword.text)
            
            # Create document
            document = Document(
                id=id,
                source="pubmed",
                title=title,
                abstract=abstract,
                publication_date=publication_date,
                doi=doi,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{id}/",
                authors=authors,
                keywords=keywords,
                document_type="article"
            )
            
            return document.__dict__
            
        except Exception as e:
            logger.error(f"Error fetching PubMed document {id}: {str(e)}")
            raise
    
    async def get_updates(self, since: datetime) -> AsyncIterator[Dict[str, Any]]:
        """Get updates since a specific date."""
        # Convert date to PubMed format (YYYY/MM/DD)
        date_str = since.strftime("%Y/%m/%d")
        
        # Build query for updates
        query = f"(\"0001\"[EDAT] : \"{date_str}\"[EDAT])"
        
        # Get initial search results
        search_result = await self.search(query)
        
        # Process documents in batches
        batch_size = self._config.get("batch_size", 100)
        document_ids = search_result["document_ids"]
        
        for i in range(0, len(document_ids), batch_size):
            batch = document_ids[i:i + batch_size]
            
            for doc_id in batch:
                try:
                    document = await self.get_by_id(doc_id)
                    yield document
                except Exception as e:
                    logger.error(f"Error processing document {doc_id}: {str(e)}")
                    continue 