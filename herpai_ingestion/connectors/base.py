from typing import Protocol, List, Dict, Any, Optional, AsyncIterator, Iterator
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import aiohttp
from datetime import datetime

from src.models.document import Document

@dataclass
class PaginationState:
    """State of pagination for a source."""
    
    page: int = 1
    page_size: int = 100
    total_pages: Optional[int] = None
    total_results: Optional[int] = None
    last_id: Optional[str] = None
    has_more: bool = True
    metadata: Dict[str, Any] = None

class PaginationStrategy(ABC):
    """Interface for different pagination strategies."""
    
    @abstractmethod
    async def initialize(self, query: str) -> PaginationState:
        """Initialize pagination state for a query."""
        pass
    
    @abstractmethod
    async def get_next_page(self, state: PaginationState) -> Dict[str, Any]:
        """Get parameters for fetching the next page."""
        pass
    
    @abstractmethod
    async def update_state(self, state: PaginationState, response_data: Dict[str, Any]) -> PaginationState:
        """Update pagination state based on response data."""
        pass

class BaseSourceConnector(ABC):
    """Base connector for data sources."""
    
    def __init__(self, config: Dict[str, Any], pagination_strategy: Optional[PaginationStrategy] = None):
        """Initialize the connector with configuration."""
        self.config = config
        self.pagination_strategy = pagination_strategy
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def search(self, query: str, limit: int = 100) -> AsyncIterator[Document]:
        """Search for documents matching a query."""
        pass
    
    @abstractmethod
    async def get_document(self, id: str) -> Optional[Document]:
        """Get a specific document by ID."""
        pass
    
    @abstractmethod
    async def download_pdf(self, document: Document) -> Optional[str]:
        """Download PDF for a document, returns path to saved PDF."""
        pass
    
    @abstractmethod
    async def get_source_name(self) -> str:
        """Get the name of the source."""
        pass

class BaseConnector(ABC):
    """Base interface for all source connectors."""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the source."""
        pass
    
    @abstractmethod
    def fetch_documents(self, query: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Fetch documents from the source."""
        pass
