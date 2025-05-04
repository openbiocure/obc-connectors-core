"""Europe PMC Connector Implementation."""

import os
import logging
from datetime import datetime
from typing import Optional, Union, Dict, Any, AsyncIterator, List

from herpai_connector_sdk.base_connector import BaseConnector

logger = logging.getLogger(__name__)

class EuropePMCConnector(BaseConnector):
    """YAML-driven connector for the Europe PMC API."""
    
    def __init__(self):
        """Initialize the connector."""
        super().__init__()
        spec_path = os.path.join(os.path.dirname(__file__), "connector.yaml")
        self.load_specification(spec_path)

    def _transform_integer(self, value: Union[str, int, float, None]) -> Optional[int]:
        """Transform a value into an integer.
        
        Args:
            value: The value to transform into an integer. Can be None, string, int, or float.
            
        Returns:
            Optional[int]: The transformed integer value or None if transformation fails
        """
        if value is None:
            return None
            
        try:
            if isinstance(value, str):
                clean_value = ''.join(c for c in value if c.isdigit() or c == '-')
                return int(clean_value) if clean_value else None
            return int(value)
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting to integer: {str(e)}")
            return None

    def _transform_date(self, date_str: str) -> Optional[datetime]:
        """Transform date string into a datetime object."""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing date: {str(e)}")
            return None

    def _transform_count_list(self, value: Any) -> Optional[int]:
        """Transform a list into its length.
        
        Args:
            value: A list or array-like object
            
        Returns:
            Optional[int]: The length of the list or None if input is not a list
        """
        try:
            if isinstance(value, (list, tuple)):
                return len(value)
            return None
        except Exception as e:
            logger.error(f"Error counting list items: {str(e)}")
            return None

    def _transform_extract_ids(self, results: List[Dict[str, Any]]) -> List[str]:
        """Extract IDs from a list of result objects.
        
        Args:
            results: List of result objects from Europe PMC API
            
        Returns:
            List[str]: List of extracted IDs
        """
        try:
            if not isinstance(results, list):
                return []
            return [result.get('id') for result in results if result.get('id')]
        except Exception as e:
            logger.error(f"Error extracting IDs: {str(e)}")
            return []

    async def authenticate(self, config: Dict[str, Any]) -> None:
        """Configure the connector with authentication.
        
        Args:
            config: Configuration dictionary that may contain:
                - api_key: Optional API key for Europe PMC
        """
        await super().authenticate(config)

    async def get_updates(self, since: datetime) -> AsyncIterator[Dict[str, Any]]:
        """Get updates since a specific date.
        
        Args:
            since: Date to get updates from
            
        Yields:
            Document data dictionaries
        """
        # Convert date to required format
        date_str = since.strftime("%Y-%m-%d")
        
        # Get updates using the configured endpoint
        results = await self.search(f"FIRST_PDATE:[{date_str} TO NOW]")
        
        # Process each document ID
        for doc_id in results.get('document_ids', []):
            try:
                document = await self.get_by_id(doc_id)
                if document:
                    yield document
            except Exception as e:
                logger.error(f"Error processing document {doc_id}: {str(e)}")
                continue 