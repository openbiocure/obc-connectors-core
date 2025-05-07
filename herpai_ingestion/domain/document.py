"""Document entity representing a biomedical document."""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import Optional, List
from datetime import datetime
from herpai_ingestion.domain.citation import Citation
from openbiocure_corelib.data.entity import BaseEntity
from .author import Author
from .entity_mention import EntityMention

class Document(BaseEntity):
    """Document entity representing a biomedical document."""
    
    __tablename__ = "documents"
    
    source: Mapped[str] = mapped_column(nullable=False)
    source_id: Mapped[str] = mapped_column(nullable=False, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(nullable=True)
    publication_date: Mapped[datetime] = mapped_column(nullable=False)
    doi: Mapped[Optional[str]] = mapped_column(nullable=True, index=True)
    url: Mapped[Optional[str]] = mapped_column(nullable=True)
    document_type: Mapped[str] = mapped_column(nullable=False)
    processing_status: Mapped[str] = mapped_column(nullable=False)
    storage_path: Mapped[Optional[str]] = mapped_column(nullable=True)
    
    # Relationships
    authors: Mapped[List["Author"]] = relationship(
        secondary="document_authors",
        back_populates="documents"
    )
    entity_mentions: Mapped[List["EntityMention"]] = relationship(back_populates="document")
    citations: Mapped[List["Citation"]] = relationship(
        foreign_keys="Citation.citing_document_id",
        back_populates="citing_document"
    )
    cited_by: Mapped[List["Citation"]] = relationship(
        foreign_keys="Citation.cited_document_id",
        back_populates="cited_document"
    ) 