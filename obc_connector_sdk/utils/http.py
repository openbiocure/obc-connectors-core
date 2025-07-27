"""HTTP client utility for connectors."""

import aiohttp
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class HTTPClient:
    """HTTP client utility for connectors."""
    
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.session = None
    
    async def ensure_session(self):
        """Ensure an aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
    
    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        await self.ensure_session()
        url = f"{self.base_url}/{path.lstrip('/')}"
        
        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP error: {e.status} - {e.message}")
            raise
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            raise 