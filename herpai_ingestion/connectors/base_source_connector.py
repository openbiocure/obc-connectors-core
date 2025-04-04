from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncIterator
import logging

from src.models.document import Document
from .pagination_strategy import PaginationStrategy

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