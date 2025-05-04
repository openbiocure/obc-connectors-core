"""Base implementation for connectors with common functionality."""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from .interfaces import IConnector, ConnectorCapability

logger = logging.getLogger(__name__)

class BaseConnector(IConnector):
    """Base implementation for connectors with common functionality."""
    
    def __init__(self):
        self._config = {}
        self._capabilities = {
            capability.name: False for capability in ConnectorCapability
        }
    
    async def install(self) -> None:
        """Default implementation of install that logs the action."""
        logger.info(f"Installing connector: {self.name}")
    
    async def uninstall(self) -> None:
        """Default implementation of uninstall that logs the action."""
        logger.info(f"Uninstalling connector: {self.name}")
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the connector with the provided settings."""
        self._config = config
    
    def load_specification(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Load the connector specification from a YAML file."""
        if not path:
            # Try to find specification in the connector's directory
            module_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(module_dir, "connector.yaml")
        
        if not os.path.exists(path):
            logger.warning(f"Specification file not found: {path}")
            return {}
        
        try:
            with open(path, "r") as f:
                spec = yaml.safe_load(f)
                
                # Update capabilities from spec
                if "capabilities" in spec:
                    # Handle both string-based and enum-based capabilities
                    for key, value in spec["capabilities"].items():
                        try:
                            # Try to convert string to enum
                            capability = ConnectorCapability[key.upper()]
                            self._capabilities[capability.name] = value
                        except KeyError:
                            # If not an enum, store as is
                            self._capabilities[key] = value
                
                return spec
        except Exception as e:
            logger.error(f"Error loading specification: {str(e)}")
            return {}
    
    @property
    def capabilities(self) -> Dict[str, bool]:
        """Get the connector capabilities."""
        return self._capabilities.copy() 