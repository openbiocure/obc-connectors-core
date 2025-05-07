import os
import yaml
import logging
from typing import Dict, Any, Optional, Set, List, cast
from pathlib import Path
from .connector_capabilities import ConnectorCapability
from .exceptions.connector_error import ConnectorError

logger = logging.getLogger(__name__)

class ConnectorRegistry:
    """Registry for managing connector states and configurations."""
    
    def __init__(self, registry_path: Optional[str] = None):
        """Initialize the connector registry.
        
        Args:
            registry_path: Optional path to the connectors.yaml file.
                         If not provided, defaults to ./config/connectors.yaml
        """
        self._registry_path = registry_path or os.path.join("config", "connectors.yaml")
        self._registry: Dict[str, Any] = {}
        self._ensure_registry_file()
        self._load_registry()
    
    def _ensure_registry_file(self) -> None:
        """Ensure the registry file exists."""
        registry_dir = os.path.dirname(self._registry_path)
        if not os.path.exists(registry_dir):
            os.makedirs(registry_dir)
        
        if not os.path.exists(self._registry_path):
            # Create initial registry file
            self._registry = {
                "version": "1.0",
                "connectors": {}
            }
            self._save_registry()
    
    def _load_registry(self) -> None:
        """Load the registry from the YAML file."""
        try:
            with open(self._registry_path, 'r') as f:
                data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    raise ConnectorError("Invalid registry format: must be a dictionary")
                self._registry = cast(Dict[str, Any], data) or {
                    "version": "1.0",
                    "connectors": {}
                }
                
                # Ensure required structure
                if "version" not in self._registry:
                    self._registry["version"] = "1.0"
                if "connectors" not in self._registry:
                    self._registry["connectors"] = {}
                
        except Exception as e:
            raise ConnectorError(f"Failed to load connector registry: {str(e)}")
    
    def _save_registry(self) -> None:
        """Save the registry to the YAML file."""
        try:
            with open(self._registry_path, 'w') as f:
                yaml.safe_dump(self._registry, f, default_flow_style=False)
        except Exception as e:
            raise ConnectorError(f"Failed to save connector registry: {str(e)}")
    
    def register_connector(self, 
                         name: str, 
                         capabilities: Set[ConnectorCapability],
                         config_path: str,
                         enabled: bool = True) -> None:
        """Register a new connector in the registry.
        
        Args:
            name: Unique name of the connector
            capabilities: Set of connector capabilities
            config_path: Path to the connector's configuration file
            enabled: Whether the connector should be enabled by default
        
        Raises:
            ConnectorError: If registration fails
        """
        if name in self._registry["connectors"]:
            logger.warning(f"Connector {name} already registered, updating configuration")
        
        self._registry["connectors"][name] = {
            "name": name,
            "capabilities": ConnectorCapability.to_dict(capabilities),
            "config_path": config_path,
            "enabled": enabled,
            "state": "disabled"  # Initial state is always disabled until explicitly enabled
        }
        self._save_registry()
        logger.info(f"Registered connector: {name}")
    
    def unregister_connector(self, name: str) -> None:
        """Remove a connector from the registry.
        
        Args:
            name: Name of the connector to remove
            
        Raises:
            ConnectorError: If the connector doesn't exist
        """
        if name not in self._registry["connectors"]:
            raise ConnectorError(f"Connector not found: {name}")
        
        del self._registry["connectors"][name]
        self._save_registry()
        logger.info(f"Unregistered connector: {name}")
    
    def update_connector_state(self, name: str, enabled: bool) -> None:
        """Update the state of a connector.
        
        Args:
            name: Name of the connector
            enabled: Whether the connector should be enabled
            
        Raises:
            ConnectorError: If the connector doesn't exist
        """
        if name not in self._registry["connectors"]:
            raise ConnectorError(f"Connector not found: {name}")
        
        self._registry["connectors"][name]["state"] = "enabled" if enabled else "disabled"
        self._save_registry()
        logger.info(f"Updated connector {name} state to: {'enabled' if enabled else 'disabled'}")
    
    def get_connector_config(self, name: str) -> Dict[str, Any]:
        """Get the configuration for a connector.
        
        Args:
            name: Name of the connector
            
        Returns:
            Dict containing the connector's configuration
            
        Raises:
            ConnectorError: If the connector doesn't exist
        """
        if name not in self._registry["connectors"]:
            raise ConnectorError(f"Connector not found: {name}")
        
        return self._registry["connectors"][name].copy()
    
    def list_connectors(self, only_enabled: bool = False) -> List[Dict[str, Any]]:
        """List all registered connectors.
        
        Args:
            only_enabled: If True, only return enabled connectors
            
        Returns:
            List of connector configurations
        """
        connectors = self._registry["connectors"].values()
        if only_enabled:
            connectors = [c for c in connectors if c["state"] == "enabled"]
        return list(connectors)
    
    def is_connector_enabled(self, name: str) -> bool:
        """Check if a connector is enabled.
        
        Args:
            name: Name of the connector
            
        Returns:
            bool indicating if the connector is enabled
            
        Raises:
            ConnectorError: If the connector doesn't exist
        """
        if name not in self._registry["connectors"]:
            raise ConnectorError(f"Connector not found: {name}")
        
        return self._registry["connectors"][name]["state"] == "enabled" 