from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, JSON, DateTime, Text, Index, ForeignKey
from typing import Optional, Dict, Any, List
from datetime import datetime

from herpai_lib.core.models.base import BaseEntity

class Document(BaseEntity):
    """Document entity representing a biomedical document."""
    
    __tablename__ = "documents"
    
    # Identifiers
    external_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Metadata
    title: Mapped[str] = mapped_column(String, nullable=False)
    authors: Mapped[str] = mapped_column(String, nullable=True)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    journal: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    doi: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    pmid: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    pmcid: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    
    # Content references
    full_text_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pdf_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    has_full_text: Mapped[bool] = mapped_column(Boolean, default=False)
    has_pdf: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Processing status
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_errors: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Additional data
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    keywords: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_document_source_external_id', 'source', 'external_id', unique=True),
    )
