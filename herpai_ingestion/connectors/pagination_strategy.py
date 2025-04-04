from abc import ABC, abstractmethod
from typing import Dict, Any

from .pagination_state import PaginationState

class PaginationStrategy(ABC):
    """Interface for different pagination strategies."""
    
    @abstractmethod
    async def initialize(self, query: str) -> PaginationState:
        """Initialize pagination state for a query."""
        pass
    
    @abstractmethod
    async def get_next_page(self, state: PaginationState) -> Dict[str, Any]:
        """Get parameters for fetching the next page."""
        pass
    
    @abstractmethod
    async def update_state(self, state: PaginationState, response_data: Dict[str, Any]) -> PaginationState:
        """Update pagination state based on response data."""
        pass 