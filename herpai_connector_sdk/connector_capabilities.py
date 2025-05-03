from enum import Enum, auto
from typing import Dict

class ConnectorCapability(Enum):
    """Enumeration of possible connector capabilities."""
    
    SUPPORTS_FULLTEXT = "supports_fulltext"
    SUPPORTS_ADVANCED_SEARCH = "supports_advanced_search"
    SUPPORTS_DATE_FILTERING = "supports_date_filtering"
    REQUIRES_AUTHENTICATION = "requires_authentication"
    SUPPORTS_BATCH_DOWNLOAD = "supports_batch_download"
    SUPPORTS_METADATA_ONLY = "supports_metadata_only"
    SUPPORTS_PDF_DOWNLOAD = "supports_pdf_download"
    SUPPORTS_CITATION_NETWORK = "supports_citation_network"
    SUPPORTS_AUTHOR_SEARCH = "supports_author_search"
    SUPPORTS_INCREMENTAL_UPDATES = "supports_incremental_updates"

    @classmethod
    def to_dict(cls, capabilities: set["ConnectorCapability"]) -> Dict[str, bool]:
        """Convert a set of capabilities to a dictionary.
        
        Args:
            capabilities: Set of ConnectorCapability values.
            
        Returns:
            Dict mapping capability names to boolean values.
        """
        return {cap.value: (cap in capabilities) for cap in cls} 