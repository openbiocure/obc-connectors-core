from typing import Protocol, List, Optional
from datetime import datetime

from herpai_lib.core.repositories import IRepository
from src.models.ingestion_state import IngestionState

class IIngestionStateRepository(IRepository[IngestionState], Protocol):
    """Repository interface for IngestionState entities."""
    
    async def find_by_job_id(self, job_id: str) -> Optional[IngestionState]:
        """Find an ingestion state by job ID."""
        ...
    
    async def find_active(self) -> List[IngestionState]:
        """Find all active ingestion states (running or pending)."""
        ...
    
    async def find_by_status(self, status: str) -> List[IngestionState]:
        """Find ingestion states by status."""
        ...
    
    async def update_status(self, state_id: str, status: str, 
                          error_message: Optional[str] = None) -> IngestionState:
        """Update the status of an ingestion state."""
        ...
    
    async def update_checkpoint(self, state_id: str, checkpoint: dict, 
                              current_page: int, last_id: Optional[str] = None) -> IngestionState:
        """Update the checkpoint of an ingestion state."""
        ...
    
    async def increment_retry(self, state_id: str) -> IngestionState:
        """Increment the retry count of an ingestion state."""
        ...
    
    async def update_progress(self, state_id: str, documents_processed: int, 
                            documents_total: Optional[int] = None) -> IngestionState:
        """Update the progress of an ingestion state."""
        ...
