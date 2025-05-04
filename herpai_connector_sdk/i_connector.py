from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Set, Union, AsyncIterator
from datetime import datetime
from .connector_capabilities import ConnectorCapability

ContentType = Union[Dict[str, Any], str, bytes]

class IConnector(ABC):
    """Interface for all connectors in the HerpAI-Ingestion system.
    
    This interface defines the contract that all connectors must implement.
    It provides methods for:
    - Lifecycle management (enable/disable)
    - Authentication
    - Content retrieval (search, get by ID)
    - Capability inspection
    - Configuration management
    
    Implementations should:
    1. Declare their capabilities accurately
    2. Handle errors appropriately
    3. Implement proper resource management
    4. Follow rate limiting guidelines
    5. Provide detailed logging
    """
    
    @abstractmethod
    async def enable(self) -> None:
        """Enable the connector for use.
        
        This method should:
        1. Validate configuration
        2. Initialize necessary resources
        3. Establish connections if needed
        4. Update the connector registry
        
        Raises:
            ConnectorError: If the connector cannot be enabled
            ConfigurationError: If the configuration is invalid
            AuthenticationError: If authentication fails during enable
        """
        pass
    
    @abstractmethod
    async def disable(self) -> None:
        """Disable the connector.
        
        This method should:
        1. Clean up resources
        2. Close connections
        3. Update the connector registry
        4. Cancel any ongoing operations
        
        The connector should handle disable gracefully even if
        it encounters errors during cleanup.
        """
        pass
    
    @abstractmethod
    async def authenticate(self, config: Dict[str, Any]) -> None:
        """Authenticate with the data source.
        
        Args:
            config: Authentication configuration which may include:
                   - API keys
                   - OAuth tokens
                   - Username/password
                   - Custom authentication parameters
        
        Raises:
            AuthenticationError: If authentication fails
            RateLimitError: If authentication is rate limited
            ConfigurationError: If authentication configuration is invalid
        """
        pass
    
    @abstractmethod
    async def search(self, 
                    query: str, 
                    limit: Optional[int] = None,
                    offset: Optional[int] = None,
                    filters: Optional[Dict[str, Any]] = None,
                    sort: Optional[Dict[str, str]] = None) -> AsyncIterator[ContentType]:
        """Search the data source with the given query.
        
        This method should return an async iterator to allow for efficient
        streaming of results, especially for large result sets.
        
        Args:
            query: The search query string
            limit: Optional maximum number of results to return
            offset: Optional offset for pagination
            filters: Optional filters to apply (e.g., date ranges, fields)
            sort: Optional sorting criteria {field: direction}
        
        Returns:
            AsyncIterator yielding content items matching the query
            
        Raises:
            ConnectorError: If search fails
            RateLimitError: If search is rate limited
            AuthenticationError: If authentication is invalid
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, 
                       id: str,
                       include_metadata: bool = True) -> ContentType:
        """Retrieve a specific item by ID.
        
        Args:
            id: The item identifier
            include_metadata: Whether to include metadata in the response
        
        Returns:
            The content item with the specified ID
            
        Raises:
            ConnectorError: If retrieval fails
            NotFoundError: If the item doesn't exist
            RateLimitError: If retrieval is rate limited
        """
        pass
    
    @abstractmethod
    async def get_updates(self,
                         since: datetime,
                         until: Optional[datetime] = None) -> AsyncIterator[ContentType]:
        """Retrieve items updated within a time range.
        
        This method is required if SUPPORTS_INCREMENTAL_UPDATES is declared.
        
        Args:
            since: Start of the update time range
            until: Optional end of the update time range
        
        Returns:
            AsyncIterator yielding updated content items
            
        Raises:
            ConnectorError: If update retrieval fails
            NotImplementedError: If incremental updates not supported
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the connector name.
        
        Returns:
            String identifier for the connector
        """
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> Set[ConnectorCapability]:
        """Get the connector capabilities.
        
        The returned set MUST include at least one content type capability.
        Use ConnectorCapability.validate_content_type_capability() to verify.
        
        Returns:
            Set of ConnectorCapability values indicating supported features
        """
        pass
    
    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if the connector is enabled.
        
        Returns:
            bool: True if the connector is enabled and operational
        """
        pass
    
    @property
    @abstractmethod
    def configuration_schema(self) -> Dict[str, Any]:
        """Get the configuration schema for this connector.
        
        The schema should follow JSON Schema format and define:
        1. Required configuration parameters
        2. Optional parameters with defaults
        3. Parameter types and constraints
        4. Parameter descriptions
        
        Returns:
            Dict containing the JSON Schema for configuration
        """
        pass 