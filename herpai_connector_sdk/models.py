"""Data models for the HerpAI Connector SDK."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

@dataclass
class Author:
    """Author data model."""
    name: str
    orcid: Optional[str] = None
    email: Optional[str] = None
    affiliation: Optional[str] = None

ContentType = Union[str, bytes, Dict[str, Any]]

@dataclass
class Document:
    """Document data model for connector responses."""
    id: str
    source: str
    title: str
    abstract: Optional[str] = None
    publication_date: Optional[datetime] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    authors: List[Author] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    document_type: str = "article"
    full_text: Optional[str] = None
    content: Optional[ContentType] = None
    metadata: Dict[str, Any] = field(default_factory=dict) 