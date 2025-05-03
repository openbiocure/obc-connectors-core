from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class IConnector(ABC):
    """Interface for all connectors in the HerpAI-Ingestion system."""
    
    @abstractmethod
    async def enable(self) -> None:
        """Enable the connector for use.
        
        This method should perform any necessary setup to make the connector operational.
        For example: validating configuration, establishing connections, etc.
        
        Raises:
            ConnectorError: If the connector cannot be enabled.
        """
        pass
    
    @abstractmethod
    async def disable(self) -> None:
        """Disable the connector.
        
        This method should perform any necessary cleanup when the connector is disabled.
        For example: closing connections, clearing caches, etc.
        """
        pass
    
    @abstractmethod
    async def authenticate(self, config: Dict[str, Any]) -> None:
        """Authenticate with the data source.
        
        Args:
            config: Authentication configuration parameters.
            
        Raises:
            AuthenticationError: If authentication fails.
        """
        pass
    
    @abstractmethod
    async def search(self, query: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Search the data source with the given query.
        
        Args:
            query: The search query string.
            limit: Optional maximum number of results to return.
            
        Returns:
            Dict containing search results and metadata.
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Dict[str, Any]:
        """Retrieve a specific document by ID.
        
        Args:
            id: The document identifier.
            
        Returns:
            Dict containing the document data.
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the connector name."""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> Dict[str, bool]:
        """Get the connector capabilities.
        
        Returns:
            Dict containing capability flags (e.g., supports_fulltext, requires_authentication).
        """
        pass
    
    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if the connector is enabled.
        
        Returns:
            bool: True if the connector is enabled and operational.
        """
        pass 