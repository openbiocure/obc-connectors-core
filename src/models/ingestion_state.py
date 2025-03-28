from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, JSON, Integer, DateTime, Text, Index
from typing import Optional, Dict, Any
from datetime import datetime

from herpai_lib.core.models.base import BaseEntity

class IngestionState(BaseEntity):
    """Entity for tracking ingestion state and checkpoints."""
    
    __tablename__ = "ingestion_states"
    
    # Job identification
    job_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Pagination state
    current_page: Mapped[int] = mapped_column(Integer, default=1)
    page_size: Mapped[int] = mapped_column(Integer, default=100)
    total_pages: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_results: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Progress tracking
    documents_processed: Mapped[int] = mapped_column(Integer, default=0)
    documents_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, running, completed, failed
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Checkpoint data
    checkpoint: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    last_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Error details
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retries: Mapped[int] = mapped_column(Integer, default=0)
