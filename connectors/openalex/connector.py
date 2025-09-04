"""OpenAlex Connector Implementation."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from obc_connector_sdk.base_connector import BaseConnector

logger = logging.getLogger(__name__)


class OpenAlexConnector(BaseConnector):
    """OpenAlex connector for academic literature and research data."""

    def __init__(self):
        super().__init__(
            base_url="https://api.openalex.org/",
            rate_limit=10,  # OpenAlex rate limit (100k requests per day)
        )
        self.email = None  # Optional email for better rate limits

    async def search(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """Search OpenAlex for works (papers)."""
        # URL encode the query
        encoded_query = quote(query)

        # Build search parameters
        params = {
            "search": encoded_query,
            "per-page": min(limit, 200),  # OpenAlex max per page is 200
            "page": 1,
        }

        # Add email if available for better rate limits
        if self.email:
            params["mailto"] = self.email

        try:
            response = await self.make_request("works", params)

            # Extract work IDs and metadata
            works = response.get("results", [])
            work_ids = [work.get("id", "").split("/")[-1] for work in works if work.get("id")]
            total_count = response.get("meta", {}).get("count", 0)

            return {
                "query": query,
                "total_results": total_count,
                "document_ids": work_ids,
                "metadata": {
                    "source": "openalex",
                    "page": 1,
                    "per_page": params["per-page"],
                    "results_returned": len(work_ids)
                },
            }
        except Exception as e:
            logger.error(f"OpenAlex search failed: {e}")
            return {
                "query": query,
                "total_results": 0,
                "document_ids": [],
                "metadata": {"source": "openalex", "error": str(e)},
            }

    async def get_by_id(self, work_id: str) -> Dict[str, Any]:
        """Get a work by OpenAlex ID."""
        # OpenAlex IDs can be full URLs or just the ID part
        if work_id.startswith("https://openalex.org/"):
            work_id = work_id.split("/")[-1]

        params = {}
        if self.email:
            params["mailto"] = self.email

        try:
            response = await self.make_request(f"works/{work_id}", params)

            if not response:
                return {"id": work_id, "error": "No response from API", "source": "openalex"}

            # Extract work details
            title = response.get("title", "Untitled")
            abstract = self._extract_abstract(response)
            authors = self._extract_authors(response)
            publication_date = self._extract_publication_date(response)
            doi = self._extract_doi(response)
            url = response.get("id", "")

            return {
                "id": work_id,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "publication_date": publication_date,
                "doi": doi,
                "url": url,
                "source": "openalex",
                "metadata": {
                    "type": response.get("type", ""),
                    "language": response.get("language", ""),
                    "is_oa": response.get("open_access", {}).get("is_oa", False) if response.get("open_access") else False,
                    "oa_url": response.get("open_access", {}).get("oa_url", "") if response.get("open_access") else "",
                    "cited_by_count": response.get("cited_by_count", 0),
                    "concepts": self._extract_concepts(response),
                    "keywords": self._extract_keywords(response),
                }
            }
        except Exception as e:
            logger.error(f"Failed to get OpenAlex work {work_id}: {e}")
            return {"id": work_id, "error": str(e), "source": "openalex"}

    def _extract_abstract(self, work: Dict[str, Any]) -> Optional[str]:
        """Extract abstract from work data."""
        # OpenAlex abstracts are in the abstract_inverted_index format
        abstract_inverted = work.get("abstract_inverted_index")
        if not abstract_inverted:
            return None

        try:
            # Convert inverted index to plain text
            # This is a simplified version - in practice you'd want more sophisticated reconstruction
            words = []
            for word, positions in abstract_inverted.items():
                if isinstance(positions, list):
                    for pos in positions:
                        words.append((pos, word))

            # Sort by position and join
            words.sort(key=lambda x: x[0])
            return " ".join([word for _, word in words])
        except Exception as e:
            logger.warning(f"Error extracting abstract: {e}")
            return None

    def _extract_authors(self, work: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract authors from work data."""
        authors = []
        authorships = work.get("authorships", [])

        for authorship in authorships:
            author = authorship.get("author", {})
            if author:
                author_name = author.get("display_name", "")
                orcid = author.get("orcid", "")
                affiliation = None

                # Get primary affiliation
                institutions = authorship.get("institutions", [])
                if institutions:
                    primary_institution = institutions[0].get("institution", {})
                    affiliation = primary_institution.get("display_name", "")

                authors.append({
                    "name": author_name,
                    "orcid": orcid,
                    "affiliation": affiliation,
                    "position": authorship.get("author_position", 0)
                })

        return authors

    def _extract_publication_date(self, work: Dict[str, Any]) -> Optional[datetime]:
        """Extract publication date from work data."""
        pub_date = work.get("publication_date")
        if not pub_date:
            return None

        try:
            # OpenAlex dates are in YYYY-MM-DD format
            return datetime.strptime(pub_date, "%Y-%m-%d")
        except ValueError:
            try:
                # Try YYYY-MM format
                return datetime.strptime(pub_date, "%Y-%m")
            except ValueError:
                try:
                    # Try YYYY format
                    return datetime.strptime(pub_date, "%Y")
                except ValueError:
                    logger.warning(f"Could not parse date: {pub_date}")
                    return None

    def _extract_doi(self, work: Dict[str, Any]) -> Optional[str]:
        """Extract DOI from work data."""
        doi = work.get("doi")
        if doi:
            # Remove https://doi.org/ prefix if present
            if doi.startswith("https://doi.org/"):
                return doi.replace("https://doi.org/", "")
            return doi
        return None

    def _extract_concepts(self, work: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract concepts from work data."""
        concepts = []
        for concept in work.get("concepts", []):
            concepts.append({
                "id": concept.get("id", ""),
                "display_name": concept.get("display_name", ""),
                "score": concept.get("score", 0.0),
                "level": concept.get("level", 0)
            })
        return concepts

    def _extract_keywords(self, work: Dict[str, Any]) -> List[str]:
        """Extract keywords from work data."""
        # OpenAlex doesn't have traditional keywords, but we can use concept names
        concepts = work.get("concepts", [])
        return [concept.get("display_name", "") for concept in concepts[:10]]  # Top 10 concepts

    async def authenticate(self, config: Dict[str, Any]) -> None:
        """Configure the connector with authentication."""
        # OpenAlex doesn't require authentication, but email improves rate limits
        if config.get("email"):
            self.email = config["email"]
            logger.info("OpenAlex connector configured with email for better rate limits")
        elif config.get("api_key"):
            # Some users might pass api_key thinking it's required
            logger.info("OpenAlex connector doesn't require API key, but email is recommended")

    async def get_updates(self, since: datetime) -> List[Dict[str, Any]]:
        """Get updates since a specific date."""
        # Convert date to OpenAlex format (YYYY-MM-DD)
        date_str = since.strftime("%Y-%m-%d")

        # Search for works published since the date
        query = f"from_publication_date:{date_str}"
        return await self.search(query, limit=1000)

    async def search_by_author(self, author_name: str, limit: int = 100) -> Dict[str, Any]:
        """Search for works by a specific author."""
        # URL encode the author name
        encoded_author = quote(author_name)

        params = {
            "filter": f"author.display_name:{encoded_author}",
            "per-page": min(limit, 200),
            "page": 1,
        }

        if self.email:
            params["mailto"] = self.email

        try:
            response = await self.make_request("works", params)

            works = response.get("results", [])
            work_ids = [work.get("id", "").split("/")[-1] for work in works if work.get("id")]
            total_count = response.get("meta", {}).get("count", 0)

            return {
                "query": f"author:{author_name}",
                "total_results": total_count,
                "document_ids": work_ids,
                "metadata": {
                    "source": "openalex",
                    "search_type": "author",
                    "author_name": author_name,
                    "results_returned": len(work_ids)
                },
            }
        except Exception as e:
            logger.error(f"OpenAlex author search failed: {e}")
            return {
                "query": f"author:{author_name}",
                "total_results": 0,
                "document_ids": [],
                "metadata": {"source": "openalex", "error": str(e)},
            }

    async def search_by_institution(self, institution_name: str, limit: int = 100) -> Dict[str, Any]:
        """Search for works from a specific institution."""
        encoded_institution = quote(institution_name)

        params = {
            "filter": f"institutions.display_name:{encoded_institution}",
            "per-page": min(limit, 200),
            "page": 1,
        }

        if self.email:
            params["mailto"] = self.email

        try:
            response = await self.make_request("works", params)

            works = response.get("results", [])
            work_ids = [work.get("id", "").split("/")[-1] for work in works if work.get("id")]
            total_count = response.get("meta", {}).get("count", 0)

            return {
                "query": f"institution:{institution_name}",
                "total_results": total_count,
                "document_ids": work_ids,
                "metadata": {
                    "source": "openalex",
                    "search_type": "institution",
                    "institution_name": institution_name,
                    "results_returned": len(work_ids)
                },
            }
        except Exception as e:
            logger.error(f"OpenAlex institution search failed: {e}")
            return {
                "query": f"institution:{institution_name}",
                "total_results": 0,
                "document_ids": [],
                "metadata": {"source": "openalex", "error": str(e)},
            }
