from typing import Protocol, List, Optional
from datetime import datetime

from herpai_lib.core.repositories import IRepository
from src.models.scheduled_job import ScheduledJob

class IScheduledJobRepository(IRepository[ScheduledJob], Protocol):
    """Repository interface for ScheduledJob entities."""
    
    async def find_by_name(self, name: str) -> Optional[ScheduledJob]:
        """Find a scheduled job by name."""
        ...
    
    async def find_enabled(self) -> List[ScheduledJob]:
        """Find all enabled scheduled jobs."""
        ...
    
    async def find_due(self, reference_time: datetime = None) -> List[ScheduledJob]:
        """Find scheduled jobs that are due to run."""
        ...
    
    async def find_running(self) -> List[ScheduledJob]:
        """Find currently running scheduled jobs."""
        ...
    
    async def mark_as_running(self, job_id: str, running: bool = True) -> ScheduledJob:
        """Mark a job as running or not running."""
        ...
    
    async def update_run_stats(self, job_id: str, documents_count: int, 
                              error_count: int = 0) -> ScheduledJob:
        """Update job run statistics."""
        ...
    
    async def update_next_run(self, job_id: str, next_run: datetime) -> ScheduledJob:
        """Update the next run time for a job."""
        ...
