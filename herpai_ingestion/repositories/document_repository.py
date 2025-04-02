from typing import Protocol, List, Optional
from datetime import datetime

from herpai_lib.core.repositories import IRepository
from src.models.document import Document

class IDocumentRepository(IRepository[Document], Protocol):
    """Repository interface for Document entities."""
    
    async def find_by_external_id(self, source: str, external_id: str) -> Optional[Document]:
        """Find a document by source and external ID."""
        ...
    
    async def find_by_doi(self, doi: str) -> Optional[Document]:
        """Find a document by DOI."""
        ...
    
    async def find_by_pmid(self, pmid: str) -> Optional[Document]:
        """Find a document by PubMed ID."""
        ...
    
    async def find_by_pmcid(self, pmcid: str) -> Optional[Document]:
        """Find a document by PubMed Central ID."""
        ...
    
    async def find_unprocessed(self, limit: int = 100) -> List[Document]:
        """Find unprocessed documents."""
        ...
    
    async def find_by_source(self, source: str, limit: int = 100, offset: int = 0) -> List[Document]:
        """Find documents by source."""
        ...
    
    async def find_by_date_range(self, start_date: datetime, end_date: datetime, 
                                limit: int = 100, offset: int = 0) -> List[Document]:
        """Find documents by publication date range."""
        ...
    
    async def search(self, query: str, limit: int = 100, offset: int = 0) -> List[Document]:
        """Search documents by title or abstract."""
        ...
