"""Citation relationship between documents."""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import Optional
from openbiocure_corelib.data.entity import BaseEntity
from .document import Document

class Citation(BaseEntity):
    """Citation relationship between documents."""
    
    __tablename__ = "citations"
    
    citing_document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    cited_document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    context: Mapped[Optional[str]] = mapped_column(nullable=True)
    
    # Relationships
    citing_document: Mapped[Document] = relationship(
        foreign_keys=[citing_document_id],
        back_populates="citations"
    )
    cited_document: Mapped[Document] = relationship(
        foreign_keys=[cited_document_id],
        back_populates="cited_by"
    ) 