"""Pytest configuration and shared fixtures."""

import asyncio
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import AsyncMock, MagicMock

from obc_connector_sdk.utils.connector_loader import ConnectorLoader
from obc_connector_sdk.models import Document, Author
from obc_connector_sdk.connector_capabilities import ConnectorCapability


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_connector_config():
    """Mock connector configuration."""
    return {
        "name": "test_connector",
        "display_name": "Test Connector",
        "description": "A test connector for unit testing",
        "version": "1.0.0",
        "capabilities": {
            "supports_document_content": True,
            "supports_json_content": True,
            "supports_advanced_search": True,
            "requires_authentication": False
        },
        "api": {
            "base_url": "https://api.test.com/",
            "rate_limit": {
                "requests_per_second": 10
            }
        }
    }


@pytest.fixture
def sample_document():
    """Sample document for testing."""
    return Document(
        id="test_doc_123",
        source="test_connector",
        title="Test Document",
        abstract="This is a test document for unit testing purposes.",
        publication_date=None,
        doi="10.1000/test.123",
        url="https://example.com/test-doc",
        authors=[
            Author(
                name="Test Author",
                orcid="0000-0000-0000-0000",
                email="test@example.com",
                affiliation="Test University"
            )
        ],
        keywords=["test", "unit", "testing"],
        document_type="article",
        full_text="Full text content of the test document.",
        metadata={"test_key": "test_value"}
    )


@pytest.fixture
def sample_search_result():
    """Sample search result for testing."""
    return {
        "query": "test query",
        "total_results": 100,
        "document_ids": ["doc1", "doc2", "doc3"],
        "metadata": {
            "source": "test_connector",
            "search_time": "2023-01-01T00:00:00Z"
        }
    }


@pytest.fixture
def mock_http_response():
    """Mock HTTP response for testing."""
    response = MagicMock()
    response.status = 200
    response.json = AsyncMock(return_value={"status": "success"})
    response.text = AsyncMock(return_value="<xml>test</xml>")
    response.raise_for_status = MagicMock()
    return response


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing."""
    client = MagicMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.close = AsyncMock()
    return client


@pytest.fixture
def mock_connector():
    """Mock connector for testing."""
    connector = MagicMock()
    connector.name = "test_connector"
    connector.capabilities = {
        "supports_document_content": True,
        "supports_json_content": True,
        "supports_advanced_search": True,
        "requires_authentication": False
    }
    connector.authenticate = AsyncMock()
    connector.search = AsyncMock()
    connector.get_by_id = AsyncMock()
    connector.get_updates = AsyncMock()
    connector.install = AsyncMock()
    connector.uninstall = AsyncMock()
    return connector


@pytest.fixture
def connector_test_data():
    """Test data for connector testing."""
    return {
        "valid_queries": [
            "machine learning",
            "cancer treatment",
            "COVID-19 vaccine",
            "artificial intelligence medical"
        ],
        "invalid_queries": [
            "",
            None,
            "   ",
            "a" * 1000  # Very long query
        ],
        "valid_doc_ids": [
            "12345",
            "67890",
            "test-doc-123"
        ],
        "invalid_doc_ids": [
            "",
            None,
            "invalid@id",
            "   "
        ]
    }


@pytest.fixture
def rate_limit_config():
    """Rate limiting configuration for testing."""
    return {
        "requests_per_second": 1.0,
        "burst_limit": 5,
        "timeout": 30
    }


@pytest.fixture
def error_scenarios():
    """Common error scenarios for testing."""
    return {
        "network_errors": [
            "ConnectionError",
            "TimeoutError",
            "aiohttp.ClientError"
        ],
        "api_errors": [
            "AuthenticationError",
            "RateLimitError",
            "ValidationError"
        ],
        "data_errors": [
            "ParseError",
            "KeyError",
            "ValueError"
        ]
    }


# Pytest markers for different test types
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests that test individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests that test component interactions"
    )
    config.addinivalue_line(
        "markers", "connector: Tests specific to connector implementations"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take a long time to run"
    )
    config.addinivalue_line(
        "markers", "network: Tests that require network access"
    )
    config.addinivalue_line(
        "markers", "mock: Tests that use mocking"
    )
    config.addinivalue_line(
        "markers", "regression: Regression tests to prevent bugs"
    )
    config.addinivalue_line(
        "markers", "smoke: Smoke tests for basic functionality"
    )
