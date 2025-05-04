"""Core interfaces for the HerpAI Connector SDK."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncIterator
from datetime import datetime
from enum import Enum, auto

class ConnectorCapability(Enum):
    """Enumeration of connector capabilities."""
    SUPPORTS_FULLTEXT = auto()
    SUPPORTS_ADVANCED_SEARCH = auto()
    SUPPORTS_DATE_FILTERING = auto()
    REQUIRES_AUTHENTICATION = auto()
    SUPPORTS_NATIVE_PAGINATION = auto()
    SUPPORTS_DOCUMENT_CONTENT = auto()
    SUPPORTS_JSON_CONTENT = auto()
    SUPPORTS_STRING_CONTENT = auto()
    SUPPORTS_BINARY_CONTENT = auto()

class IConnector(ABC):
    """Interface for all connectors in the HerpAI-Ingestion system."""
    
    @abstractmethod
    async def install(self) -> None:
        """Install connector dependencies or set up resources."""
        pass
    
    @abstractmethod
    async def uninstall(self) -> None:
        """Clean up connector resources."""
        pass
    
    @abstractmethod
    async def authenticate(self, config: Dict[str, Any]) -> None:
        """Authenticate with the data source."""
        pass
    
    @abstractmethod
    async def search(self, query: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Search the data source with the given query."""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Dict[str, Any]:
        """Retrieve a specific document by ID."""
        pass
    
    @abstractmethod
    async def get_updates(self, since: datetime) -> AsyncIterator[Dict[str, Any]]:
        """Get updates since a specific date."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the connector name."""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> Dict[str, bool]:
        """Get the connector capabilities."""
        pass 