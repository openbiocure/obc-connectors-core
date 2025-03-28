#!/bin/bash

# Script to extend HerpAI-Lib with biomedical data ingestion functionality
# Author: OpenBioCure
# Usage: ./scafold_fixed.sh

set -e  # Exit on error

echo "Setting up HerpAI-Ingestion by extending HerpAI-Lib"

# Create initial directory structure
mkdir -p src/{cli,connectors,processors,storage,services,scheduler}
touch src/__init__.py
touch src/{cli,connectors,processors,storage,services,scheduler}/__init__.py

# Create biomedical entity models extending BaseEntity
mkdir -p src/models
cat > src/models/__init__.py << 'EOF'
from src.models.document import Document
from src.models.ingestion_state import IngestionState
from src.models.scheduled_job import ScheduledJob

__all__ = ["Document", "IngestionState", "ScheduledJob"]
EOF

cat > src/models/document.py << 'EOF'
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, JSON, DateTime, Text, Index, ForeignKey
from typing import Optional, Dict, Any, List
from datetime import datetime

from herpai_lib.core.models.base import BaseEntity

class Document(BaseEntity):
    """Document entity representing a biomedical document."""
    
    __tablename__ = "documents"
    
    # Identifiers
    external_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Metadata
    title: Mapped[str] = mapped_column(String, nullable=False)
    authors: Mapped[str] = mapped_column(String, nullable=True)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    journal: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    doi: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    pmid: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    pmcid: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    
    # Content references
    full_text_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pdf_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    has_full_text: Mapped[bool] = mapped_column(Boolean, default=False)
    has_pdf: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Processing status
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_errors: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Additional data
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    keywords: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_document_source_external_id', 'source', 'external_id', unique=True),
    )
EOF

cat > src/models/ingestion_state.py << 'EOF'
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, JSON, Integer, DateTime, Text, Index
from typing import Optional, Dict, Any
from datetime import datetime

from herpai_lib.core.models.base import BaseEntity

class IngestionState(BaseEntity):
    """Entity for tracking ingestion state and checkpoints."""
    
    __tablename__ = "ingestion_states"
    
    # Job identification
    job_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Pagination state
    current_page: Mapped[int] = mapped_column(Integer, default=1)
    page_size: Mapped[int] = mapped_column(Integer, default=100)
    total_pages: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_results: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Progress tracking
    documents_processed: Mapped[int] = mapped_column(Integer, default=0)
    documents_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, running, completed, failed
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Checkpoint data
    checkpoint: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    last_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Error details
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retries: Mapped[int] = mapped_column(Integer, default=0)
EOF

cat > src/models/scheduled_job.py << 'EOF'
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, JSON, Integer, DateTime, Text, Index
from typing import Optional, Dict, Any
from datetime import datetime

from herpai_lib.core.models.base import BaseEntity

