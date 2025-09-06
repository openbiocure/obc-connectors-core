"""Simple tests for PubMed connector that match actual implementation."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from connectors.pubmed.connector import PubMedConnector


class TestPubMedConnectorSimple:
    """Simple test cases for PubMed connector."""

    def test_connector_initialization(self):
        """Test PubMed connector initialization."""
        connector = PubMedConnector()
        assert connector is not None
        assert connector.base_url == "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        assert connector.rate_limit == 3

    @pytest.mark.asyncio
    async def test_search_with_mock(self):
        """Test PubMed search with mocked HTTP response."""
        connector = PubMedConnector()

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
    async def test_search_with_error(self):
        """Test PubMed search with error handling."""
        connector = PubMedConnector()

        with patch.object(connector, 'make_request', side_effect=Exception("API Error")):
            result = await connector.search("test query", limit=5)

            assert result["query"] == "test query"
            assert result["total_results"] == 0
            assert result["document_ids"] == []
            assert "error" in result["metadata"]

    @pytest.mark.asyncio
    async def test_get_by_id_with_mock(self):
        """Test PubMed get_by_id with mocked HTTP response."""
        connector = PubMedConnector()

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
    async def test_get_by_id_with_error(self):
        """Test PubMed get_by_id with error handling."""
        connector = PubMedConnector()

        with patch.object(connector.http_client, 'get', side_effect=Exception("Network Error")):
            result = await connector.get_by_id("12345")

            assert result["id"] == "12345"
            assert result["source"] == "pubmed"
            assert "error" in result

    def test_extract_authors(self):
        """Test PubMed author extraction."""
        connector = PubMedConnector()

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

    def test_extract_publication_date(self):
        """Test PubMed publication date extraction."""
        connector = PubMedConnector()

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

    def test_extract_text(self):
        """Test text extraction utility."""
        connector = PubMedConnector()

        data = {"level1": {"level2": {"value": "test"}}}
        result = connector.extract_text(data, "level1.level2.value")
        assert result == "test"

    def test_extract_text_missing_key(self):
        """Test text extraction with missing key."""
        connector = PubMedConnector()

        data = {"level1": {"level2": {}}}
        result = connector.extract_text(data, "level1.level2.value")
        assert result is None

    def test_extract_list(self):
        """Test list extraction utility."""
        connector = PubMedConnector()

        data = {"level1": {"level2": ["item1", "item2"]}}
        result = connector.extract_list(data, "level1.level2")
        assert result == ["item1", "item2"]

    def test_extract_list_missing_key(self):
        """Test list extraction with missing key."""
        connector = PubMedConnector()

        data = {"level1": {"level2": {}}}
        result = connector.extract_list(data, "level1.level2")
        assert result == []

    @pytest.mark.asyncio
    async def test_authenticate(self):
        """Test authentication method."""
        connector = PubMedConnector()
        config = {"api_key": "test_key"}

        # Should not raise an exception
        await connector.authenticate(config)
        assert hasattr(connector, 'api_key')
        assert connector.api_key == "test_key"

    @pytest.mark.asyncio
    async def test_authenticate_without_key(self):
        """Test authentication without API key."""
        connector = PubMedConnector()
        config = {}

        # Should not raise an exception
        await connector.authenticate(config)

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test connector as context manager."""
        connector = PubMedConnector()

        # Test __enter__ and __exit__
        with connector:
            assert connector is not None

    @pytest.mark.asyncio
    async def test_close(self):
        """Test connector close method."""
        connector = PubMedConnector()

        # Should not raise an exception
        await connector.close()

    @pytest.mark.asyncio
    @pytest.mark.network
    async def test_search_real(self):
        """Test PubMed search with real API call."""
        connector = PubMedConnector()
        result = await connector.search("machine learning", limit=5)

        assert isinstance(result, dict)
        assert "total_results" in result
        assert "document_ids" in result
        assert "metadata" in result
        assert result["total_results"] > 0
        assert len(result["document_ids"]) <= 5

    @pytest.mark.asyncio
    @pytest.mark.network
    async def test_get_by_id_real(self):
        """Test PubMed get_by_id with real API call."""
        connector = PubMedConnector()
        result = await connector.get_by_id("40910727")

        assert isinstance(result, dict)
        assert result["id"] == "40910727"
        assert result["source"] == "pubmed"
