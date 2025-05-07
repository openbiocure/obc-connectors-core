"""Base implementation for YAML-driven connectors."""

import os
import logging
import json
import xml.etree.ElementTree as ET
import yaml
from typing import Dict, Any, Optional, List, Union, Callable, cast
from datetime import datetime
from dynaconf import Dynaconf
from aiohttp import ClientResponseError
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
        self._config: Dict[str, Any] = {}
        self._capabilities = {
            capability.name: False for capability in ConnectorCapability
        }
        self._settings = None
        self._http_client = None
        self._rate_limiter = RateLimiter(3.0)  # Default rate limit
        self._spec: Dict[str, Any] = {}
    
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
            rate_limit = self._spec.get("api", {}).get("rate_limit", {}).get("with_api_key", 10)
            # Convert rate limit to float if it's a string
            if isinstance(rate_limit, str):
                try:
                    # Remove any ${...} template syntax
                    rate_limit = rate_limit.split("|")[-1].rstrip("}")
                    rate_limit = float(rate_limit)
                except (ValueError, IndexError):
                    logger.warning(f"Invalid rate limit value: {rate_limit}, using default of 10")
                    rate_limit = 10.0
            
            self._rate_limiter.requests_per_second = float(rate_limit)
    
    def load_specification(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Load and process the YAML specification."""
        if not path:
            module_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(module_dir, "connector.yaml")
        
        logger.info(f"Loading specification from: {path}")
        
        if not os.path.exists(path):
            logger.warning(f"Specification file not found: {path}")
            return {}
        
        try:
            # Load YAML directly first
            with open(path, 'r') as f:
                raw_spec = cast(Dict[str, Any], yaml.safe_load(f))
                logger.debug(f"Raw YAML content: {raw_spec}")
            
            # Initialize Dynaconf with the YAML file
            settings = Dynaconf(
                settings_files=[path],
                environments=True,
                env_prefix="HERPAI_",
                lowercase_read=True,
                merge_enabled=True
            )
            
            self._settings = settings
            
            # Store both raw and processed configurations
            self._spec = raw_spec
            
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
                logger.debug(f"Processing base URL template: {base_url}")
                # Handle template URLs
                if isinstance(base_url, str) and "|" in base_url:
                    try:
                        # Extract default value after the | character
                        base_url = base_url.split("|")[1].rstrip("}")
                        logger.debug(f"Extracted base URL: {base_url}")
                    except (IndexError, ValueError):
                        logger.warning(f"Invalid base URL format: {base_url}")
                        raise ValueError("Invalid base URL format in connector specification")
                
                self._http_client = HTTPClient(base_url)
                logger.info(f"Initialized HTTP client with base URL: {base_url}")
            
            # Initialize rate limiter
            rate_limit = self._spec.get("api", {}).get("rate_limit", {}).get("requests_per_second", 3)
            # Convert rate limit to float if it's a string
            if isinstance(rate_limit, str):
                try:
                    # Remove any ${...} template syntax
                    rate_limit = rate_limit.split("|")[-1].rstrip("}")
                    rate_limit = float(rate_limit)
                except (ValueError, IndexError):
                    logger.warning(f"Invalid rate limit value: {rate_limit}, using default of 3")
                    rate_limit = 3.0
            
            self._rate_limiter = RateLimiter(float(rate_limit))
            
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
    
    def _get_transform_function(self, name: str) -> Optional[Callable[[Any], Any]]:
        """Dynamically resolve a transform name to a method on the current connector instance."""
        transform_method_name = f"_transform_{name}"
        if hasattr(self, transform_method_name):
            return getattr(self, transform_method_name)
        logger.warning(f"Transform function {transform_method_name} not found")
        return None

    def _apply_transform(self, data: Any, transform_spec: Dict[str, Any]) -> Any:
        """Apply transformation to extracted value."""
        # Handle string-based transform references
        if isinstance(transform_spec, str):
            transform_func = self._get_transform_function(transform_spec)
            if transform_func:
                return transform_func(data)
            return data

        # Handle dictionary transform specs
        if isinstance(transform_spec, dict):
            # Extract value if path is specified
            value = self._extract_value(data, transform_spec["path"]) if "path" in transform_spec else data
            
            # Handle transform field
            if "transform" in transform_spec:
                # If transform is a string, treat it as a transform function name
                if isinstance(transform_spec["transform"], str):
                    transform_func = self._get_transform_function(transform_spec["transform"])
                    if transform_func:
                        return transform_func(value)
                    return value
                
                # Legacy dictionary transform handling
                elif isinstance(transform_spec["transform"], dict):
                    transform_type = transform_spec["transform"].get("type")
                    if transform_type:
                        # Try to resolve named transform
                        transform_func = self._get_transform_function(transform_type)
                        if transform_func:
                            return transform_func(value)
                        
                        # Legacy date transform handling
                        if transform_type == "date" and isinstance(value, str):
                            if all(k in transform_spec["transform"] for k in ["year", "month", "day"]):
                                try:
                                    year = self._extract_value(data, transform_spec["transform"]["year"]) or "1970"
                                    month = self._extract_value(data, transform_spec["transform"]["month"].split("|")[0]) or "1"
                                    day = self._extract_value(data, transform_spec["transform"]["day"].split("|")[0]) or "1"
                                    
                                    # Handle month names if provided
                                    month_names = transform_spec["transform"].get("month_names", {})
                                    if month in month_names:
                                        month = str(month_names[month])
                                    
                                    return datetime(int(year), int(month), int(day))
                                except (ValueError, TypeError) as e:
                                    logger.error(f"Error parsing date: {str(e)}")
                                    return None
            
            # Handle list transforms
            if transform_spec.get("list", False):
                if isinstance(data, ET.Element):
                    elements = data.findall(transform_spec["path"])
                    if "transform" in transform_spec:
                        # Apply transform to each element
                        results = []
                        for elem in elements:
                            if isinstance(transform_spec["transform"], str):
                                transform_func = self._get_transform_function(transform_spec["transform"])
                                if transform_func:
                                    result = transform_func(elem)
                                    if result is not None:
                                        results.append(result)
                            elif isinstance(transform_spec["transform"], dict):
                                # Legacy transform handling for lists
                                result = self._apply_transform(elem, {"transform": transform_spec["transform"]})
                                if result is not None:
                                    results.append(result)
                        return results
                    else:
                        # Simple list of text values
                        return [elem.text.strip() for elem in elements if elem.text and elem.text.strip()]
            
            # Return extracted value if no transform applied
            return value
            
        return data
    
    def _transform_response(self, data: Any, response_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Transform response using mapping specification.
        
        Args:
            data: Raw response data
            response_spec: Response specification from YAML including data_path and mapping
            
        Returns:
            Transformed response data
        """
        result = {}
        
        # Log raw response for debugging
        logger.debug(f"Raw response data: {data}")
        logger.debug(f"Response spec: {response_spec}")
        
        # Get data from specified path if provided
        if "data_path" in response_spec:
            data_parts = response_spec["data_path"].split(".")
            current_data = data
            for part in data_parts:
                if isinstance(current_data, dict):
                    logger.debug(f"Navigating to {part} in {current_data.keys()}")
                    current_data = current_data.get(part)
                    if current_data is None:
                        logger.error(f"Could not find data at path: {response_spec['data_path']}")
                        return {}
                else:
                    logger.error(f"Invalid data structure at path: {response_spec['data_path']}, got {type(current_data)}")
                    return {}
            data = current_data
            logger.debug(f"Data after path navigation: {data}")

        # Process mapping
        mapping = response_spec.get("mapping", {})
        logger.debug(f"Processing mapping: {mapping}")
        for key, spec in mapping.items():
            try:
                if isinstance(spec, dict):
                    if "template" in spec:
                        # Handle template strings
                        result[key] = spec["template"].format(**self._config)
                        logger.debug(f"Applied template for {key}: {result[key]}")
                    else:
                        # Handle transforms and paths
                        result[key] = self._apply_transform(data, spec)
                        logger.debug(f"Applied transform for {key}: {result[key]}")
                else:
                    # Direct path mapping
                    result[key] = self._extract_value(data, spec)
                    logger.debug(f"Extracted value for {key}: {result[key]}")
            except Exception as e:
                logger.error(f"Error transforming field {key}: {str(e)}")
                result[key] = None

        logger.debug(f"Final transformed result: {result}")
        return result
    
    async def _make_request(self, method: str, path: str, params: Dict[str, Any]) -> Any:
        """Make HTTP request with error handling."""
        if not self._http_client:
            raise ConnectorError("HTTP client not initialized")
            
        await self._rate_limiter.acquire()
        
        try:
            if method.upper() != "GET":
                raise ConnectorError(f"Unsupported HTTP method: {method}")
            
            response = await self._http_client.get(
                path=path,
                params=params
            )
            return response
        except ClientResponseError as e:
            # Map errors based on specification
            error_mappings = self._spec.get("error_handling", {}).get("error_mappings", {})
            error_class = error_mappings.get(
                str(e.status),
                error_mappings.get("default", ConnectorError)
            )
            raise error_class(str(e))
        except Exception as e:
            raise ConnectorError(str(e))
    
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
        
        # Transform response using the response specification
        return self._transform_response(response, endpoint_spec["response"])
    
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