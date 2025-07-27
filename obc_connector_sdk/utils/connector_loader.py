"""Utilities for dynamically loading and managing connectors."""

import importlib
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, Tuple, Type

import yaml

from ..base_connector import BaseConnector
from ..exceptions import ConnectorError

logger = logging.getLogger(__name__)


class ConnectorLoader:
    """Utility class for loading and managing connectors."""

    CONNECTOR_PATHS = [
        # When installed as a package
        lambda: os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "connectors"),
        # When in development
        lambda: os.getcwd(),
        # Environment variable override
        lambda: os.getenv("obc_CONNECTORS_PATH"),
    ]

    @classmethod
    def _get_search_paths(cls) -> list[str]:
        """Get list of valid connector search paths."""
        return [path() for path in cls.CONNECTOR_PATHS if path() is not None]

    @classmethod
    def _get_yaml_version(cls, connector_dir: str) -> str:
        """Get version from connector.yaml file."""
        yaml_path = os.path.join(connector_dir, "connector.yaml")
        if not os.path.exists(yaml_path):
            raise ConnectorError(f"connector.yaml not found in {connector_dir}")

        with open(yaml_path) as f:
            spec = yaml.safe_load(f)
            if not spec.get("version"):
                raise ConnectorError(f"Version not specified in {yaml_path}")
            return spec["version"]

    @classmethod
    def find_connector_dir(cls, connector_name: str) -> str:
        """Find the connector directory.

        Args:
            connector_name: Name of the connector (e.g., 'pubmed')

        Returns:
            Path to the connector directory

        Raises:
            ConnectorError: If connector directory cannot be found
        """
        for base_path in cls._get_search_paths():
            connector_dir = os.path.join(base_path, "connectors", connector_name)
            if os.path.exists(connector_dir):
                return connector_dir

        raise ConnectorError(f"Connector directory not found for: {connector_name}")

    @classmethod
    def load_yaml_spec(cls, connector_dir: str) -> Dict[str, Any]:
        """Load and validate the connector's YAML specification.

        Args:
            connector_dir: Path to the connector directory

        Returns:
            Parsed and validated YAML specification

        Raises:
            ConnectorError: If YAML is missing or invalid
        """
        yaml_path = os.path.join(connector_dir, "connector.yaml")
        if not os.path.exists(yaml_path):
            raise ConnectorError(f"connector.yaml not found in {connector_dir}")

        try:
            with open(yaml_path) as f:
                spec = yaml.safe_load(f)

            # Validate required fields
            if not spec.get("name"):
                raise ConnectorError("Invalid connector.yaml: 'name' field missing")

            return spec
        except Exception as e:
            raise ConnectorError(f"Error loading connector.yaml: {str(e)}")

    @classmethod
    def load_connector_class(cls, connector_name: str) -> Type[BaseConnector]:
        """Load a connector class by name.

        Args:
            connector_name: Name of the connector (e.g., 'pubmed')

        Returns:
            Connector class that inherits from BaseConnector

        Raises:
            ConnectorError: If connector cannot be loaded
        """
        try:
            # Find and validate connector directory
            connector_dir = cls.find_connector_dir(connector_name)

            # Load and validate YAML spec
            cls.load_yaml_spec(connector_dir)

            # Import the connector module
            module = importlib.import_module(f"connectors.{connector_name}.connector")

            # Find the connector class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BaseConnector)
                    and attr != BaseConnector
                ):
                    return attr

            raise ConnectorError(f"No connector class found in {connector_name}/connector.py")
        except ImportError as e:
            raise ConnectorError(f"Failed to load connector {connector_name}: {str(e)}")
        except Exception as e:
            raise ConnectorError(f"Error loading connector {connector_name}: {str(e)}")

    @classmethod
    @asynccontextmanager
    async def managed_connector(cls, connector_name: str, version: Optional[str] = None):
        """Context manager for handling connector lifecycle.

        Args:
            connector_name: Name of the connector to load
            version: Optional version for validation. If provided, checks against YAML version.

        Yields:
            Initialized connector instance

        Example:
            ```python
            async with ConnectorLoader.managed_connector("pubmed") as connector:
                await connector.authenticate({"api_key": "..."})
                results = await connector.search("query")
            ```
        """
        connector_class = cls.load_connector_class(connector_name)

        # Version validation if requested
        if version:
            connector_dir = cls.find_connector_dir(connector_name)
            yaml_version = cls._get_yaml_version(connector_dir)
            if yaml_version != version:
                raise ConnectorError(
                    f"Version mismatch: requested version {version} != "
                    f"yaml version {yaml_version}"
                )

        connector = connector_class()
        try:
            yield connector
        finally:
            if hasattr(connector, "http_client") and connector.http_client:
                await connector.http_client.close()
            elif hasattr(connector, "close"):
                await connector.close()

    @classmethod
    async def test_connector(
        cls,
        connector_name: str,
        version: Optional[str] = None,
        query: Optional[str] = None,
        doc_id: Optional[str] = None,
        api_key: Optional[str] = None,
        limit: int = 10,
        callback=None,
    ):
        """Test a connector's functionality.

        Args:
            connector_name: Name of the connector to test
            version: Optional version to validate against YAML
            query: Optional search query
            doc_id: Optional document ID to fetch
            api_key: Optional API key for authentication
            limit: Maximum number of results to return
            callback: Optional callback function for progress/results
        """
        if callback is None:
            callback = logger.info

        async with cls.managed_connector(connector_name, version) as connector:
            # Configure with API key if provided
            if api_key:
                await connector.authenticate({"api_key": api_key})

            if query:
                # Test search
                version_str = f" v{version}" if version else ""
                callback(f"Searching {connector_name}{version_str}...")
                results = await connector.search(query, limit=limit)
                if results and "total_results" in results:
                    callback(f"Found {results['total_results']} results")
                    if "document_ids" in results:
                        for doc_id in results["document_ids"][:limit]:
                            callback(f"- {doc_id}")
                    else:
                        callback("No document IDs found in response")
                else:
                    callback("No results found")

            if doc_id:
                # Test document retrieval
                callback(f"\nFetching document {doc_id}...")
                doc = await connector.get_by_id(doc_id)
                if doc:
                    callback(f"Title: {doc.get('title', 'No title')}")
                    callback(f"Abstract: {doc.get('abstract', 'No abstract')[:200]}...")
                else:
                    callback("Document not found")
