"""OpenAlex Connector Implementation."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
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

    async def search(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:

        """Search OpenAlex for works (papers)."""
        # URL encode the query
        encoded_query = quote(query)

        all_works: List[Dict[str, Any]] = []
        page = 1
        per_page = min(200, limit)  # OpenAlex max per page is 200

        try:
            while len(all_works) < limit:
                # Calculate how many results we need for this page
                remaining = limit - len(all_works)
                current_per_page = min(per_page, remaining)

                # Build search parameters
                params = {
                    "search": encoded_query,
                    "per-page": current_per_page,
                    "page": page,
                }

                # Add email if available for better rate limits
                if self.email:
                    params["mailto"] = self.email

                response = await self.make_request("works", params)
                works = response.get("results", [])

                if not works:  # No more results
                    break

                # Process works and add to results
                for work in works:
                    if len(all_works) >= limit:
                        break

                    work_id = work.get("id", "").split("/")[-1] if work.get("id") else ""
                    if work_id:
                        all_works.append({
                            "id": work_id,
                            "title": work.get("title", "Untitled"),
                            "abstract": self._extract_abstract(work),
                            "authors": self._extract_authors(work),
                            "publication_date": self._extract_publication_date(work),
                            "doi": self._extract_doi(work),
                            "url": work.get("id", ""),
                            "source": "openalex",
                            "metadata": {
                                "type": work.get("type", ""),
                                "language": work.get("language", ""),
                                "is_oa": work.get("open_access", {}).get("is_oa", False) if work.get("open_access") else False,
                                "oa_url": work.get("open_access", {}).get("oa_url", "") if work.get("open_access") else "",
                                "cited_by_count": work.get("cited_by_count", 0),
                                "concepts": self._extract_concepts(work),
                                "keywords": self._extract_keywords(work),
                            }
                        })

                page += 1

                # Safety check to prevent infinite loops
                if page > 50:  # Max 50 pages (10,000 results)
                    logger.warning(f"Reached maximum page limit for query: {query}")
                    break

            return all_works

        except Exception as e:
            logger.error(f"OpenAlex search failed: {e}")
            return []

    async def get_by_id(self, doc_id: str) -> Dict[str, Any]:
        """Get a work by OpenAlex ID."""
        # OpenAlex IDs can be full URLs or just the ID part
        if doc_id.startswith("https://openalex.org/"):
            doc_id = doc_id.split("/")[-1]

        params: Dict[str, Any] = {}
        if self.email:
            params["mailto"] = self.email

        try:
            response = await self.make_request(f"works/{doc_id}", params)

            if not response:
                return {"id": doc_id, "error": "No response from API", "source": "openalex"}

            # Extract work details
            title = response.get("title", "Untitled")
            abstract = self._extract_abstract(response)
            authors = self._extract_authors(response)
            publication_date = self._extract_publication_date(response)
            doi = self._extract_doi(response)
            url = response.get("id", "")

            return {
                "id": doc_id,
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
            logger.error(f"Failed to get OpenAlex work {doc_id}: {e}")
            return {"id": doc_id, "error": str(e), "source": "openalex"}

    def _extract_abstract(self, work: Dict[str, Any]) -> Optional[str]:
        """Extract abstract from work data."""
        # OpenAlex abstracts are in the abstract_inverted_index format
        abstract_inverted = work.get("abstract_inverted_index")
        if not abstract_inverted:
            return None

        try:
            # Convert inverted index to plain text
            # This is a simplified version - in practice you'd want more sophisticated reconstruction
            words: List[Tuple[int, str]] = []
            for word, positions in abstract_inverted.items():
                if isinstance(positions, list) and isinstance(word, str):
                    for pos in positions:  # type: ignore
                        if isinstance(pos, int):
                            words.append((int(pos), str(word)))

            # Sort by position and join
            words.sort(key=lambda x: x[0])
            return " ".join([word for _, word in words])
        except Exception as e:
            logger.warning(f"Error extracting abstract: {e}")
            return None

    def _extract_authors(self, work: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract authors from work data."""
        authors: List[Dict[str, Any]] = []
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
        concepts: List[Dict[str, Any]] = []
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

    async def search_by_author(self, author_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search for works by a specific author."""
        # URL encode the author name
        encoded_author = quote(author_name)

        all_works: List[Dict[str, Any]] = []
        page = 1
        per_page = min(200, limit)  # OpenAlex max per page is 200

        try:
            while len(all_works) < limit:
                # Calculate how many results we need for this page
                remaining = limit - len(all_works)
                current_per_page = min(per_page, remaining)

                params = {
                    "filter": f"author.display_name:{encoded_author}",
                    "per-page": current_per_page,
                    "page": page,
                }

                if self.email:
                    params["mailto"] = self.email

                response = await self.make_request("works", params)
                works = response.get("results", [])

                if not works:  # No more results
                    break

                # Process works and add to results
                for work in works:
                    if len(all_works) >= limit:
                        break

                    work_id = work.get("id", "").split("/")[-1] if work.get("id") else ""
                    if work_id:
                        all_works.append({
                            "id": work_id,
                            "title": work.get("title", "Untitled"),
                            "abstract": self._extract_abstract(work),
                            "authors": self._extract_authors(work),
                            "publication_date": self._extract_publication_date(work),
                            "doi": self._extract_doi(work),
                            "url": work.get("id", ""),
                            "source": "openalex",
                            "metadata": {
                                "type": work.get("type", ""),
                                "language": work.get("language", ""),
                                "is_oa": work.get("open_access", {}).get("is_oa", False) if work.get("open_access") else False,
                                "oa_url": work.get("open_access", {}).get("oa_url", "") if work.get("open_access") else "",
                                "cited_by_count": work.get("cited_by_count", 0),
                                "concepts": self._extract_concepts(work),
                                "keywords": self._extract_keywords(work),
                                "search_type": "author",
                                "author_name": author_name,
                            }
                        })

                page += 1

                # Safety check to prevent infinite loops
                if page > 50:  # Max 50 pages (10,000 results)
                    logger.warning(f"Reached maximum page limit for author search: {author_name}")
                    break

            return all_works

        except Exception as e:
            logger.error(f"OpenAlex author search failed: {e}")
            return []

    async def search_by_institution(self, institution_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search for works from a specific institution."""
        encoded_institution = quote(institution_name)

        all_works: List[Dict[str, Any]] = []
        page = 1
        per_page = min(200, limit)  # OpenAlex max per page is 200

        try:
            while len(all_works) < limit:
                # Calculate how many results we need for this page
                remaining = limit - len(all_works)
                current_per_page = min(per_page, remaining)

                params = {
                    "filter": f"institutions.display_name:{encoded_institution}",
                    "per-page": current_per_page,
                    "page": page,
                }

                if self.email:
                    params["mailto"] = self.email

                response = await self.make_request("works", params)
                works = response.get("results", [])

                if not works:  # No more results
                    break

                # Process works and add to results
                for work in works:
                    if len(all_works) >= limit:
                        break

                    work_id = work.get("id", "").split("/")[-1] if work.get("id") else ""
                    if work_id:
                        all_works.append({
                            "id": work_id,
                            "title": work.get("title", "Untitled"),
                            "abstract": self._extract_abstract(work),
                            "authors": self._extract_authors(work),
                            "publication_date": self._extract_publication_date(work),
                            "doi": self._extract_doi(work),
                            "url": work.get("id", ""),
                            "source": "openalex",
                            "metadata": {
                                "type": work.get("type", ""),
                                "language": work.get("language", ""),
                                "is_oa": work.get("open_access", {}).get("is_oa", False) if work.get("open_access") else False,
                                "oa_url": work.get("open_access", {}).get("oa_url", "") if work.get("open_access") else "",
                                "cited_by_count": work.get("cited_by_count", 0),
                                "concepts": self._extract_concepts(work),
                                "keywords": self._extract_keywords(work),
                                "search_type": "institution",
                                "institution_name": institution_name,
                            }
                        })

                page += 1

                # Safety check to prevent infinite loops
                if page > 50:  # Max 50 pages (10,000 results)
                    logger.warning(f"Reached maximum page limit for institution search: {institution_name}")
                    break

            return all_works

        except Exception as e:
            logger.error(f"OpenAlex institution search failed: {e}")
            return []
