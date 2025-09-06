"""Simple base connector without YAML complexity."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """Simple base connector with common functionality."""

    def __init__(self, base_url: str, rate_limit: int = 10):
        self.base_url = base_url
        self.rate_limit = rate_limit
        self._http_client = None
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    def http_client(self):
        """Lazy initialization of HTTP client."""
        if self._http_client is None:
            self._http_client = aiohttp.ClientSession()
        return self._http_client

    async def make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request with rate limiting."""
        url = f"{self.base_url}{endpoint}"

        try:
            async with self.http_client.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            raise

    def extract_text(self, data: Dict[str, Any], path: str) -> Optional[str]:
        """Extract text from response using dot notation."""
        try:
            keys = path.split(".")
            value = data
            for key in keys:
                value = value[key]
            return str(value) if value is not None else None
        except (KeyError, TypeError):
            return None

    def extract_list(self, data: Dict[str, Any], path: str) -> List[str]:
        """Extract list from response using dot notation."""
        try:
            keys = path.split(".")
            value = data
            for key in keys:
                value = value[key]
            return value if isinstance(value, list) else []
        except (KeyError, TypeError):
            return []

    @abstractmethod
    async def search(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search for papers/documents."""
        pass

    @abstractmethod
    async def get_by_id(self, doc_id: str) -> Dict[str, Any]:
        """Get document by ID."""
        pass

    async def close(self):
        """Close HTTP client."""
        if self._http_client is not None:
            await self._http_client.close()
            self._http_client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import asyncio

        asyncio.create_task(self.close())
