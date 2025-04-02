from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, JSON, Integer, DateTime, Text, Index
from typing import Optional, Dict, Any
from datetime import datetime

from herpai_lib.core.models.base import BaseEntity

class ScheduledJob(BaseEntity):
    """Scheduled job entity for automated ingestion tasks."""
    
    __tablename__ = "scheduled_jobs"
    
    # Job details
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    source: Mapped[str] = mapped_column(String, nullable=False, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    schedule: Mapped[str] = mapped_column(String, nullable=False)  # Cron expression
    
    # Job configuration
    max_results: Mapped[int] = mapped_column(Integer, default=1000)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Execution status
    last_run: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_run: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    running: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Statistics
    total_runs: Mapped[int] = mapped_column(Integer, default=0)
    total_documents: Mapped[int] = mapped_column(Integer, default=0)
    total_errors: Mapped[int] = mapped_column(Integer, default=0)
    
    # Additional configuration
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