class ScheduledJob(BaseEntity):
    """Scheduled job entity for automated ingestion tasks."""
    
    __tablename__ = "scheduled_jobs"
    
    # Job details
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    source: Mapped[str] = mapped_column(String, nullable=False, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    schedule: Mapped[str] = mapped_column(String, nullable=False)  # Cron expression
    
    # Job configuration
    max_results: Mapped[int] = mapped_column(Integer, default=1000)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Execution status
    last_run: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_run: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    running: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Statistics
    total_runs: Mapped[int] = mapped_column(Integer, default=0)
    total_documents: Mapped[int] = mapped_column(Integer, default=0)
    total_errors: Mapped[int] = mapped_column(Integer, default=0)
    
    # Additional configuration
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
EOF

# Create repository interfaces (just the custom methods, base methods from IRepository)
mkdir -p src/repositories
cat > src/repositories/__init__.py << 'EOF'
from src.repositories.document_repository import IDocumentRepository
from src.repositories.ingestion_state_repository import IIngestionStateRepository
from src.repositories.scheduled_job_repository import IScheduledJobRepository
from src.repositories.specifications import *

__all__ = [
    "IDocumentRepository",
    "IIngestionStateRepository",
    "IScheduledJobRepository"
]
EOF

cat > src/repositories/document_repository.py << 'EOF'
from typing import Protocol, List, Optional
from datetime import datetime

from herpai_lib.core.repositories import IRepository
from src.models.document import Document

class IDocumentRepository(IRepository[Document], Protocol):
    """Repository interface for Document entities."""
    
    async def find_by_external_id(self, source: str, external_id: str) -> Optional[Document]:
        """Find a document by source and external ID."""
        ...
    
    async def find_by_doi(self, doi: str) -> Optional[Document]:
        """Find a document by DOI."""
        ...
    
    async def find_by_pmid(self, pmid: str) -> Optional[Document]:
        """Find a document by PubMed ID."""
        ...
    
    async def find_by_pmcid(self, pmcid: str) -> Optional[Document]:
        """Find a document by PubMed Central ID."""
        ...
    
    async def find_unprocessed(self, limit: int = 100) -> List[Document]:
        """Find unprocessed documents."""
        ...
    
    async def find_by_source(self, source: str, limit: int = 100, offset: int = 0) -> List[Document]:
        """Find documents by source."""
        ...
    
    async def find_by_date_range(self, start_date: datetime, end_date: datetime, 
                                limit: int = 100, offset: int = 0) -> List[Document]:
        """Find documents by publication date range."""
        ...
    
    async def search(self, query: str, limit: int = 100, offset: int = 0) -> List[Document]:
        """Search documents by title or abstract."""
        ...
EOF

cat > src/repositories/ingestion_state_repository.py << 'EOF'
from typing import Protocol, List, Optional
from datetime import datetime

from herpai_lib.core.repositories import IRepository
from src.models.ingestion_state import IngestionState

class IIngestionStateRepository(IRepository[IngestionState], Protocol):
    """Repository interface for IngestionState entities."""
    
    async def find_by_job_id(self, job_id: str) -> Optional[IngestionState]:
        """Find an ingestion state by job ID."""
        ...
    
    async def find_active(self) -> List[IngestionState]:
        """Find all active ingestion states (running or pending)."""
        ...
    
    async def find_by_status(self, status: str) -> List[IngestionState]:
        """Find ingestion states by status."""
        ...
    
    async def update_status(self, state_id: str, status: str, 
                          error_message: Optional[str] = None) -> IngestionState:
        """Update the status of an ingestion state."""
        ...
    
    async def update_checkpoint(self, state_id: str, checkpoint: dict, 
                              current_page: int, last_id: Optional[str] = None) -> IngestionState:
        """Update the checkpoint of an ingestion state."""
        ...
    
    async def increment_retry(self, state_id: str) -> IngestionState:
        """Increment the retry count of an ingestion state."""
        ...
    
    async def update_progress(self, state_id: str, documents_processed: int, 
                            documents_total: Optional[int] = None) -> IngestionState:
        """Update the progress of an ingestion state."""
        ...
EOF

cat > src/repositories/scheduled_job_repository.py << 'EOF'
from typing import Protocol, List, Optional
from datetime import datetime

from herpai_lib.core.repositories import IRepository
from src.models.scheduled_job import ScheduledJob

class IScheduledJobRepository(IRepository[ScheduledJob], Protocol):
    """Repository interface for ScheduledJob entities."""
    
    async def find_by_name(self, name: str) -> Optional[ScheduledJob]:
        """Find a scheduled job by name."""
        ...
    
    async def find_enabled(self) -> List[ScheduledJob]:
        """Find all enabled scheduled jobs."""
        ...
    
    async def find_due(self, reference_time: datetime = None) -> List[ScheduledJob]:
        """Find scheduled jobs that are due to run."""
        ...
    
    async def find_running(self) -> List[ScheduledJob]:
        """Find currently running scheduled jobs."""
        ...
    
    async def mark_as_running(self, job_id: str, running: bool = True) -> ScheduledJob:
        """Mark a job as running or not running."""
        ...
    
    async def update_run_stats(self, job_id: str, documents_count: int, 
                              error_count: int = 0) -> ScheduledJob:
        """Update job run statistics."""
        ...
    
    async def update_next_run(self, job_id: str, next_run: datetime) -> ScheduledJob:
        """Update the next run time for a job."""
        ...
EOF

# Create specifications for custom queries
mkdir -p src/repositories
cat > src/repositories/specifications.py << 'EOF'
from herpai_lib.core.repositories import Specification
from sqlalchemy import and_, or_, func
from datetime import datetime

from src.models.document import Document
from src.models.ingestion_state import IngestionState
from src.models.scheduled_job import ScheduledJob

# Document specifications
class DocumentBySourceSpecification(Specification[Document]):
    """Specification for finding documents by source."""
    
    def __init__(self, source: str):
        self.source = source
    
    def to_expression(self):
        return Document.source == self.source

class DocumentByExternalIdSpecification(Specification[Document]):
    """Specification for finding documents by external ID."""
    
    def __init__(self, source: str, external_id: str):
        self.source = source
        self.external_id = external_id
    
    def to_expression(self):
        return and_(Document.source == self.source, Document.external_id == self.external_id)

class DocumentByDoiSpecification(Specification[Document]):
    """Specification for finding documents by DOI."""
    
    def __init__(self, doi: str):
        self.doi = doi
    
    def to_expression(self):
        return Document.doi == self.doi

class DocumentByPmidSpecification(Specification[Document]):
    """Specification for finding documents by PMID."""
    
    def __init__(self, pmid: str):
        self.pmid = pmid
    
    def to_expression(self):
        return Document.pmid == self.pmid

class DocumentByPmcidSpecification(Specification[Document]):
    """Specification for finding documents by PMCID."""
    
    def __init__(self, pmcid: str):
        self.pmcid = pmcid
    
    def to_expression(self):
        return Document.pmcid == self.pmcid

class UnprocessedDocumentSpecification(Specification[Document]):
    """Specification for finding unprocessed documents."""
    
    def to_expression(self):
        return Document.processed == False

class DocumentByDateRangeSpecification(Specification[Document]):
    """Specification for finding documents by publication date range."""
    
    def __init__(self, start_date: datetime, end_date: datetime):
        self.start_date = start_date
        self.end_date = end_date
    
    def to_expression(self):
        return and_(
            Document.publication_date >= self.start_date,
            Document.publication_date <= self.end_date
        )

class DocumentSearchSpecification(Specification[Document]):
    """Specification for searching documents by title or abstract."""
    
    def __init__(self, query: str):
        self.query = query
    
    def to_expression(self):
        return or_(
            Document.title.ilike(f"%{self.query}%"),
            Document.abstract.ilike(f"%{self.query}%")
        )

# IngestionState specifications
class IngestionStateByJobIdSpecification(Specification[IngestionState]):
    """Specification for finding ingestion state by job ID."""
    
    def __init__(self, job_id: str):
        self.job_id = job_id
    
    def to_expression(self):
        return IngestionState.job_id == self.job_id

class IngestionStateByStatusSpecification(Specification[IngestionState]):
    """Specification for finding ingestion states by status."""
    
    def __init__(self, status: str):
        self.status = status
    
    def to_expression(self):
        return IngestionState.status == self.status

class ActiveIngestionStateSpecification(Specification[IngestionState]):
    """Specification for finding active ingestion states."""
    
    def to_expression(self):
        return IngestionState.status.in_(["pending", "running"])

# ScheduledJob specifications
class ScheduledJobByNameSpecification(Specification[ScheduledJob]):
    """Specification for finding scheduled job by name."""
    
    def __init__(self, name: str):
        self.name = name
    
    def to_expression(self):
        return ScheduledJob.name == self.name

class EnabledScheduledJobSpecification(Specification[ScheduledJob]):
    """Specification for finding enabled scheduled jobs."""
    
    def to_expression(self):
        return ScheduledJob.enabled == True

class RunningScheduledJobSpecification(Specification[ScheduledJob]):
    """Specification for finding running scheduled jobs."""
    
    def to_expression(self):
        return ScheduledJob.running == True

class DueScheduledJobSpecification(Specification[ScheduledJob]):
    """Specification for finding scheduled jobs that are due to run."""
    
    def __init__(self, reference_time: datetime = None):
        self.reference_time = reference_time or datetime.utcnow()
    
    def to_expression(self):
        return and_(
            ScheduledJob.enabled == True,
            ScheduledJob.running == False,
            ScheduledJob.next_run <= self.reference_time
        )
EOF

# Create connector base class
cat > src/connectors/base.py << 'EOF'
from typing import Protocol, List, Dict, Any, Optional, AsyncIterator
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import aiohttp
from datetime import datetime

from src.models.document import Document

@dataclass
class PaginationState:
    """State of pagination for a source."""
    
    page: int = 1
    page_size: int = 100
    total_pages: Optional[int] = None
    total_results: Optional[int] = None
    last_id: Optional[str] = None
    has_more: bool = True
    metadata: Dict[str, Any] = None

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

class BaseSourceConnector(ABC):
    """Base connector for data sources."""
    
    def __init__(self, config: Dict[str, Any], pagination_strategy: Optional[PaginationStrategy] = None):
        """Initialize the connector with configuration."""
        self.config = config
        self.pagination_strategy = pagination_strategy
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def search(self, query: str, limit: int = 100) -> AsyncIterator[Document]:
        """Search for documents matching a query."""
        pass
    
    @abstractmethod
    async def get_document(self, id: str) -> Optional[Document]:
        """Get a specific document by ID."""
        pass
    
    @abstractmethod
    async def download_pdf(self, document: Document) -> Optional[str]:
        """Download PDF for a document, returns path to saved PDF."""
        pass
    
    @abstractmethod
    async def get_source_name(self) -> str:
        """Get the name of the source."""
        pass
EOF

# Create an extended AppConfig for biomedical settings
cat > src/config.py << 'EOF'
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List, Set
import logging
from datetime import datetime

from herpai_lib.core.config import AppConfig as BaseAppConfig

@dataclass
class BiomedicalAppConfig(BaseAppConfig):
    """Extended application configuration for biomedical data ingestion."""
    
    # Extend base AppConfig with biomedical-specific settings
    pubmed_api_key: Optional[str] = None
    grobid_host: str = "localhost"
    grobid_port: int = 8070
    pdf_storage_path: str = "data/pdfs"
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'BiomedicalAppConfig':
        """Create an instance from a YAML file by extending base implementation."""
        # First use the parent class implementation
        instance = super().from_yaml(config_path)
        
        # Then add our custom properties
        yaml_config = cls._get_yaml_config()
        
        # Set biomedical-specific properties from YAML
        if yaml_config:
            instance.pubmed_api_key = yaml_config.get('sources.pubmed.api_key')
            
            if yaml_config.get('grobid'):
                instance.grobid_host = yaml_config.get('grobid.host', instance.grobid_host)
                instance.grobid_port = yaml_config.get('grobid.port', instance.grobid_port)
            
            if yaml_config.get('storage.pdf_path'):
                instance.pdf_storage_path = yaml_config.get('storage.pdf_path', instance.pdf_storage_path)
        
        return instance
EOF

# Create the main CLI module
mkdir -p src/cli
cat > src/cli/main.py << 'EOF'
import typer
from rich.console import Console
from typing import Optional
import logging
import os

from herpai_lib.core.engine import engine
from herpai_lib.core.config import YamlConfig

# Import subcommands
from src.cli import ingest, process, catalog, scheduler, sources, storage
from src.config import BiomedicalAppConfig

app = typer.Typer(
    name="herpai",
    help="HerpAI-Ingestion: A toolkit for biomedical data ingestion",
    add_completion=False,
)

console = Console()

# Add subcommands
app.add_typer(ingest.app, name="ingest")
app.add_typer(process.app, name="process") 
app.add_typer(catalog.app, name="catalog")
app.add_typer(scheduler.app, name="scheduler")
app.add_typer(sources.app, name="sources")
app.add_typer(storage.app, name="storage")

@app.callback()
def main(
    config: str = typer.Option(
        "config.yaml", "--config", "-c", help="Path to configuration file"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """
    HerpAI-Ingestion: A toolkit for biomedical data ingestion.
    
    This tool provides functionality for ingesting, processing, and storing biomedical
    data from various sources like PubMed, Europe PMC, and ClinicalTrials.gov.
    """
    # Set up logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create data directories if they don't exist
    os.makedirs("data/pdfs", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    # Initialize engine and load configuration
    engine.initialize()
    
    # Load the biomedical app config (extending base AppConfig)
    app_config = BiomedicalAppConfig.from_yaml(config)
    
    # Register the app config as a singleton
    engine.register_instance(BiomedicalAppConfig, app_config)
    
    if verbose:
        console.print(f"Loaded configuration from [bold]{config}[/bold]")

if __name__ == "__main__":
    app()
EOF

# Create CLI subcommand stubs
cat > src/cli/ingest.py << 'EOF'
import typer
from rich.console import Console
from typing import Optional, List

app = typer.Typer(help="Run ingestion from a specific source")
console = Console()

@app.command()
def run(
    source: str = typer.Argument(..., help="Source to ingest from (pubmed, europepmc, clinicaltrials)"),
    query: str = typer.Option(..., "--query", "-q", help="Search query for the source"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum number of records to ingest"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory for downloaded files"),
    batch_size: int = typer.Option(0, "--batch-size", "-b", help="Batch size for requests (0 = use config default)"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-download of existing documents"),
    tags: Optional[List[str]] = typer.Option(None, "--tag", help="Tags to assign to ingested documents"),
):
    """
    Run an ingestion job from a specific source.
    """
    console.print(f"Running ingestion from [bold]{source}[/bold] with query: [italic]{query}[/italic]")
    console.print(f"Limit: {limit}, Batch size: {batch_size or 'default'}")
    # Implementation will be added
EOF

# Create other CLI module stubs - Fixed version without string capitalization
cat > src/cli/process.py << 'EOF'
import typer
from rich.console import Console
from typing import Optional

app = typer.Typer(help="Process operations")
console = Console()

@app.command()
def list():
    """
    List process items.
    """
    console.print("Listing process items")
    # Implementation will be added

@app.command()
def info(
    id: str = typer.Argument(..., help="ID to get info for"),
):
    """
    Get info about a specific process item.
    """
    console.print(f"Getting info for: [bold]{id}[/bold]")
    # Implementation will be added
EOF

cat > src/cli/catalog.py << 'EOF'
import typer
from rich.console import Console
from typing import Optional

app = typer.Typer(help="Catalog operations")
console = Console()

@app.command()
def list():
    """
    List catalog items.
    """
    console.print("Listing catalog items")
    # Implementation will be added

@app.command()
def info(
    id: str = typer.Argument(..., help="ID to get info for"),
):
    """
    Get info about a specific catalog item.
    """
    console.print(f"Getting info for: [bold]{id}[/bold]")
    # Implementation will be added
EOF

cat > src/cli/scheduler.py << 'EOF'
import typer
from rich.console import Console
from typing import Optional

app = typer.Typer(help="Scheduler operations")
console = Console()

@app.command()
def list():
    """
    List scheduler items.
    """
    console.print("Listing scheduler items")
    # Implementation will be added

@app.command()
def info(
    id: str = typer.Argument(..., help="ID to get info for"),
):
    """
    Get info about a specific scheduler item.
    """
    console.print(f"Getting info for: [bold]{id}[/bold]")
    # Implementation will be added
EOF

cat > src/cli/sources.py << 'EOF'
import typer
from rich.console import Console
from typing import Optional

app = typer.Typer(help="Sources operations")
console = Console()

@app.command()
def list():
    """
    List sources items.
    """
    console.print("Listing sources items")
    # Implementation will be added

@app.command()
def info(
    id: str = typer.Argument(..., help="ID to get info for"),
):
    """
    Get info about a specific sources item.
    """
    console.print(f"Getting info for: [bold]{id}[/bold]")
    # Implementation will be added
EOF

cat > src/cli/storage.py << 'EOF'
import typer
from rich.console import Console
from typing import Optional

app = typer.Typer(help="Storage operations")
console = Console()

@app.command()
def list():
    """
    List storage items.
    """
    console.print("Listing storage items")
    # Implementation will be added

@app.command()
def info(
    id: str = typer.Argument(..., help="ID to get info for"),
):
    """
    Get info about a specific storage item.
    """
    console.print(f"Getting info for: [bold]{id}[/bold]")
    # Implementation will be added
EOF

# Create a commit message
cat > commit-message.txt << 'EOF'
Initial project structure for HerpAI-Ingestion

This commit establishes the foundation for the HerpAI-Ingestion project, a biomedical data ingestion library that extends HerpAI-Lib. The structure follows proper software engineering practices and extends the existing functionality of HerpAI-Lib rather than duplicating it.

Key components added:
- Biomedical-specific entity models (Document, IngestionState, ScheduledJob)
- Repository interfaces with domain-specific methods
- Specifications for common biomedical data queries
- Source connector architecture for different biomedical data sources
- CLI command structure for user interaction
- BiomedicalAppConfig extending HerpAI-Lib's AppConfig

This implementation properly leverages existing HerpAI-Lib functionality:
- Uses the engine for dependency injection
- Extends the BaseEntity for domain models
- Uses IRepository for base CRUD operations
- Uses the Specification pattern for queries
- Follows the AppConfig pattern for configuration

Technical highlights:
- Clean separation of interfaces and implementations
- Type annotations and protocol-based interfaces
- Domain-specific models for biomedical data
- CLI powered by Typer with rich console output

Next steps will involve implementing the source connectors, storage services, and processing functionality.
EOF

# Prepare the commit command
echo ""
echo "To commit these changes, run:"
echo 'git add . && git commit -F commit-message.txt'
echo ""

echo "HerpAI-Ingestion project structure has been created successfully."