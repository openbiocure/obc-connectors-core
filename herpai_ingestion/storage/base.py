from abc import ABC, abstractmethod
from typing import BinaryIO, Optional

class BaseStorage(ABC):
    """Base interface for all storage implementations."""
    
    @abstractmethod
    def upload(self, file_path: str, data: BinaryIO) -> str:
        """Upload a file to storage."""
        pass
    
    @abstractmethod
    def download(self, file_path: str) -> Optional[BinaryIO]:
        """Download a file from storage."""
        pass 