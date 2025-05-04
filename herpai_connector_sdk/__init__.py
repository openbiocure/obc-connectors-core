"""HerpAI Connector SDK.

A flexible SDK for building data source connectors for the HerpAI-Ingestion system.
"""

from .interfaces import IConnector, ConnectorCapability
from .base import BaseConnector
from .models import Document, Author, ContentType
from .exceptions import (
    ConnectorError,
    AuthenticationError,
    RateLimitExceeded,
    FetchError,
    ParseError
)

__version__ = "1.0.0"
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