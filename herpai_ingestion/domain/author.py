"""Author entity representing a document author."""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import Optional, List
from openbiocure_corelib.data.entity import BaseEntity
from .document import Document

class Author(BaseEntity):
    """Author entity representing a document author."""
    
    __tablename__ = "authors"
    
    name: Mapped[str] = mapped_column(nullable=False)
    orcid: Mapped[Optional[str]] = mapped_column(nullable=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(nullable=True)
    affiliation: Mapped[Optional[str]] = mapped_column(nullable=True)
    
    # Relationships
    documents: Mapped[List[Document]] = relationship(
        secondary="document_authors",
        back_populates="authors"
    )

class DocumentAuthor(BaseEntity):
    """Junction table for document-author many-to-many relationship."""
    
    __tablename__ = "document_authors"
    
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    author_id: Mapped[str] = mapped_column(ForeignKey("authors.id"), nullable=False)
    author_position: Mapped[int] = mapped_column(nullable=False)
    is_corresponding: Mapped[bool] = mapped_column(nullable=False, default=False) 