"""PubMed Connector Implementation."""

import os
import logging
import yaml
from datetime import datetime
from typing import Dict, Any, AsyncIterator, Optional, Union, cast, TypedDict
import xml.etree.ElementTree as ET

from herpai_connector_sdk.base_connector import BaseConnector

logger = logging.getLogger(__name__)

class ConnectorSpec(TypedDict, total=False):
    api: Dict[str, Dict[str, Any]]
    version: str

class PubMedConnector(BaseConnector):
    """YAML-driven connector for the PubMed/NCBI E-utilities API."""
    
    def __init__(self):
        super().__init__()
        spec_path = os.path.join(os.path.dirname(__file__), "connector.yaml")
        
        # Load YAML directly first for debugging
        with open(spec_path, 'r') as f:
            raw_spec = yaml.safe_load(f)
            logger.debug("Raw YAML content: %s", raw_spec)
            
        # Now load through the base class
        self.load_specification(spec_path)
        logger.debug(f"Loaded specification: {self._spec}")
        logger.debug(f"API endpoints: {self._spec.get('api', {}).get('endpoints', {})}")

    def _transform_integer(self, value: Union[str, int, float]) -> Optional[int]:
        """Transform a value into an integer."""
        try:
            if isinstance(value, str):
                # Remove any non-numeric characters (except negative sign)
                clean_value = ''.join(c for c in value if c.isdigit() or c == '-')
                return int(clean_value)
            return int(value)
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting to integer: {str(e)}")
            return None

    def _transform_pubmed_date_parser(self, element: ET.Element) -> Optional[datetime]:
        """Transform PubMed publication date XML element into a datetime object."""
        try:
            # Extract date components
            year = element.findtext(".//Year") or "1970"
            month = element.findtext(".//Month") or "1"
            day = element.findtext(".//Day") or "1"

            # Handle month names
            if isinstance(month, str) and not month.isdigit():
                month_map = {
                    "Jan": "1", "Feb": "2", "Mar": "3", "Apr": "4",
                    "May": "5", "Jun": "6", "Jul": "7", "Aug": "8",
                    "Sep": "9", "Oct": "10", "Nov": "11", "Dec": "12"
                }
                month = month_map.get(month[:3], "1")

            return datetime(int(year), int(month), int(day))
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error parsing PubMed date: {str(e)}")
            return None

    def _transform_pubmed_author_name(self, element: ET.Element) -> Optional[Dict[str, Optional[str]]]:
        """Transform PubMed author element into a structured author object."""
        try:
            last_name = element.findtext("LastName") or ""
            fore_name = element.findtext("ForeName") or ""
            affiliation = element.findtext(".//Affiliation")
            
            return {
                "name": f"{last_name}, {fore_name}".strip(", "),
                "affiliation": affiliation if affiliation else None
            }
        except (AttributeError, TypeError) as e:
            logger.error(f"Error formatting author data: {str(e)}")
            return None

    def _transform_pubmed_keywords(self, element: ET.Element) -> list[str]:
        """Transform PubMed keywords into a list of strings."""
        try:
            return [kw.text.strip() for kw in element.findall(".//Keyword") if kw.text and kw.text.strip()]
        except (AttributeError, TypeError) as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []
    
    async def authenticate(self, config: Dict[str, Any]) -> None:
        """Configure the connector with authentication."""
        self.configure(config)
    
    async def get_updates(self, since: datetime) -> AsyncIterator[Dict[str, Any]]:
        """Get updates since a specific date."""
        # Convert date to PubMed format (YYYY/MM/DD)
        date_str = since.strftime("%Y/%m/%d")
        
        # Get updates using the configured endpoint
        results = await self.search(f"(\"0001\"[EDAT] : \"{date_str}\"[EDAT])")
        
        # Process documents in batches
        for doc_id in results["document_ids"]:
            try:
                document = await self.get_by_id(doc_id)
                yield document
            except Exception as e:
                logger.error(f"Error processing document {doc_id}: {str(e)}")
                continue 