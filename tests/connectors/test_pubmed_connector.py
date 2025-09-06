"""Tests for PubMed connector."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from obc_connector_sdk.utils.connector_loader import ConnectorLoader
from tests.connectors.test_connector_base import ConnectorTestBase


class TestPubMedConnector(ConnectorTestBase):
    """Test cases for PubMed connector."""

    def get_connector_class(self):
        """Return the PubMed connector class."""
        from connectors.pubmed.connector import PubMedConnector
        return PubMedConnector

    def get_connector_name(self):
        """Return the PubMed connector name."""
        return "pubmed"

    def get_valid_queries(self):
        """Return valid test queries for PubMed."""
        return [
            "machine learning",
            "cancer treatment",
            "COVID-19 vaccine",
            "artificial intelligence medical",
            "herpes simplex virus"
        ]

    def get_valid_doc_ids(self):
        """Return valid document IDs for testing."""
        return [
            "40910727",
            "40909445",
            "40908922"
        ]

    def get_expected_capabilities(self):
        """Return expected capabilities for PubMed connector."""
        return {
            "supports_document_content": True,
            "supports_json_content": True,
            "supports_advanced_search": True,
            "supports_date_filtering": True,
            "requires_authentication": False,
            "supports_native_pagination": True
        }

    @pytest.mark.asyncio
    async def test_pubmed_connector_initialization(self):
        """Test PubMed connector initialization."""
        connector = self.create_connector()
        assert connector.name == "pubmed"
        assert connector.base_url == "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        assert connector.rate_limit == 3

    @pytest.mark.asyncio
    async def test_pubmed_authenticate_with_api_key(self):
        """Test PubMed authentication with API key."""
        connector = self.create_connector()
        config = {"api_key": "test_api_key"}
        
        await connector.authenticate(config)
        assert hasattr(connector, 'api_key')
        assert connector.api_key == "test_api_key"

    @pytest.mark.asyncio
    async def test_pubmed_authenticate_without_api_key(self):
        """Test PubMed authentication without API key."""
        connector = self.create_connector()
        config = {}
        
        await connector.authenticate(config)
        # Should not raise an exception

    @pytest.mark.asyncio
    @pytest.mark.network
    async def test_pubmed_search_real(self):
        """Test PubMed search with real API call."""
        connector = self.create_connector()
        result = await connector.search("machine learning", limit=5)
        
        assert isinstance(result, dict)
        assert "total_results" in result
        assert "document_ids" in result
        assert "metadata" in result
        assert result["total_results"] > 0
        assert len(result["document_ids"]) <= 5

    @pytest.mark.asyncio
    @pytest.mark.network
    async def test_pubmed_get_by_id_real(self):
        """Test PubMed get_by_id with real API call."""
        connector = self.create_connector()
        result = await connector.get_by_id("40910727")
        
        assert isinstance(result, dict)
        assert result["id"] == "40910727"
        assert result["source"] == "pubmed"

    @pytest.mark.asyncio
    async def test_pubmed_search_with_mock(self):
        """Test PubMed search with mocked HTTP response."""
        connector = self.create_connector()
        
        mock_response = {
            "esearchresult": {
                "idlist": ["12345", "67890"],
                "count": "2"
            }
        }
        
        with patch.object(connector, 'make_request', return_value=mock_response):
            result = await connector.search("test query", limit=5)
            
            assert result["query"] == "test query"
            assert result["total_results"] == 2
            assert result["document_ids"] == ["12345", "67890"]
            assert result["metadata"]["db"] == "pubmed"

    @pytest.mark.asyncio
    async def test_pubmed_get_by_id_with_mock(self):
        """Test PubMed get_by_id with mocked HTTP response."""
        connector = self.create_connector()
        
        mock_xml = """
        <PubmedArticle>
            <MedlineCitation>
                <PMID>12345</PMID>
                <Article>
                    <ArticleTitle>Test Article</ArticleTitle>
                    <Abstract>
                        <AbstractText>Test abstract</AbstractText>
                    </Abstract>
                </Article>
            </MedlineCitation>
        </PubmedArticle>
        """
        
        with patch.object(connector.http_client, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.text = AsyncMock(return_value=mock_xml)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await connector.get_by_id("12345")
            
            assert result["id"] == "12345"
            assert result["source"] == "pubmed"

    @pytest.mark.asyncio
    async def test_pubmed_extract_authors(self):
        """Test PubMed author extraction."""
        connector = self.create_connector()
        
        response_data = {
            "PubmedArticle": {
                "Article": {
                    "AuthorList": {
                        "Author": [
                            {"LastName": "Smith", "ForeName": "John"},
                            {"LastName": "Doe", "ForeName": "Jane"}
                        ]
                    }
                }
            }
        }
        
        authors = connector.extract_authors(response_data)
        assert len(authors) == 2
        assert "Smith, John" in authors
        assert "Doe, Jane" in authors

    @pytest.mark.asyncio
    async def test_pubmed_extract_publication_date(self):
        """Test PubMed publication date extraction."""
        connector = self.create_connector()
        
        response_data = {
            "PubmedArticle": {
                "Article": {
                    "Journal": {
                        "JournalIssue": {
                            "PubDate": {
                                "Year": "2023",
                                "Month": "Jan",
                                "Day": "15"
                            }
                        }
                    }
                }
            }
        }
        
        date_str = connector.extract_publication_date(response_data)
        assert date_str is not None
        assert "2023" in date_str

    @pytest.mark.asyncio
    async def test_pubmed_get_updates(self):
        """Test PubMed get_updates method."""
        from datetime import datetime, timedelta
        
        connector = self.create_connector()
        since_date = datetime.now() - timedelta(days=30)
        
        # Mock the search method to return test data
        with patch.object(connector, 'search', return_value={
            "query": "test",
            "total_results": 2,
            "document_ids": ["12345", "67890"],
            "metadata": {"db": "pubmed"}
        }):
            updates = []
            async for update in connector.get_updates(since_date):
                updates.append(update)
                if len(updates) >= 2:
                    break
            
            assert len(updates) == 2
            assert updates[0]["query"] == "test"

    @pytest.mark.asyncio
    async def test_pubmed_rate_limiting(self):
        """Test PubMed rate limiting."""
        connector = self.create_connector()
        
        # Test that rate limiter is properly initialized
        assert hasattr(connector, 'rate_limit')
        assert connector.rate_limit == 3

    @pytest.mark.asyncio
    async def test_pubmed_error_handling(self):
        """Test PubMed error handling."""
        connector = self.create_connector()
        
        # Test with invalid query
        with patch.object(connector, 'make_request', side_effect=Exception("API Error")):
            result = await connector.search("invalid query", limit=5)
            
            # Should return error information
            assert "error" in result or result["total_results"] == 0

    @pytest.mark.asyncio
    async def test_pubmed_http_client_cleanup(self):
        """Test PubMed HTTP client cleanup."""
        connector = self.create_connector()
        
        # Test context manager cleanup
        with connector:
            assert connector.http_client is not None
        
        # HTTP client should be closed after context
        # Note: The actual cleanup happens in __exit__

    @pytest.mark.asyncio
    async def test_pubmed_search_parameters(self):
        """Test PubMed search parameters."""
        connector = self.create_connector()
        
        with patch.object(connector, 'make_request') as mock_request:
            mock_request.return_value = {
                "esearchresult": {
                    "idlist": [],
                    "count": "0"
                }
            }
            
            await connector.search("test query", limit=10)
            
            # Check that make_request was called with correct parameters
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "esearch.fcgi"
            assert call_args[0][1]["db"] == "pubmed"
            assert call_args[0][1]["term"] == "test query"
            assert call_args[0][1]["retmax"] == 10
            assert call_args[0][1]["retmode"] == "json"

    @pytest.mark.asyncio
    async def test_pubmed_get_by_id_parameters(self):
        """Test PubMed get_by_id parameters."""
        connector = self.create_connector()
        
        with patch.object(connector.http_client, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.text = AsyncMock(return_value="<xml>test</xml>")
            mock_get.return_value.__aenter__.return_value = mock_response
            
            await connector.get_by_id("12345")
            
            # Check that get was called with correct parameters
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "efetch.fcgi" in call_args[0][0]
            assert call_args[0][1]["db"] == "pubmed"
            assert call_args[0][1]["id"] == "12345"
            assert call_args[0][1]["retmode"] == "xml"
