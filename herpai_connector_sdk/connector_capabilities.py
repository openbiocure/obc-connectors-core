from enum import Enum, auto
from typing import Dict

class ConnectorCapability(Enum):
    """Enumeration of possible connector capabilities.
    
    This enum defines the standard set of capabilities that a connector can support.
    Each capability represents a specific feature or functionality that the connector
    may implement. These capabilities are used for:
    
    1. Feature discovery and validation
    2. Runtime behavior decisions
    3. API documentation and client expectations
    4. Configuration validation
    """
    
    SUPPORTS_FULLTEXT = "supports_fulltext"
    """Indicates if the connector can retrieve full text content of documents.
    When True, the connector can fetch complete document content beyond just metadata.
    This is important for text mining and content analysis use cases."""
    
    SUPPORTS_ADVANCED_SEARCH = "supports_advanced_search"
    """Indicates if the connector supports complex search queries.
    This may include boolean operators, field-specific searches, wildcards,
    proximity searches, etc. Useful for precise document retrieval."""
    
    SUPPORTS_DATE_FILTERING = "supports_date_filtering"
    """Indicates if the connector can filter results by date ranges.
    This allows temporal queries like "documents published between dates",
    "updated since date", etc. Essential for incremental updates."""
    
    REQUIRES_AUTHENTICATION = "requires_authentication"
    """Indicates if the connector requires authentication to access the data source.
    When True, valid credentials must be provided before the connector can be used.
    This affects initialization and error handling behavior."""
    
    SUPPORTS_BATCH_DOWNLOAD = "supports_batch_download"
    """Indicates if the connector can efficiently download multiple documents at once.
    This capability suggests optimized bulk operations are available,
    which can improve performance for large-scale data ingestion."""
    
    SUPPORTS_METADATA_ONLY = "supports_metadata_only"
    """Indicates if the connector can retrieve only metadata without full content.
    This is useful for initial scanning, preview generation, and when full
    content download is not needed or too resource-intensive."""
    
    SUPPORTS_PDF_DOWNLOAD = "supports_pdf_download"
    """Indicates if the connector can download documents in PDF format.
    This is important for sources that provide documents in multiple formats
    and when preservation of original formatting is required."""
    
    SUPPORTS_CITATION_NETWORK = "supports_citation_network"
    """Indicates if the connector can retrieve citation relationships.
    This includes both cited and citing documents, enabling citation
    network analysis and academic impact tracking."""
    
    SUPPORTS_AUTHOR_SEARCH = "supports_author_search"
    """Indicates if the connector supports searching by author information.
    This enables finding documents by author names, affiliations, or
    author identifiers like ORCID."""
    
    SUPPORTS_INCREMENTAL_UPDATES = "supports_incremental_updates"
    """Indicates if the connector can efficiently fetch only new or updated documents.
    This is crucial for maintaining up-to-date document collections without
    downloading everything again."""

    SUPPORTS_NATIVE_PAGINATION = "supports_native_pagination"
    """Indicates if the connector supports native pagination from the data source.
    When True, the connector can use the source's built-in pagination mechanisms
    (like cursor-based or offset-based pagination) for efficient data retrieval.
    This is crucial for:
    - Memory-efficient processing of large result sets
    - Respecting rate limits and resource constraints
    - Implementing reliable resumable downloads
    - Maintaining consistent ordering across pages"""

    @classmethod
    def to_dict(cls, capabilities: set["ConnectorCapability"]) -> Dict[str, bool]:
        """Convert a set of capabilities to a dictionary.
        
        This method is useful for serializing capabilities to configuration files
        or API responses. It creates a standardized representation where each
        capability is mapped to a boolean indicating if it's supported.
        
        Args:
            capabilities: Set of ConnectorCapability values representing
                         the active capabilities.
            
        Returns:
            Dict mapping capability names (as strings) to boolean values,
            where True indicates the capability is supported.
            
        Example:
            >>> caps = {ConnectorCapability.SUPPORTS_FULLTEXT, 
            ...        ConnectorCapability.REQUIRES_AUTHENTICATION}
            >>> ConnectorCapability.to_dict(caps)
            {
                'supports_fulltext': True,
                'requires_authentication': True,
                'supports_advanced_search': False,
                ...
            }
        """
        return {cap.value: (cap in capabilities) for cap in cls} 