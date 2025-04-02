from .services.ingestion import IngestionService
from .connectors.pubmed import PubMedConnector
from .processors.grobid import GrobidProcessor
from .storage.s3 import S3Storage

def main():
    """Entry point for the ingestion pipeline."""
    service = IngestionService(
        connector=PubMedConnector(),
        processor=GrobidProcessor(),
        storage=S3Storage()
    )
    # Main application logic here

if __name__ == "__main__":
    main() 