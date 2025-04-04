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
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    journal: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    doi: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    pmid: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    pmcid: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    
    # Storage Configuration
    storage_config: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=lambda: {
        "provider": "s3",  # s3, azure, minio
        "bucket": "herpai-datalake",
        "region": "us-east-1",  # for S3/MinIO
        "endpoint": None,  # for MinIO or custom endpoints
        "prefix": "documents/",  # optional prefix for all paths
        "custom_options": {}  # provider-specific options
    })
    
    # Content Locations (relative to bucket/container)
    abstract_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    full_text_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pdf_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Content Status
    has_abstract: Mapped[bool] = mapped_column(Boolean, default=False)
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
    
    def _get_full_path(self, path: Optional[str]) -> Optional[str]:
        """Get the full path including any configured prefix."""
        if not path:
            return None
        prefix = self.storage_config.get("prefix", "").rstrip("/")
        if prefix:
            return f"{prefix}/{path}"
        return path
    
    @property
    def abstract_url(self) -> Optional[str]:
        """Get the full URL for the abstract."""
        if not self.abstract_path:
            return None
        
        provider = self.storage_config["provider"]
        bucket = self.storage_config["bucket"]
        path = self._get_full_path(self.abstract_path)
        
        if provider == "minio" and self.storage_config.get("endpoint"):
            return f"{self.storage_config['endpoint']}/{bucket}/{path}"
        
        return f"{provider}://{bucket}/{path}"
    
    @property
    def full_text_url(self) -> Optional[str]:
        """Get the full URL for the full text."""
        if not self.full_text_path:
            return None
            
        provider = self.storage_config["provider"]
        bucket = self.storage_config["bucket"]
        path = self._get_full_path(self.full_text_path)
        
        if provider == "minio" and self.storage_config.get("endpoint"):
            return f"{self.storage_config['endpoint']}/{bucket}/{path}"
        
        return f"{provider}://{bucket}/{path}"
    
    @property
    def pdf_url(self) -> Optional[str]:
        """Get the full URL for the PDF."""
        if not self.pdf_path:
            return None
            
        provider = self.storage_config["provider"]
        bucket = self.storage_config["bucket"]
        path = self._get_full_path(self.pdf_path)
        
        if provider == "minio" and self.storage_config.get("endpoint"):
            return f"{self.storage_config['endpoint']}/{bucket}/{path}"
        
        return f"{provider}://{bucket}/{path}"
