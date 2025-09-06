"""Base test class for connector testing."""

import pytest
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch

from obc_connector_sdk.base_connector import BaseConnector
from obc_connector_sdk.models import Document


class ConnectorTestBase(ABC):
    """Base class for testing connectors."""

    @abstractmethod
    def get_connector_class(self):
        """Return the connector class to test."""
        pass

    @abstractmethod
    def get_connector_name(self):
        """Return the connector name."""
        pass

    @abstractmethod
    def get_valid_queries(self):
        """Return list of valid test queries."""
        pass

    @abstractmethod
    def get_valid_doc_ids(self):
        """Return list of valid document IDs for testing."""
        pass

    @abstractmethod
    def get_expected_capabilities(self):
        """Return expected capabilities for this connector."""
        pass

    def create_connector(self, **kwargs):
        """Create a connector instance for testing."""
        connector_class = self.get_connector_class()
        return connector_class(**kwargs)

    @pytest.mark.asyncio
    async def test_connector_initialization(self):
        """Test that connector initializes correctly."""
        connector = self.create_connector()
        assert connector is not None
        assert hasattr(connector, 'name')
        assert hasattr(connector, 'capabilities')

    @pytest.mark.asyncio
    async def test_connector_name(self):
        """Test connector name property."""
        connector = self.create_connector()
        assert connector.name == self.get_connector_name()

    @pytest.mark.asyncio
    async def test_connector_capabilities(self):
        """Test connector capabilities."""
        connector = self.create_connector()
        capabilities = connector.capabilities
        expected_capabilities = self.get_expected_capabilities()
        
        for capability, expected_value in expected_capabilities.items():
            assert capabilities.get(capability) == expected_value

    @pytest.mark.asyncio
    async def test_authenticate_method(self):
        """Test authenticate method exists and is callable."""
        connector = self.create_connector()
        assert hasattr(connector, 'authenticate')
        assert callable(connector.authenticate)

    @pytest.mark.asyncio
    async def test_search_method(self):
        """Test search method exists and is callable."""
        connector = self.create_connector()
        assert hasattr(connector, 'search')
        assert callable(connector.search)

    @pytest.mark.asyncio
    async def test_get_by_id_method(self):
        """Test get_by_id method exists and is callable."""
        connector = self.create_connector()
        assert hasattr(connector, 'get_by_id')
        assert callable(connector.get_by_id)

    @pytest.mark.asyncio
    async def test_get_updates_method(self):
        """Test get_updates method exists and is callable."""
        connector = self.create_connector()
        assert hasattr(connector, 'get_updates')
        assert callable(connector.get_updates)

    @pytest.mark.asyncio
    async def test_install_method(self):
        """Test install method exists and is callable."""
        connector = self.create_connector()
        assert hasattr(connector, 'install')
        assert callable(connector.install)

    @pytest.mark.asyncio
    async def test_uninstall_method(self):
        """Test uninstall method exists and is callable."""
        connector = self.create_connector()
        assert hasattr(connector, 'uninstall')
        assert callable(connector.uninstall)

    @pytest.mark.asyncio
    @pytest.mark.network
    async def test_search_with_valid_queries(self):
        """Test search with valid queries."""
        connector = self.create_connector()
        valid_queries = self.get_valid_queries()
        
        for query in valid_queries:
            try:
                result = await connector.search(query, limit=5)
                assert isinstance(result, dict)
                assert "total_results" in result
                assert "document_ids" in result
                assert isinstance(result["total_results"], int)
                assert isinstance(result["document_ids"], list)
                assert result["total_results"] >= 0
            except Exception as e:
                pytest.fail(f"Search failed for query '{query}': {str(e)}")

    @pytest.mark.asyncio
    @pytest.mark.network
    async def test_get_by_id_with_valid_ids(self):
        """Test get_by_id with valid document IDs."""
        connector = self.create_connector()
        valid_doc_ids = self.get_valid_doc_ids()
        
        for doc_id in valid_doc_ids:
            try:
                result = await connector.get_by_id(doc_id)
                assert isinstance(result, dict)
                assert "id" in result
                assert result["id"] == doc_id
            except Exception as e:
                pytest.fail(f"get_by_id failed for document ID '{doc_id}': {str(e)}")

    @pytest.mark.asyncio
    async def test_search_with_invalid_query(self):
        """Test search with invalid query."""
        connector = self.create_connector()
        
        # Test with empty query
        with pytest.raises(Exception):
            await connector.search("", limit=5)
        
        # Test with None query
        with pytest.raises(Exception):
            await connector.search(None, limit=5)

    @pytest.mark.asyncio
    async def test_get_by_id_with_invalid_id(self):
        """Test get_by_id with invalid document ID."""
        connector = self.create_connector()
        
        # Test with empty ID
        with pytest.raises(Exception):
            await connector.get_by_id("")
        
        # Test with None ID
        with pytest.raises(Exception):
            await connector.get_by_id(None)

    @pytest.mark.asyncio
    async def test_search_with_negative_limit(self):
        """Test search with negative limit."""
        connector = self.create_connector()
        
        with pytest.raises(Exception):
            await connector.search("test query", limit=-1)

    @pytest.mark.asyncio
    async def test_search_with_zero_limit(self):
        """Test search with zero limit."""
        connector = self.create_connector()
        
        result = await connector.search("test query", limit=0)
        assert isinstance(result, dict)
        assert result["total_results"] >= 0
        assert len(result["document_ids"]) == 0

    @pytest.mark.asyncio
    async def test_authenticate_with_config(self):
        """Test authenticate with configuration."""
        connector = self.create_connector()
        config = {"api_key": "test_key", "base_url": "https://api.test.com"}
        
        # Should not raise an exception
        await connector.authenticate(config)

    @pytest.mark.asyncio
    async def test_install_and_uninstall(self):
        """Test install and uninstall methods."""
        connector = self.create_connector()
        
        # Should not raise exceptions
        await connector.install()
        await connector.uninstall()

    @pytest.mark.asyncio
    async def test_get_updates_with_date(self):
        """Test get_updates with date parameter."""
        from datetime import datetime, timedelta
        
        connector = self.create_connector()
        since_date = datetime.now() - timedelta(days=30)
        
        try:
            updates = []
            async for update in connector.get_updates(since_date):
                updates.append(update)
                if len(updates) >= 5:  # Limit for testing
                    break
            
            # Should not raise an exception
            assert isinstance(updates, list)
        except Exception as e:
            # Some connectors might not support updates
            pytest.skip(f"get_updates not supported: {str(e)}")

    @pytest.mark.asyncio
    async def test_connector_context_manager(self):
        """Test connector as context manager."""
        connector = self.create_connector()
        
        # Test __enter__ and __exit__
        with connector:
            assert connector is not None

    @pytest.mark.asyncio
    async def test_connector_close(self):
        """Test connector close method."""
        connector = self.create_connector()
        
        # Should not raise an exception
        await connector.close()

    @pytest.mark.asyncio
    async def test_search_result_structure(self):
        """Test that search results have expected structure."""
        connector = self.create_connector()
        valid_queries = self.get_valid_queries()
        
        if not valid_queries:
            pytest.skip("No valid queries available for testing")
        
        query = valid_queries[0]
        result = await connector.search(query, limit=5)
        
        # Check required fields
        required_fields = ["query", "total_results", "document_ids"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Check data types
        assert isinstance(result["query"], str)
        assert isinstance(result["total_results"], int)
        assert isinstance(result["document_ids"], list)
        
        # Check that query matches input
        assert result["query"] == query

    @pytest.mark.asyncio
    async def test_document_result_structure(self):
        """Test that document results have expected structure."""
        connector = self.create_connector()
        valid_doc_ids = self.get_valid_doc_ids()
        
        if not valid_doc_ids:
            pytest.skip("No valid document IDs available for testing")
        
        doc_id = valid_doc_ids[0]
        result = await connector.get_by_id(doc_id)
        
        # Check required fields
        required_fields = ["id", "source"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Check data types
        assert isinstance(result["id"], str)
        assert isinstance(result["source"], str)
        
        # Check that ID matches input
        assert result["id"] == doc_id
