"""Simple tests for OpenAlex Connector implementation."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from connectors.openalex.connector import OpenAlexConnector


class TestOpenAlexConnectorSimple:
    """Simple test cases for OpenAlex Connector implementation."""

    def test_connector_initialization(self):
        """Test OpenAlex connector initialization."""
        connector = OpenAlexConnector()
        assert connector.base_url == "https://api.openalex.org/"
        assert connector.rate_limit == 10
        assert connector.email is None

    @pytest.mark.asyncio
    async def test_search_with_mock(self):
        """Test OpenAlex search with mocked response."""
        connector = OpenAlexConnector()

        mock_response = {
            "results": [
                {
                    "id": "https://openalex.org/W1234567890",
                    "title": "Test Paper",
                    "abstract_inverted_index": {"test": [0], "paper": [1]},
                    "authorships": [{"author": {"display_name": "Test Author"}}],
                    "publication_date": "2023-01-01",
                    "doi": "https://doi.org/10.1000/test",
                    "type": "journal-article",
                    "language": "en",
                    "open_access": {"is_oa": True, "oa_url": "https://example.com/paper"},
                    "cited_by_count": 5,
                    "concepts": [{"display_name": "Machine Learning", "score": 0.8}]
                }
            ]
        }

        with patch.object(connector, 'make_request', return_value=mock_response):
            result = await connector.search("test query", limit=1)

            assert isinstance(result, dict)
            assert result["query"] == "test query"
            assert result["total_results"] == 1
            assert len(result["document_ids"]) == 1

    @pytest.mark.asyncio
    async def test_search_with_error(self):
        """Test OpenAlex search with error."""
        connector = OpenAlexConnector()

        with patch.object(connector, 'make_request', side_effect=Exception("API Error")):
            result = await connector.search("test", limit=10)
            assert result["total_results"] == 0
            assert "error" in result["metadata"]

    @pytest.mark.asyncio
    async def test_get_by_id_with_mock(self):
        """Test OpenAlex get_by_id with mocked response."""
        connector = OpenAlexConnector()

        mock_response = {
            "id": "https://openalex.org/W1234567890",
            "title": "Test Paper",
            "abstract_inverted_index": {"test": [0], "paper": [1]},
            "authorships": [{"author": {"display_name": "Test Author"}}],
            "publication_date": "2023-01-01",
            "doi": "https://doi.org/10.1000/test",
            "type": "journal-article",
            "language": "en",
            "open_access": {"is_oa": True, "oa_url": "https://example.com/paper"},
            "cited_by_count": 5,
            "concepts": [{"display_name": "Machine Learning", "score": 0.8}]
        }

        with patch.object(connector, 'make_request', return_value=mock_response):
            result = await connector.get_by_id("W1234567890")

            assert result["id"] == "W1234567890"
            assert result["title"] == "Test Paper"
            assert result["source"] == "openalex"

    @pytest.mark.asyncio
    async def test_get_by_id_with_error(self):
        """Test OpenAlex get_by_id with error."""
        connector = OpenAlexConnector()

        with patch.object(connector, 'make_request', side_effect=Exception("API Error")):
            result = await connector.get_by_id("W1234567890")
            assert result["id"] == "W1234567890"
            assert result["source"] == "openalex"
            assert "error" in result

    def test_extract_abstract(self):
        """Test OpenAlex abstract extraction."""
        connector = OpenAlexConnector()

        work_data = {
            "abstract_inverted_index": {
                "This": [0],
                "is": [1],
                "a": [2],
                "test": [3],
                "abstract": [4]
            }
        }

        abstract = connector._extract_abstract(work_data)
        assert abstract == "This is a test abstract"

    def test_extract_abstract_missing(self):
        """Test OpenAlex abstract extraction with missing data."""
        connector = OpenAlexConnector()

        work_data = {}
        abstract = connector._extract_abstract(work_data)
        assert abstract is None

    def test_extract_authors(self):
        """Test OpenAlex author extraction."""
        connector = OpenAlexConnector()

        work_data = {
            "authorships": [
                {
                    "author": {
                        "display_name": "John Doe",
                        "orcid": "https://orcid.org/0000-0000-0000-0000"
                    },
                    "institutions": [
                        {
                            "institution": {
                                "display_name": "Test University"
                            }
                        }
                    ],
                    "author_position": 1
                }
            ]
        }

        authors = connector._extract_authors(work_data)
        assert len(authors) == 1
        assert authors[0]["name"] == "John Doe"
        assert authors[0]["orcid"] == "https://orcid.org/0000-0000-0000-0000"
        assert authors[0]["affiliation"] == "Test University"
        assert authors[0]["position"] == 1

    def test_extract_publication_date(self):
        """Test OpenAlex publication date extraction."""
        connector = OpenAlexConnector()

        work_data = {"publication_date": "2023-01-15"}
        pub_date = connector._extract_publication_date(work_data)
        assert pub_date == datetime(2023, 1, 15)

    def test_extract_publication_date_missing(self):
        """Test OpenAlex publication date extraction with missing data."""
        connector = OpenAlexConnector()

        work_data = {}
        pub_date = connector._extract_publication_date(work_data)
        assert pub_date is None

    def test_extract_doi(self):
        """Test OpenAlex DOI extraction."""
        connector = OpenAlexConnector()

        work_data = {"doi": "https://doi.org/10.1000/test"}
        doi = connector._extract_doi(work_data)
        assert doi == "10.1000/test"

    def test_extract_doi_missing(self):
        """Test OpenAlex DOI extraction with missing data."""
        connector = OpenAlexConnector()

        work_data = {}
        doi = connector._extract_doi(work_data)
        assert doi is None

    def test_extract_concepts(self):
        """Test OpenAlex concept extraction."""
        connector = OpenAlexConnector()

        work_data = {
            "concepts": [
                {
                    "id": "https://openalex.org/C1234567890",
                    "display_name": "Machine Learning",
                    "score": 0.8,
                    "level": 2
                }
            ]
        }

        concepts = connector._extract_concepts(work_data)
        assert len(concepts) == 1
        assert concepts[0]["display_name"] == "Machine Learning"
        assert concepts[0]["score"] == 0.8
        assert concepts[0]["level"] == 2

    def test_extract_keywords(self):
        """Test OpenAlex keyword extraction."""
        connector = OpenAlexConnector()

        work_data = {
            "concepts": [
                {"display_name": "Machine Learning"},
                {"display_name": "Artificial Intelligence"},
                {"display_name": "Deep Learning"}
            ]
        }

        keywords = connector._extract_keywords(work_data)
        assert len(keywords) == 3
        assert "Machine Learning" in keywords
        assert "Artificial Intelligence" in keywords
        assert "Deep Learning" in keywords

    @pytest.mark.asyncio
    async def test_authenticate(self):
        """Test OpenAlex authentication."""
        connector = OpenAlexConnector()

        config = {"email": "test@example.com"}
        await connector.authenticate(config)
        assert connector.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_authenticate_without_email(self):
        """Test OpenAlex authentication without email."""
        connector = OpenAlexConnector()

        config = {}
        await connector.authenticate(config)
        assert connector.email is None

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test OpenAlex connector as context manager."""
        connector = OpenAlexConnector()

        async with connector:
            assert connector is not None

    @pytest.mark.asyncio
    async def test_close(self):
        """Test OpenAlex connector close method."""
        connector = OpenAlexConnector()

        await connector.close()

    @pytest.mark.asyncio
    async def test_search_real(self):
        """Test OpenAlex search with real API (if network available)."""
        connector = OpenAlexConnector()

        try:
            result = await connector.search("machine learning", limit=5)
            assert isinstance(result, dict)
            assert "query" in result
            assert "total_results" in result
            assert "document_ids" in result
        except Exception as e:
            pytest.skip(f"Network test skipped: {e}")

    @pytest.mark.asyncio
    async def test_get_by_id_real(self):
        """Test OpenAlex get_by_id with real API (if network available)."""
        connector = OpenAlexConnector()

        try:
            # Use a known OpenAlex work ID
            result = await connector.get_by_id("W2755950973")  # Example ID
            assert isinstance(result, dict)
            assert "id" in result
            assert "source" in result
            assert result["source"] == "openalex"
        except Exception as e:
            pytest.skip(f"Network test skipped: {e}")
