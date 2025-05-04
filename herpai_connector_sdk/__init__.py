"""HerpAI Connector SDK.

A flexible SDK for building data source connectors for the HerpAI-Ingestion system.
"""

__version__ = "0.1.0"

# Core interfaces and base classes
from .i_connector import IConnector, ConnectorCapability
from .base_connector import BaseConnector
from .models import Document, Author, ContentType
from .exceptions import (
    ConnectorError,
    AuthenticationError,
    RateLimitExceeded,
    FetchError,
    ParseError
)

__all__ = [
    'IConnector',
    'ConnectorCapability',
    'BaseConnector',
    'Document',
    'Author',
    'ContentType',
    'ConnectorError',
    'AuthenticationError',
    'RateLimitExceeded',
    'FetchError',
    'ParseError'
] 