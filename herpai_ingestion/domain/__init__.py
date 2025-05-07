"""Domain entities for the HerpAI-Ingestion system."""

from .document import Document
from .author import Author
from .entity_mention import EntityMention
from .citation import Citation
from .connector_execution import ConnectorExecution

__all__ = [
    'Document',
    'Author',
    'EntityMention',
    'Citation',
    'ConnectorExecution',
] 