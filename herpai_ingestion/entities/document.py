from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class Document:
    """Represents a document in the system."""
    id: str
    title: str
    source: str
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime 