from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseProcessor(ABC):
    """Base interface for all document processors."""
    
    @abstractmethod
    def process(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single document."""
        pass 