from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class Document:
    """Represents a document in the system."""
    id: str
    title: str
    source: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    # Storage Configuration
    storage_config: Dict[str, Any] = field(default_factory=lambda: {
        "provider": "s3",  # s3, azure, minio
        "bucket": "herpai-datalake",
        "region": "us-east-1",  # for S3/MinIO
        "endpoint": None,  # for MinIO or custom endpoints
        "prefix": "documents/",  # optional prefix for all paths
        "custom_options": {}  # provider-specific options
    })
    
    # Content Locations (relative to bucket/container)
    abstract_path: Optional[str] = None
    full_text_path: Optional[str] = None
    pdf_path: Optional[str] = None
    
    # Content Status
    has_abstract: bool = False
    has_full_text: bool = False
    has_pdf: bool = False
    
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
    