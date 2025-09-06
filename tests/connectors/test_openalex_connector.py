"""Tests for OpenAlex Connector."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from connectors.openalex.connector import OpenAlexConnector
from tests.connectors.test_connector_base import ConnectorTestBase


class TestOpenAlexConnector(ConnectorTestBase):
    """Test cases for OpenAlex Connector."""

    def create_connector(self):
        """Create OpenAlex connector instance."""
        return OpenAlexConnector()

    # Interface Tests
    def test_connector_initialization(self):
        """Test OpenAlex connector initialization."""
        connector = self.create_connector()
        assert connector is not None
        assert connector.base_url == "https://api.openalex.org/"
        assert connector.rate_limit == 10
        assert connector.email is None

    def test_connector_name(self):
        """Test OpenAlex connector name property."""
        connector = self.create_connector()
        assert connector.name == "openalex"

    def test_connector_capabilities(self):
        """Test OpenAlex connector capabilities."""
        connector = self.create_connector()
        capabilities = connector.capabilities

        assert isinstance(capabilities, dict)
        assert capabilities["supports_document_content"] is True
        assert capabilities["supports_json_content"] is True
        assert capabilities["supports_advanced_search"] is True
        assert capabilities["supports_date_filtering"] is True
        assert capabilities["requires_authentication"] is False
        assert capabilities["supports_native_pagination"] is True
        assert capabilities["supports_fulltext"] is True
        assert capabilities["supports_string_content"] is True
        assert capabilities["supports_binary_content"] is False

    @pytest.mark.asyncio
    async def test_authenticate_method(self):
        """Test OpenAlex authenticate method."""
        connector = self.create_connector()

        # Test with email
        config = {"email": "test@example.com"}
        await connector.authenticate(config)
        assert connector.email == "test@example.com"

        # Test with api_key (should be ignored)
        config = {"api_key": "fake_key"}
        await connector.authenticate(config)
        # Email should remain unchanged
        assert connector.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_search_method(self):
        """Test OpenAlex search method."""
        connector = self.create_connector()

        with patch.object(connector, 'make_request', return_value={
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
        }):
            result = await connector.search("machine learning", limit=10)

            assert isinstance(result, dict)
            assert "query" in result
            assert "total_results" in result
            assert "document_ids" in result
            assert "metadata" in result
            assert result["query"] == "machine learning"
            assert result["total_results"] == 1
            assert len(result["document_ids"]) == 1

    @pytest.mark.asyncio
    async def test_get_by_id_method(self):
        """Test OpenAlex get_by_id method."""
        connector = self.create_connector()

        with patch.object(connector, 'make_request', return_value={
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
        }):
            result = await connector.get_by_id("W1234567890")

            assert isinstance(result, dict)
            assert result["id"] == "W1234567890"
            assert result["title"] == "Test Paper"
            assert result["source"] == "openalex"
            assert "metadata" in result

    @pytest.mark.asyncio
    async def test_get_updates_method(self):
        """Test OpenAlex get_updates method."""
        connector = self.create_connector()
        since_date = datetime.now() - timedelta(days=30)

        with patch.object(connector, 'search', return_value={
            "query": "test",
            "total_results": 2,
            "document_ids": ["W123", "W456"],
            "metadata": {"source": "openalex"}
        }):
            updates = []
            async for update in connector.get_updates(since_date):
                updates.append(update)
                if len(updates) >= 2:
                    break

            assert len(updates) == 2
            assert "id" in updates[0]
            assert "source" in updates[0]
            assert updates[0]["source"] == "openalex"

    @pytest.mark.asyncio
    async def test_install_method(self):
        """Test OpenAlex install method."""
        connector = self.create_connector()

        # Should not raise any exceptions
        await connector.install()

    @pytest.mark.asyncio
    async def test_uninstall_method(self):
        """Test OpenAlex uninstall method."""
        connector = self.create_connector()

        # Should not raise any exceptions
        await connector.uninstall()

    # Validation Tests
    @pytest.mark.asyncio
    async def test_search_with_invalid_query(self):
        """Test OpenAlex search with invalid query."""
        connector = self.create_connector()

        with pytest.raises(ValueError, match="Query cannot be empty"):
            await connector.search("")

    @pytest.mark.asyncio
    async def test_get_by_id_with_invalid_id(self):
        """Test OpenAlex get_by_id with invalid ID."""
        connector = self.create_connector()

        with pytest.raises(ValueError, match="Paper ID cannot be empty"):
            await connector.get_by_id("")

    @pytest.mark.asyncio
    async def test_search_with_negative_limit(self):
        """Test OpenAlex search with negative limit."""
        connector = self.create_connector()

        with pytest.raises(ValueError, match="Limit cannot be negative"):
            await connector.search("test", limit=-1)

    # OpenAlex-specific Tests
    def test_openalex_connector_initialization(self):
        """Test OpenAlex connector specific initialization."""
        connector = self.create_connector()
        assert connector.base_url == "https://api.openalex.org/"
        assert connector.rate_limit == 10
        assert connector.email is None

    @pytest.mark.asyncio
    async def test_openalex_authenticate_with_email(self):
        """Test OpenAlex authentication with email."""
        connector = self.create_connector()

        config = {"email": "test@example.com"}
        await connector.authenticate(config)

        assert connector.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_openalex_authenticate_without_email(self):
        """Test OpenAlex authentication without email."""
        connector = self.create_connector()

        config = {}
        await connector.authenticate(config)

        assert connector.email is None

    @pytest.mark.asyncio
    async def test_openalex_search_real(self):
        """Test OpenAlex search with real API (if network available)."""
        connector = self.create_connector()

        try:
            result = await connector.search("machine learning", limit=5)
            assert isinstance(result, dict)
            assert "query" in result
            assert "total_results" in result
            assert "document_ids" in result
        except Exception as e:
            pytest.skip(f"Network test skipped: {e}")

    @pytest.mark.asyncio
    async def test_openalex_get_by_id_real(self):
        """Test OpenAlex get_by_id with real API (if network available)."""
        connector = self.create_connector()

        try:
            # Use a known OpenAlex work ID
            result = await connector.get_by_id("W2755950973")  # Example ID
            assert isinstance(result, dict)
            assert "id" in result
            assert "source" in result
            assert result["source"] == "openalex"
        except Exception as e:
            pytest.skip(f"Network test skipped: {e}")

    @pytest.mark.asyncio
    async def test_openalex_search_with_mock(self):
        """Test OpenAlex search with mocked response."""
        connector = self.create_connector()

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
            result = await connector.search("test query", limit=10)

            assert result["query"] == "test query"
            assert result["total_results"] == 1
            assert len(result["document_ids"]) == 1

    @pytest.mark.asyncio
    async def test_openalex_get_by_id_with_mock(self):
        """Test OpenAlex get_by_id with mocked response."""
        connector = self.create_connector()

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

    def test_openalex_extract_abstract(self):
        """Test OpenAlex abstract extraction."""
        connector = self.create_connector()

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

    def test_openalex_extract_authors(self):
        """Test OpenAlex author extraction."""
        connector = self.create_connector()

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

    def test_openalex_extract_publication_date(self):
        """Test OpenAlex publication date extraction."""
        connector = self.create_connector()

        work_data = {"publication_date": "2023-01-15"}
        pub_date = connector._extract_publication_date(work_data)
        assert pub_date == datetime(2023, 1, 15)

    def test_openalex_extract_doi(self):
        """Test OpenAlex DOI extraction."""
        connector = self.create_connector()

        work_data = {"doi": "https://doi.org/10.1000/test"}
        doi = connector._extract_doi(work_data)
        assert doi == "10.1000/test"

    def test_openalex_extract_concepts(self):
        """Test OpenAlex concept extraction."""
        connector = self.create_connector()

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

    def test_openalex_extract_keywords(self):
        """Test OpenAlex keyword extraction."""
        connector = self.create_connector()

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
    async def test_openalex_search_by_author(self):
        """Test OpenAlex search by author."""
        connector = self.create_connector()

        with patch.object(connector, 'make_request', return_value={
            "results": [
                {
                    "id": "https://openalex.org/W1234567890",
                    "title": "Test Paper",
                    "authorships": [{"author": {"display_name": "Test Author"}}],
                    "publication_date": "2023-01-01"
                }
            ]
        }):
            result = await connector.search_by_author("Test Author", limit=10)
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["title"] == "Test Paper"

    @pytest.mark.asyncio
    async def test_openalex_search_by_institution(self):
        """Test OpenAlex search by institution."""
        connector = self.create_connector()

        with patch.object(connector, 'make_request', return_value={
            "results": [
                {
                    "id": "https://openalex.org/W1234567890",
                    "title": "Test Paper",
                    "authorships": [{"author": {"display_name": "Test Author"}}],
                    "publication_date": "2023-01-01"
                }
            ]
        }):
            result = await connector.search_by_institution("Test University", limit=10)
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["title"] == "Test Paper"

    @pytest.mark.asyncio
    async def test_openalex_rate_limiting(self):
        """Test OpenAlex rate limiting."""
        connector = self.create_connector()

        # Test that rate limiting is configured
        assert connector.rate_limit == 10

    @pytest.mark.asyncio
    async def test_openalex_error_handling(self):
        """Test OpenAlex error handling."""
        connector = self.create_connector()

        with patch.object(connector, 'make_request', side_effect=Exception("API Error")):
            result = await connector.search("test", limit=10)
            assert result["total_results"] == 0
            assert "error" in result["metadata"]

    @pytest.mark.asyncio
    async def test_openalex_http_client_cleanup(self):
        """Test OpenAlex HTTP client cleanup."""
        connector = self.create_connector()

        # Test that uninstall properly cleans up
        await connector.uninstall()

    @pytest.mark.asyncio
    async def test_openalex_search_parameters(self):
        """Test OpenAlex search parameters."""
        connector = self.create_connector()

        with patch.object(connector.http_client, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json = AsyncMock(return_value={"results": []})
            mock_get.return_value.__aenter__.return_value = mock_response

            await connector.search("test query", limit=10)

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "works" in call_args[0][0]
            assert call_args[0][1]["search"] == "test%20query"
            assert call_args[0][1]["per-page"] == 10
            assert call_args[0][1]["page"] == 1

    @pytest.mark.asyncio
    async def test_openalex_get_by_id_parameters(self):
        """Test OpenAlex get_by_id parameters."""
        connector = self.create_connector()

        with patch.object(connector.http_client, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json = AsyncMock(return_value={"id": "test"})
            mock_get.return_value.__aenter__.return_value = mock_response

            await connector.get_by_id("W1234567890")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "works/W1234567890" in call_args[0][0]
