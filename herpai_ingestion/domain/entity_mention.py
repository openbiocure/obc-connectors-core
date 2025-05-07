"""Entity mention in a document."""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from openbiocure_corelib.data.entity import BaseEntity
from .document import Document

class EntityMention(BaseEntity):
    """Entity mention in a document."""
    
    __tablename__ = "entity_mentions"
    
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    entity_type: Mapped[str] = mapped_column(nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(nullable=False, index=True)
    text: Mapped[str] = mapped_column(nullable=False)
    start_offset: Mapped[int] = mapped_column(nullable=False)
    end_offset: Mapped[int] = mapped_column(nullable=False)
    confidence: Mapped[float] = mapped_column(nullable=False)
    
    # Relationships
    document: Mapped[Document] = relationship(back_populates="entity_mentions") 