"""Unit tests for connector capabilities."""

import pytest
from obc_connector_sdk.connector_capabilities import ConnectorCapability


class TestConnectorCapability:
    """Test cases for ConnectorCapability enum."""

    def test_capability_values(self):
        """Test that capabilities have correct string values."""
        assert ConnectorCapability.SUPPORTS_DOCUMENT_CONTENT.value == "supports_document_content"
        assert ConnectorCapability.SUPPORTS_JSON_CONTENT.value == "supports_json_content"
        assert ConnectorCapability.SUPPORTS_STRING_CONTENT.value == "supports_string_content"
        assert ConnectorCapability.SUPPORTS_BINARY_CONTENT.value == "supports_binary_content"
        assert ConnectorCapability.SUPPORTS_FULLTEXT.value == "supports_fulltext"
        assert ConnectorCapability.SUPPORTS_ADVANCED_SEARCH.value == "supports_advanced_search"
        assert ConnectorCapability.SUPPORTS_DATE_FILTERING.value == "supports_date_filtering"
        assert ConnectorCapability.REQUIRES_AUTHENTICATION.value == "requires_authentication"

    def test_to_dict_empty(self):
        """Test to_dict with empty capabilities set."""
        capabilities = set()
        result = ConnectorCapability.to_dict(capabilities)

        # All capabilities should be False
        for capability in ConnectorCapability:
            assert result[capability.value] is False

    def test_to_dict_single_capability(self):
        """Test to_dict with single capability."""
        capabilities = {ConnectorCapability.SUPPORTS_FULLTEXT}
        result = ConnectorCapability.to_dict(capabilities)

        assert result["supports_fulltext"] is True
        assert result["supports_document_content"] is False
        assert result["supports_json_content"] is False
        assert result["requires_authentication"] is False

    def test_to_dict_multiple_capabilities(self):
        """Test to_dict with multiple capabilities."""
        capabilities = {
            ConnectorCapability.SUPPORTS_DOCUMENT_CONTENT,
            ConnectorCapability.SUPPORTS_ADVANCED_SEARCH,
            ConnectorCapability.REQUIRES_AUTHENTICATION
        }
        result = ConnectorCapability.to_dict(capabilities)

        assert result["supports_document_content"] is True
        assert result["supports_advanced_search"] is True
        assert result["requires_authentication"] is True
        assert result["supports_fulltext"] is False
        assert result["supports_json_content"] is False

    def test_validate_content_type_capability_valid(self):
        """Test content type validation with valid capabilities."""
        # Test with document content
        capabilities = {ConnectorCapability.SUPPORTS_DOCUMENT_CONTENT}
        assert ConnectorCapability.validate_content_type_capability(capabilities) is True

        # Test with JSON content
        capabilities = {ConnectorCapability.SUPPORTS_JSON_CONTENT}
        assert ConnectorCapability.validate_content_type_capability(capabilities) is True

        # Test with string content
        capabilities = {ConnectorCapability.SUPPORTS_STRING_CONTENT}
        assert ConnectorCapability.validate_content_type_capability(capabilities) is True

        # Test with binary content
        capabilities = {ConnectorCapability.SUPPORTS_BINARY_CONTENT}
        assert ConnectorCapability.validate_content_type_capability(capabilities) is True

        # Test with multiple content types
        capabilities = {
            ConnectorCapability.SUPPORTS_DOCUMENT_CONTENT,
            ConnectorCapability.SUPPORTS_JSON_CONTENT
        }
        assert ConnectorCapability.validate_content_type_capability(capabilities) is True

    def test_validate_content_type_capability_invalid(self):
        """Test content type validation with invalid capabilities."""
        # Test with no content type capabilities
        capabilities = {ConnectorCapability.SUPPORTS_FULLTEXT}
        assert ConnectorCapability.validate_content_type_capability(capabilities) is False

        # Test with empty set
        capabilities = set()
        assert ConnectorCapability.validate_content_type_capability(capabilities) is False

        # Test with only non-content capabilities
        capabilities = {
            ConnectorCapability.SUPPORTS_ADVANCED_SEARCH,
            ConnectorCapability.REQUIRES_AUTHENTICATION
        }
        assert ConnectorCapability.validate_content_type_capability(capabilities) is False

    def test_all_capabilities_covered(self):
        """Test that to_dict covers all capabilities."""
        capabilities = set(ConnectorCapability)
        result = ConnectorCapability.to_dict(capabilities)

        # Should have an entry for every capability
        assert len(result) == len(ConnectorCapability)

        # All should be True
        for capability in ConnectorCapability:
            assert result[capability.value] is True

    def test_content_type_capabilities_constant(self):
        """Test that content type capabilities are correctly defined."""
        content_type_caps = {
            ConnectorCapability.SUPPORTS_DOCUMENT_CONTENT,
            ConnectorCapability.SUPPORTS_JSON_CONTENT,
            ConnectorCapability.SUPPORTS_STRING_CONTENT,
            ConnectorCapability.SUPPORTS_BINARY_CONTENT
        }

        # Test that each content type capability validates correctly
        for cap in content_type_caps:
            assert ConnectorCapability.validate_content_type_capability({cap}) is True
