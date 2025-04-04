from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class PaginationState:
    """State of pagination for a source."""
    
    page: int = 1
    page_size: int = 100
    total_pages: Optional[int] = None
    total_results: Optional[int] = None
    last_id: Optional[str] = None
    has_more: bool = True
    metadata: Dict[str, Any] = None 