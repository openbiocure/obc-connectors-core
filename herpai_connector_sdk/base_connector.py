"""Base implementation for YAML-driven connectors."""

import os
import logging
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from dynaconf import Dynaconf
from .i_connector import IConnector, ConnectorCapability
from .utils.http import HTTPClient
from .utils.rate_limiter import RateLimiter
from .exceptions import (
    ConnectorError,
    AuthenticationError,
    RateLimitExceeded,
    FetchError,
    ParseError
)

logger = logging.getLogger(__name__)

class BaseConnector(IConnector):
    """Base implementation for YAML-driven connectors."""
    
    def __init__(self):
        self._config = {}
        self._capabilities = {
            capability.name: False for capability in ConnectorCapability
        }
        self._settings = None
        self._http_client = None
        self._rate_limiter = None
        self._spec = {}
    
    async def install(self) -> None:
        """Install connector."""
        logger.info(f"Installing connector: {self.name}")
    
    async def uninstall(self) -> None:
        """Uninstall connector."""
        logger.info(f"Uninstalling connector: {self.name}")
        if self._http_client:
            await self._http_client.close()
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the connector."""
        self._config = config
        
        # Update rate limiter if API key provided
        if config.get("api_key") and self._rate_limiter:
            rate_limit = self._spec.get("rate_limit", {}).get("with_api_key", 10)
            self._rate_limiter.requests_per_second = rate_limit
    
    def load_specification(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Load and process the YAML specification."""
        if not path:
            module_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(module_dir, "connector.yaml")
        
        if not os.path.exists(path):
            logger.warning(f"Specification file not found: {path}")
            return {}
        
        try:
            # Initialize Dynaconf with the YAML file
            settings = Dynaconf(
                settings_files=[path],
                environments=True,
                env_prefix="HERPAI_",
                lowercase_read=True,
                merge_enabled=True
            )
            
            self._settings = settings
            
            # Convert to dict and store
            self._spec = {
                key: value for key, value in settings.as_dict().items()
                if not key.startswith('_')
            }
            
            # Initialize capabilities
            if "capabilities" in self._spec:
                for key, value in self._spec["capabilities"].items():
                    try:
                        capability = ConnectorCapability[key.upper()]
                        self._capabilities[capability.name] = value
                    except KeyError:
                        self._capabilities[key] = value
            
            # Initialize HTTP client
            base_url = self._spec.get("api", {}).get("base_url")
            if base_url:
                self._http_client = HTTPClient(base_url)
            
            # Initialize rate limiter
            rate_limit = self._spec.get("rate_limit", {}).get("requests_per_second", 3)
            self._rate_limiter = RateLimiter(rate_limit)
            
            return self._spec
            
        except Exception as e:
            logger.error(f"Error loading specification: {str(e)}")
            return {}
    
    def _build_params(self, param_spec: Dict[str, Any], values: Dict[str, Any]) -> Dict[str, Any]:
        """Build request parameters from specification."""
        params = {}
        for key, template in param_spec.items():
            if isinstance(template, str) and template.startswith("{") and template.endswith("}"):
                # Template parameter
                param_name = template[1:-1]
                if param_name in values and values[param_name] is not None:
                    params[key] = values[param_name]
            else:
                # Static parameter
                params[key] = template
        return params
    
    def _extract_value(self, data: Any, path: str) -> Any:
        """Extract value from response using path."""
        if isinstance(data, dict):
            # Handle JSON path
            parts = path.split(".")
            value = data
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    return None
            return value
        elif isinstance(data, ET.Element):
            # Handle XML path
            try:
                if path.startswith(".//"):
                    # XPath
                    elem = data.find(path)
                    return elem.text if elem is not None else None
                else:
                    # Direct child
                    return data.findtext(path)
            except Exception as e:
                logger.error(f"Error extracting XML value: {str(e)}")
                return None
        return None
    
    def _apply_transform(self, data: Any, transform_spec: Dict[str, Any]) -> Any:
        """Apply transformation to extracted value."""
        if "path" not in transform_spec:
            return None
            
        # Extract base value
        value = self._extract_value(data, transform_spec["path"])
        
        if "transform" in transform_spec:
            if isinstance(value, str):
                # Handle date transformations
                if all(k in transform_spec["transform"] for k in ["year", "month", "day"]):
                    try:
                        year = self._extract_value(data, transform_spec["transform"]["year"]) or "1970"
                        month = self._extract_value(data, transform_spec["transform"]["month"].split("|")[0]) or "1"
                        day = self._extract_value(data, transform_spec["transform"]["day"].split("|")[0]) or "1"
                        
                        # Handle month names
                        if not month.isdigit():
                            month_map = {
                                "Jan": "1", "Feb": "2", "Mar": "3", "Apr": "4",
                                "May": "5", "Jun": "6", "Jul": "7", "Aug": "8",
                                "Sep": "9", "Oct": "10", "Nov": "11", "Dec": "12"
                            }
                            month = month_map.get(month[:3], "1")
                        
                        return datetime(int(year), int(month), int(day))
                    except (ValueError, TypeError) as e:
                        logger.error(f"Error transforming date: {str(e)}")
                        return None
                        
        if "list" in transform_spec and transform_spec["list"]:
            # Handle list of values
            if isinstance(data, ET.Element):
                elements = data.findall(transform_spec["path"])
                if "mapping" in transform_spec:
                    # Transform each element
                    return [
                        {
                            k: self._apply_transform(elem, v) if isinstance(v, dict) else self._extract_value(elem, v)
                            for k, v in transform_spec["mapping"].items()
                        }
                        for elem in elements
                    ]
                else:
                    # Simple list of values
                    return [elem.text for elem in elements if elem.text]
            
        return value
    
    def _transform_response(self, data: Any, mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Transform response using mapping specification."""
        result = {}
        for key, spec in mapping.items():
            if isinstance(spec, dict):
                result[key] = self._apply_transform(data, spec)
            else:
                result[key] = self._extract_value(data, spec)
        return result
    
    async def _make_request(self, method: str, path: str, params: Dict[str, Any]) -> Any:
        """Make HTTP request with error handling."""
        if not self._http_client:
            raise ConnectorError("HTTP client not initialized")
            
        await self._rate_limiter.acquire()
        
        try:
            response = await self._http_client.request(
                method=method,
                path=path,
                params=params
            )
            return response
        except Exception as e:
            # Map errors based on specification
            error_mappings = self._spec.get("error_handling", {}).get("error_mappings", {})
            if hasattr(e, "status"):
                error_class = error_mappings.get(
                    str(e.status),
                    error_mappings.get("default", ConnectorError)
                )
                raise error_class(str(e))
            raise
    
    async def search(self, query: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Search using the configured endpoint."""
        endpoint_spec = self._spec.get("api", {}).get("endpoints", {}).get("search")
        if not endpoint_spec:
            raise ConnectorError("Search endpoint not configured")
            
        params = self._build_params(endpoint_spec["params"], {
            "query": query,
            "limit": limit,
            "api_key": self._config.get("api_key")
        })
        
        response = await self._make_request(
            method=endpoint_spec["method"],
            path=endpoint_spec["path"],
            params=params
        )
        
        return self._transform_response(response, endpoint_spec["response"]["mapping"])
    
    async def get_by_id(self, id: str) -> Dict[str, Any]:
        """Get document by ID using the configured endpoint."""
        endpoint_spec = self._spec.get("api", {}).get("endpoints", {}).get("get_document")
        if not endpoint_spec:
            raise ConnectorError("Get document endpoint not configured")
            
        params = self._build_params(endpoint_spec["params"], {
            "id": id,
            "api_key": self._config.get("api_key")
        })
        
        response = await self._make_request(
            method=endpoint_spec["method"],
            path=endpoint_spec["path"],
            params=params
        )
        
        return self._transform_response(response, endpoint_spec["response"]["mapping"])
    
    @property
    def name(self) -> str:
        """Get connector name from specification."""
        return self._spec.get("name", "unnamed")
    
    @property
    def capabilities(self) -> Dict[str, bool]:
        """Get connector capabilities."""
        return self._capabilities.copy() 