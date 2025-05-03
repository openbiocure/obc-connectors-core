from typing import Dict, List, Optional, Any, Set
import yaml
import os
import logging
from openbiocure_corelib import YamlConfig
from .i_connector import IConnector
from .connector_capabilities import ConnectorCapability
from .connector_registry import ConnectorRegistry
from .exceptions.connector_error import ConnectorError
from .exceptions.authentication_error import AuthenticationError
from .exceptions.rate_limit_error import RateLimitError

logger = logging.getLogger(__name__)

class BaseConnector(IConnector):
    """Base implementation of the IConnector interface with common functionality."""
    
    _registry: Optional[ConnectorRegistry] = None
    
    @classmethod
    def get_registry(cls) -> ConnectorRegistry:
        """Get or create the connector registry instance."""
        if cls._registry is None:
            cls._registry = ConnectorRegistry()
        return cls._registry
    
    def __init__(self):
        """Initialize the base connector."""
        self._config: Dict[str, Any] = {}
        self._capabilities: Set[ConnectorCapability] = set()
        self._name: str = ""
        self._load_connector_config()
        
        # Register this connector instance
        registry = self.get_registry()
        registry.register_connector(
            name=self._name,
            capabilities=self._capabilities,
            config_path=self._get_config_path(),
            enabled=self._config.get("enabled", True)
        )
    
    def _get_config_path(self) -> str:
        """Get the path to this connector's configuration file."""
        return os.path.join(
            os.path.dirname(os.path.abspath(self.__class__.__module__)),
            "connector.yaml"
        )
    
    def _load_connector_config(self) -> None:
        """Load connector configuration from YAML file."""
        try:
            config_path = self._get_config_path()
            
            if not os.path.exists(config_path):
                raise ConnectorError(f"Connector configuration not found: {config_path}")
            
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Load basic connector information
            self._name = config.get("name", self.__class__.__name__)
            
            # Load capabilities from config
            capabilities_config = config.get("capabilities", {})
            self._capabilities = {
                cap for cap in ConnectorCapability
                if capabilities_config.get(cap.value, False)
            }
            
            self._config = config
            
        except Exception as e:
            raise ConnectorError(f"Failed to load connector configuration: {str(e)}")
    
    async def enable(self) -> None:
        """Enable the connector for use.
        
        This base implementation validates the configuration and updates the registry.
        Subclasses should override this if they need additional setup steps.
        
        Raises:
            ConnectorError: If the connector cannot be enabled or configuration is invalid.
        """
        try:
            # Validate required configuration
            self._validate_config()
            
            # Update registry state
            registry = self.get_registry()
            registry.update_connector_state(self._name, True)
            
            logger.info(f"Enabled connector: {self.name}")
            
        except Exception as e:
            raise ConnectorError(f"Failed to enable connector {self.name}: {str(e)}")
    
    async def disable(self) -> None:
        """Disable the connector.
        
        This base implementation updates the registry state.
        Subclasses should override this if they need additional cleanup steps.
        """
        registry = self.get_registry()
        registry.update_connector_state(self._name, False)
        logger.info(f"Disabled connector: {self.name}")
    
    def _validate_config(self) -> None:
        """Validate the connector configuration.
        
        Raises:
            ConnectorError: If the configuration is invalid.
        """
        # Check if connector is enabled in config
        if not self._config.get("enabled", True):
            raise ConnectorError(f"Connector {self.name} is disabled in configuration")
        
        # Check if authentication is required but not configured
        if ConnectorCapability.REQUIRES_AUTHENTICATION in self.capabilities:
            auth_config = self._config.get("auth", {})
            if not auth_config:
                raise ConnectorError(f"Authentication configuration missing for connector {self.name}")
        
        # Validate required configuration properties
        for prop in self._config.get("configuration", {}).get("properties", []):
            if prop.get("required", False):
                if prop["name"] not in self._config:
                    raise ConnectorError(
                        f"Required configuration property '{prop['name']}' not found for connector {self.name}"
                    )
    
    @property
    def name(self) -> str:
        """Get the connector name."""
        return self._name
    
    @property
    def capabilities(self) -> Set[ConnectorCapability]:
        """Get the connector capabilities.
        
        Returns:
            Set of ConnectorCapability values indicating supported features.
        """
        return self._capabilities.copy()
    
    @property
    def is_enabled(self) -> bool:
        """Check if the connector is enabled.
        
        Returns:
            bool: True if the connector is enabled and operational.
        """
        registry = self.get_registry()
        return registry.is_connector_enabled(self._name)
    
    async def authenticate(self, config: Dict[str, Any]) -> None:
        """Authenticate with the data source.
        
        Args:
            config: Authentication configuration parameters.
            
        Raises:
            AuthenticationError: If authentication fails.
            NotImplementedError: If authentication is required but not implemented.
        """
        if ConnectorCapability.REQUIRES_AUTHENTICATION in self.capabilities:
            raise NotImplementedError("Authentication is required but not implemented")
        logger.debug(f"No authentication required for connector: {self.name}")
    
    async def search(self, query: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Search the data source with the given query.
        
        Args:
            query: The search query string.
            limit: Optional maximum number of results to return.
            
        Returns:
            Dict containing search results and metadata.
            
        Raises:
            NotImplementedError: This base method must be implemented by subclasses.
            ConnectorError: If the connector is not enabled.
        """
        if not self.is_enabled:
            raise ConnectorError(f"Connector {self.name} is not enabled")
        raise NotImplementedError("search() must be implemented by connector")
    
    async def get_by_id(self, id: str) -> Dict[str, Any]:
        """Retrieve a specific document by ID.
        
        Args:
            id: The document identifier.
            
        Returns:
            Dict containing the document data.
            
        Raises:
            NotImplementedError: This base method must be implemented by subclasses.
            ConnectorError: If the connector is not enabled.
        """
        if not self.is_enabled:
            raise ConnectorError(f"Connector {self.name} is not enabled")
        raise NotImplementedError("get_by_id() must be implemented by connector")
    
    def _get_rate_limit(self) -> Dict[str, int]:
        """Get rate limit configuration.
        
        Returns:
            Dict containing rate limit settings (requests_per_second, with_api_key).
        """
        return self._config.get("api", {}).get("rate_limit", {
            "requests_per_second": 3,
            "with_api_key": 10
        }) 