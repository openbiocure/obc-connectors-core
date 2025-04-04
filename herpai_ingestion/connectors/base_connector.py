from abc import ABC, abstractmethod
from typing import Dict, Any, Iterator

class BaseConnector(ABC):
    """Base interface for all source connectors."""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the source."""
        pass
    
    @abstractmethod
    def fetch_documents(self, query: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Fetch documents from the source."""
        pass 