# HerpAI-Ingestion: Solution Design Document

A flexible and scalable library for ingesting, processing, and storing biomedical data from various sources, built for the HerpAI Project to enrich AI Agents with domain-specific knowledge and power Retrieval-Augmented Generation (RAG) systems.

## Table of Contents
- [HerpAI-Ingestion: Solution Design Document](#herpai-ingestion-solution-design-document)
  - [Table of Contents](#table-of-contents)
  - [System Overview](#system-overview)
  - [Architecture](#architecture)
    - [Connector SDK Components](#connector-sdk-components)
    - [Interfaces and Base Classes](#interfaces-and-base-classes)
    - [Connector Data Models](#connector-data-models)
    - [Connector Utilities](#connector-utilities)
    - [Connector Exceptions](#connector-exceptions)
    - [Data Flow](#data-flow)
    - [Component Interactions](#component-interactions)
  - [Sample Connector Implementation](#sample-connector-implementation)
    - [Connector Registry](#connector-registry)
    - [Connector Specifications](#connector-specifications)
  - [Data Processing Pipeline](#data-processing-pipeline)
    - [Extraction Phase](#extraction-phase)
    - [Transformation Phase](#transformation-phase)
    - [Loading Phase](#loading-phase)
  - [Data Model and Repository Pattern](#data-model-and-repository-pattern)
    - [Domain Entities](#domain-entities)
    - [Repository Interfaces](#repository-interfaces)
    - [Specifications](#specifications)
    - [Repository Implementations](#repository-implementations)
  - [Engine Initialization and Startup](#engine-initialization-and-startup)
  - [Configuration System](#configuration-system)

## System Overview

HerpAI-Ingestion is a critical component of the HerpAI ecosystem, designed to gather and process biomedical data with a focus on herpes viruses and related treatments. It serves as the knowledge acquisition layer, feeding domain-specific information into the AI systems that power HerpAI's capabilities.

**Key Objectives:**
1. Systematically collect and process biomedical data from authoritative sources
2. Transform raw data into structured, AI-consumable formats
3. Enable Retrieval-Augmented Generation (RAG) for HerpAI Agents
4. Maintain an up-to-date knowledge base with the latest research and clinical information
5. Provide a flexible, extensible architecture that can incorporate new data sources

**Role in HerpAI Ecosystem:**
- Provides the foundation for domain knowledge acquisition
- Enables HerpAI Agents to reference specific scientific information
- Powers data-driven insights and analysis capabilities
- Ensures responses are grounded in accurate, current medical literature

## Architecture

### Connector SDK Components

The `herpai_connector_sdk` package provides the foundation for all connectors:

### Interfaces and Base Classes

```python
# herpai_connector_sdk/interfaces.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class IConnector(ABC):
    """Interface for all connectors in the HerpAI-Ingestion system."""
    
    @abstractmethod
    async def install(self) -> None:
        """Install connector dependencies or set up resources."""
        pass
    
    @abstractmethod
    async def uninstall(self) -> None:
        """Clean up connector resources."""
        pass
    
    @abstractmethod
    async def authenticate(self, config: Dict[str, Any]) -> None:
        """Authenticate with the data source."""
        pass
    
    @abstractmethod
    async def search(self, query: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Search the data source with the given query."""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Dict[str, Any]:
        """Retrieve a specific document by ID."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the connector name."""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> Dict[str, bool]:
        """Get the connector capabilities."""
        pass

# herpai_connector_sdk/base.py
from .interfaces import IConnector
from .models import Document
from typing import Dict, List, Optional, Any
import yaml
import os
import logging

logger = logging.getLogger(__name__)

class BaseConnector(IConnector):
    """Base implementation for connectors with common functionality."""
    
    def __init__(self):
        self._config = {}
        self._capabilities = {
            "supports_fulltext": False,
            "supports_advanced_search": False,
            "supports_date_filtering": False,
            "requires_authentication": False
        }
    
    async def install(self) -> None:
        """Default implementation of install that logs the action."""
        logger.info(f"Installing connector: {self.name}")
    
    async def uninstall(self) -> None:
        """Default implementation of uninstall that logs the action."""
        logger.info(f"Uninstalling connector: {self.name}")
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the connector with the provided settings."""
        self._config = config
    
    def load_specification(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Load the connector specification from a YAML file."""
        if not path:
            # Try to find specification in the connector's directory
            module_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(module_dir, "connector.yaml")
        
        if not os.path.exists(path):
            logger.warning(f"Specification file not found: {path}")
            return {}
        
        try:
            with open(path, "r") as f:
                spec = yaml.safe_load(f)
                
                # Update capabilities from spec
                if "capabilities" in spec:
                    self._capabilities.update(spec["capabilities"])
                
                return spec
        except Exception as e:
            logger.error(f"Error loading specification: {str(e)}")
            return {}
    
    @property
    def capabilities(self) -> Dict[str, bool]:
        """Get the connector capabilities."""
        return self._capabilities.copy()
```

### Connector Data Models

```python
# herpai_connector_sdk/models.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class Author:
    """Author data model."""
    name: str
    orcid: Optional[str] = None
    email: Optional[str] = None
    affiliation: Optional[str] = None

@dataclass
class Document:
    """Document data model for connector responses."""
    id: str
    source: str
    title: str
    abstract: Optional[str] = None
    publication_date: Optional[datetime] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    authors: List[Author] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    document_type: str = "article"
    full_text: Optional[str] = None
    metadata: Dict[str, any] = field(default_factory=dict)

@dataclass
class SearchResult:
    """Search result data model."""
    query: str
    total_results: int
    document_ids: List[str]
    metadata: Dict[str, any] = field(default_factory=dict)
```

### Connector Utilities

```python
# herpai_connector_sdk/utils/rate_limiter.py
import asyncio
import time
from typing import Optional

class RateLimiter:
    """Utility for managing API rate limits."""
    
    def __init__(self, requests_per_second: float):
        self.requests_per_second = requests_per_second
        self._last_request_time = 0.0
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request."""
        async with self._lock:
            current_time = time.time()
            time_since_last_request = current_time - self._last_request_time
            min_interval = 1.0 / self.requests_per_second
            
            if time_since_last_request < min_interval:
                # Need to wait
                wait_time = min_interval - time_since_last_request
                await asyncio.sleep(wait_time)
            
            self._last_request_time = time.time()

# herpai_connector_sdk/utils/http.py
import aiohttp
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class HTTPClient:
    """HTTP client utility for connectors."""
    
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.session = None
    
    async def ensure_session(self):
        """Ensure an aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
    
    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        await self.ensure_session()
        url = f"{self.base_url}/{path.lstrip('/')}"
        
        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP error: {e.status} - {e.message}")
            raise
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            raise
```

### Connector Exceptions

```python
# herpai_connector_sdk/exceptions.py
class ConnectorError(Exception):
    """Base exception for connector-related errors."""
    pass

class AuthenticationError(ConnectorError):
    """Exception raised for authentication failures."""
    def __init__(self, message="Authentication failed", *args, **kwargs):
        super().__init__(message, *args, **kwargs)

class RateLimitExceeded(ConnectorError):
    """Exception raised when rate limits are exceeded."""
    def __init__(self, message="Rate limit exceeded", retry_after=None, *args, **kwargs):
        self.retry_after = retry_after
        super().__init__(message, *args, **kwargs)

class FetchError(ConnectorError):
    """Exception raised when document fetching fails."""
    def __init__(self, document_id, message="Failed to fetch document", *args, **kwargs):
        self.document_id = document_id
        super().__init__(f"{message}: {document_id}", *args, **kwargs)

class ParseError(ConnectorError):
    """Exception raised when document parsing fails."""
    def __init__(self, document_id, message="Failed to parse document", *args, **kwargs):
        self.document_id = document_id
        super().__init__(f"{message}: {document_id}", *args, **kwargs)
```

### Data Flow

The system follows a clear data flow pattern:

1. **Ingestion Request Initiation**
   - Via CLI, API, or scheduled job
   - Query parameters specified (search terms, date ranges, etc.)
   - Resources allocated based on request size

2. **Connector Execution**
   - Appropriate connector selected
   - Authentication performed if required
   - Query translated to source-specific format
   - Results retrieved with pagination if needed

3. **Document Acquisition**
   - Raw documents downloaded
   - Initial format detection
   - Checksums calculated for deduplication

4. **Document Processing**
   - Text extraction from various formats
   - Structure identification (sections, references)
   - Entity extraction (diseases, treatments, genes)
   - Relationship mapping

5. **Metadata Extraction**
   - Bibliographic information captured
   - Author information normalized
   - Citation network built
   - Keywords and classifications extracted

6. **Storage**
   - Raw documents stored in data lake
   - Processed documents stored in structured format
   - Metadata stored in database
   - Vector embeddings generated for RAG

7. **Indexing and Optimization**
   - Search indices created/updated
   - Access patterns optimized
   - Cache warming for frequent queries

### Component Interactions

The system uses a combination of interfaces and events to coordinate component interactions:

**Key Interface Points:**
1. **IConnector** - Standardized interface for all data source connectors
2. **IDocumentProcessor** - Interface for document processing components
3. **IStorageProvider** - Abstraction for different storage backends
4. **IMetadataRepository** - Interface for metadata catalog interactions

**Event Flow:**
1. **IngestionRequested** - Triggered when a new ingestion job is created
2. **DocumentAcquired** - Fired when a document is successfully downloaded
3. **DocumentProcessed** - Signaled after document processing completes
4. **MetadataExtracted** - Indicates metadata extraction completion
5. **DocumentStored** - Confirms successful storage of a document
6. **IngestionCompleted** - Marks the completion of an ingestion job

## Sample Connector Implementation

Example implementation of a PubMed connector:

```python
# connectors/pubmed/connector.py
from herpai_connector_sdk.base import BaseConnector
from herpai_connector_sdk.models import Document, Author, SearchResult
from herpai_connector_sdk.utils.rate_limiter import RateLimiter
from herpai_connector_sdk.utils.http import HTTPClient
from herpai_connector_sdk.exceptions import AuthenticationError, RateLimitExceeded, FetchError

from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class PubMedConnector(BaseConnector):
    """Connector for the PubMed/NCBI E-utilities API."""
    
    def __init__(self):
        super().__init__()
        
        # Load connector specification
        spec_path = os.path.join(os.path.dirname(__file__), "connector.yaml")
        self._spec = self.load_specification(spec_path)
        
        # Initialize HTTP client
        base_url = self._spec.get("api", {}).get("base_url", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/")
        self._http_client = HTTPClient(base_url)
        
        # Set up rate limiter based on specification
        requests_per_second = self._spec.get("api", {}).get("rate_limit", {}).get("requests_per_second", 3)
        self._rate_limiter = RateLimiter(requests_per_second)
    
    @property
    def name(self) -> str:
        """Get the connector name."""
        return "pubmed"
    
    async def authenticate(self, config: Dict[str, Any]) -> None:
        """Authenticate with the PubMed API."""
        api_key = config.get("api_key")
        
        if api_key:
            # Update rate limit if API key is provided
            requests_per_second = self._spec.get("api", {}).get("rate_limit", {}).get("with_api_key", 10)
            self._rate_limiter = RateLimiter(requests_per_second)
            
            # Store API key for later use
            self._config["api_key"] = api_key
            logger.info("PubMed connector authenticated with API key")
        else:
            logger.info("PubMed connector using unauthenticated access (lower rate limits)")
    
    async def search(self, query: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Search PubMed with the given query."""
        await self._rate_limiter.acquire()
        
        # Prepare search parameters
        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": limit or 20
        }
        
        # Add API key if available
        if self._config.get("api_key"):
            params["api_key"] = self._config["api_key"]
        
        try:
            # Perform the search
            response = await self._http_client.get("esearch.fcgi", params)
            
            # Extract document IDs
            result = response.get("esearchresult", {})
            document_ids = result.get("idlist", [])
            total_count = int(result.get("count", 0))
            
            return SearchResult(
                query=query,
                total_results=total_count,
                document_ids=document_ids,
                metadata={"db": "pubmed"}
            ).__dict__
            
        except Exception as e:
            logger.error(f"Error searching PubMed: {str(e)}")
            raise
    
    async def get_by_id(self, id: str) -> Dict[str, Any]:
        """Retrieve a specific document from PubMed by ID."""
        await self._rate_limiter.acquire()
        
        # Prepare fetch parameters
        params = {
            "db": "pubmed",
            "id": id,
            "retmode": "xml"
        }
        
        # Add API key if available
        if self._config.get("api_key"):
            params["api_key"] = self._config["api_key"]
        
        try:
            # Fetch the document
            response = await self._http_client.get("efetch.fcgi", params)
            
            # Parse XML response
            root = ET.fromstring(response)
            article = root.find(".//PubmedArticle")
            
            if article is None:
                raise FetchError(id, "Document not found or invalid format")
            
            # Extract document data
            title = article.findtext(".//ArticleTitle") or "Untitled"
            abstract = article.findtext(".//AbstractText")
            
            # Extract publication date
            pub_date_elem = article.find(".//PubDate")
            if pub_date_elem is not None:
                year = pub_date_elem.findtext("Year")
                month = pub_date_elem.findtext("Month") or "1"
                day = pub_date_elem.findtext("Day") or "1"
                
                # Convert month name to number if needed
                if not month.isdigit():
                    month_map = {
                        "Jan": "1", "Feb": "2", "Mar": "3", "Apr": "4",
                        "May": "5", "Jun": "6", "Jul": "7", "Aug": "8",
                        "Sep": "9", "Oct": "10", "Nov": "11", "Dec": "12"
                    }
                    month = month_map.get(month[:3], "1")
                
                try:
                    publication_date = datetime(int(year), int(month), int(day))
                except (ValueError, TypeError):
                    publication_date = None
            else:
                publication_date = None
            
            # Extract DOI
            doi = None
            article_id_list = article.find(".//ArticleIdList")
            if article_id_list is not None:
                for article_id in article_id_list.findall("ArticleId"):
                    if article_id.get("IdType") == "doi":
                        doi = article_id.text
                        break
            
            # Extract authors
            authors = []
            author_list = article.find(".//AuthorList")
            if author_list is not None:
                for author_elem in author_list.findall("Author"):
                    last_name = author_elem.findtext("LastName") or ""
                    fore_name = author_elem.findtext("ForeName") or ""
                    initials = author_elem.findtext("Initials") or ""
                    
                    name = f"{last_name}, {fore_name}".strip()
                    if not name:
                        name = initials
                    
                    # Extract affiliation
                    affiliation = author_elem.findtext(".//Affiliation")
                    
                    authors.append(Author(
                        name=name,
                        affiliation=affiliation
                    ).__dict__)
            
            # Extract keywords
            keywords = []
            keyword_list = article.find(".//KeywordList")
            if keyword_list is not None:
                for keyword in keyword_list.findall("Keyword"):
                    if keyword.text:
                        keywords.append(keyword.text)
            
            # Create document
            document = Document(
                id=id,
                source="pubmed",
                title=title,
                abstract=abstract,
                publication_date=publication_date,
                doi=doi,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{id}/",
                authors=authors,
                keywords=keywords,
                document_type="article"
            )
            
            return document.__dict__
            
        except Exception as e:
            logger.error(f"Error fetching PubMed document {id}: {str(e)}")
            raise
```

Corresponding connector specification:

```yaml
# connectors/pubmed/connector.yaml
name: pubmed
display_name: PubMed
description: Connects to the PubMed/NCBI E-utilities API for biomedical literature
version: 1.0.0

capabilities:
  supports_fulltext: false
  supports_advanced_search: true
  supports_date_filtering: true
  requires_authentication: false

api:
  base_url: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
  rate_limit:
    requests_per_second: 3
    with_api_key: 10

configuration:
  properties:
    - name: api_key
      type: string
      required: false
      description: NCBI API key for higher rate limits
      sensitive: true
    
    - name: batch_size
      type: integer
      required: false
      default: 100
      description: Number of items to retrieve in each batch
```."""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> Dict[str, bool]:
        """Get the connector capabilities."""
        pass
```

Additional utility classes in the SDK:

```python
class ConnectorError(Exception):
    """Base exception for connector-related errors."""
    pass

class AuthenticationError(ConnectorError):
    """Exception raised for authentication failures."""
    pass

class RateLimitExceeded(ConnectorError):
    """Exception raised when rate limits are exceeded."""
    pass

class RateLimiter:
    """Utility for managing API rate limits."""
    
    def __init__(self, requests_per_second: float):
        self.requests_per_second = requests_per_second
        # Implementation details...
    
    async def acquire(self):
        """Acquire permission to make a request."""
        # Implementation details...
```

### Connector Registry

The ConnectorRegistry manages the discovery, registration, and lifecycle of connectors:

```python
class ConnectorRegistry:
    """Manages connector discovery, registration, and lifecycle."""
    
    def __init__(self, type_finder: ITypeFinder):
        self._type_finder = type_finder
        self._connectors = {}
        self._specifications = {}
    
    async def discover_connectors(self) -> List[str]:
        """Discover available connectors."""
        connector_classes = self._type_finder.find_classes_of_type(
            BaseConnector, only_concrete=True
        )
        
        for connector_class in connector_classes:
            try:
                # Create an instance
                connector = connector_class()
                
                # Register the connector
                await self.register_connector(connector)
                
            except Exception as e:
                logger.error(f"Error registering connector {connector_class.__name__}: {str(e)}")
        
        return list(self._connectors.keys())
    
    async def register_connector(self, connector: BaseConnector) -> None:
        """Register a connector instance."""
        name = connector.name
        self._connectors[name] = connector
        
        # Load the connector specification
        spec_path = self._find_specification_path(name)
        if spec_path:
            self._specifications[name] = self._load_specification(spec_path)
        
        logger.info(f"Registered connector: {name}")
    
    def get_connector(self, name: str) -> Optional[BaseConnector]:
        """Get a connector by name."""
        return self._connectors.get(name)
    
    def get_specification(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a connector specification by name."""
        return self._specifications.get(name)
    
    def _find_specification_path(self, name: str) -> Optional[str]:
        """Find the specification file for a connector."""
        # Implementation details...
    
    def _load_specification(self, path: str) -> Dict[str, Any]:
        """Load a connector specification from file."""
        # Implementation details...
```

### Connector Specifications

Each connector includes a YAML specification file that defines its capabilities, configuration options, and requirements:

```yaml
name: pubmed
display_name: PubMed
description: Connects to the PubMed/NCBI API for biomedical literature
version: 1.0.0

capabilities:
  supports_fulltext: false
  supports_advanced_search: true
  supports_date_filtering: true
  requires_authentication: false

api:
  base_url: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
  rate_limit:
    requests_per_second: 3
    with_api_key: 10

configuration:
  properties:
    - name: api_key
      type: string
      required: false
      description: NCBI API key for higher rate limits
      sensitive: true
    
    - name: batch_size
      type: integer
      required: false
      default: 100
      description: Number of items to retrieve in each batch
```

## Data Processing Pipeline

The data processing pipeline is designed as a series of configurable, composable stages that transform raw data into structured, AI-ready information.

### Extraction Phase

The extraction phase is responsible for acquiring documents from source systems:

1. **Source Query Execution**
   - Translates generic queries to source-specific formats
   - Implements pagination and result set handling
   - Manages authentication and session state

2. **Document Acquisition**
   - Downloads raw document content
   - Resolves DOIs and other identifiers
   - Handles redirects and content negotiation
   - Implements retry logic for transient failures

3. **Initial Validation**
   - Verifies document integrity (checksums)
   - Checks for duplicate documents
   - Validates format and content type
   - Records acquisition metadata (timestamp, source, etc.)

**Key Classes:**

```python
class SourceQueryExecutor:
    """Executes queries against data sources."""
    
    def __init__(self, connector_registry: ConnectorRegistry):
        self._connector_registry = connector_registry
    
    async def execute_query(self, source: str, query: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Execute a query against a specific source."""
        connector = self._connector_registry.get_connector(source)
        if not connector:
            raise ValueError(f"Connector not found: {source}")
        
        return await connector.search(query, limit)

class DocumentAcquisitionService:
    """Acquires documents from data sources."""
    
    def __init__(self, connector_registry: ConnectorRegistry, storage_manager: StorageManager):
        self._connector_registry = connector_registry
        self._storage_manager = storage_manager
    
    async def acquire_document(self, source: str, document_id: str) -> str:
        """Acquire a document from a data source."""
        connector = self._connector_registry.get_connector(source)
        if not connector:
            raise ValueError(f"Connector not found: {source}")
        
        # Get document data
        document_data = await connector.get_by_id(document_id)
        
        # Store raw document
        document_path = await self._storage_manager.store_raw_document(
            source=source,
            document_id=document_id,
            content=document_data.get("content"),
            metadata=document_data.get("metadata")
        )
        
        return document_path
```

### Transformation Phase

The transformation phase processes raw documents into structured, normalized formats:

1. **Format Conversion**
   - Converts various formats (PDF, HTML, XML) to structured text
   - Integrates with GROBID for scientific document parsing
   - Preserves document structure and formatting when relevant

2. **Entity Extraction**
   - Identifies biomedical entities (diseases, treatments, genes, etc.)
   - Maps entities to standardized ontologies
   - Extracts relationships between entities
   - Captures metadata (publication info, authors, etc.)

3. **Knowledge Graph Construction**
   - Builds semantic relationships between entities
   - Links to existing knowledge base
   - Captures citation networks
   - Preserves provenance information

**Key Classes:**

```python
class DocumentProcessor:
    """Processes raw documents into structured formats."""
    
    def __init__(self, config: Dict[str, Any]):
        self._config = config
        # Initialize document processing tools
    
    async def process_document(self, document_path: str) -> Dict[str, Any]:
        """Process a document at the given path."""
        # Detect document format
        document_format = self._detect_format(document_path)
        
        # Select appropriate processor
        processor = self._get_processor_for_format(document_format)
        
        # Process document
        processed_document = await processor.process(document_path)
        
        return processed_document
    
    def _detect_format(self, document_path: str) -> str:
        """Detect the format of a document."""
        # Implementation details...
    
    def _get_processor_for_format(self, document_format: str) -> 'FormatProcessor':
        """Get the appropriate processor for a document format."""
        # Implementation details...

class PDFProcessor(FormatProcessor):
    """Processor for PDF documents."""
    
    async def process(self, document_path: str) -> Dict[str, Any]:
        """Process a PDF document."""
        # Use GROBID for scientific PDF processing
        # Implementation details...

class EntityExtractor:
    """Extracts entities from processed documents."""
    
    async def extract_entities(self, processed_document: Dict[str, Any]) -> Dict[str, Any]:
        """Extract entities from a processed document."""
        # Implementation details...
```

### Loading Phase

The loading phase stores processed documents and their metadata:

1. **Document Storage**
   - Stores raw and processed documents in data lake
   - Implements versioning and change tracking
   - Optimizes for retrieval patterns
   - Handles deduplication and compression

2. **Metadata Indexing**
   - Stores structured metadata in database
   - Creates indices for efficient querying
   - Maintains relationships between documents
   - Updates search indices

3. **Vector Embedding Generation**
   - Generates embeddings for RAG systems
   - Stores embeddings in vector database
   - Implements semantic similarity search
   - Optimizes for retrieval performance

**Key Classes:**

```python
class StorageManager:
    """Manages document storage across different backends."""
    
    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self._storage_provider = self._create_storage_provider()
    
    def _create_storage_provider(self) -> 'IStorageProvider':
        """Create the appropriate storage provider based on configuration."""
        provider_type = self._config.get("storage", {}).get("type", "local")
        
        if provider_type == "azure":
            return AzureBlobStorageProvider(self._config.get("storage", {}).get("azure", {}))
        elif provider_type == "s3":
            return S3StorageProvider(self._config.get("storage", {}).get("s3", {}))
        else:
            return LocalStorageProvider(self._config.get("storage", {}).get("local", {}))
    
    async def store_raw_document(self, source: str, document_id: str, content: bytes, metadata: Dict[str, Any]) -> str:
        """Store a raw document."""
        path = f"raw/{source}/{document_id}"
        await self._storage_provider.store(path, content)
        
        # Store metadata
        await self._store_metadata(path + ".meta.json", metadata)
        
        return path
    
    async def store_processed_document(self, source: str, document_id: str, content: Dict[str, Any]) -> str:
        """Store a processed document."""
        path = f"processed/{source}/{document_id}"
        await self._storage_provider.store(path + ".json", json.dumps(content).encode("utf-8"))
        
        return path
    
    async def _store_metadata(self, path: str, metadata: Dict[str, Any]) -> None:
        """Store metadata for a document."""
        await self._storage_provider.store(path, json.dumps(metadata).encode("utf-8"))

class MetadataCatalog:
    """Manages document metadata in a database."""
    
    def __init__(self, db_context: IDbContext):
        self._db_context = db_context
    
    async def store_document_metadata(self, document: Document) -> None:
        """Store metadata for a document."""
        async with self._db_context.session() as session:
            # Store document metadata
            await session.add(document)
            await session.commit()
    
    async def find_documents(self, query: Dict[str, Any]) -> List[Document]:
        """Find documents matching a query."""
        async with self._db_context.session() as session:
            # Build query
            query_builder = self._build_query(query)
            
            # Execute query
            result = await session.execute(query_builder)
            
            return result.scalars().all()
    
    def _build_query(self, query: Dict[str, Any]):
        """Build a database query from a dictionary."""
        # Implementation details...

class VectorEmbeddingService:
    """Generates and stores vector embeddings for documents."""
    
    def __init__(self, config: Dict[str, Any]):
        self._config = config
        # Initialize embedding model
    
    async def generate_embeddings(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Generate embeddings for a document."""
        # Implementation details...
    
    async def store_embeddings(self, document_id: str, embeddings: Dict[str, Any]) -> None:
        """Store embeddings for a document."""
        # Implementation details...
```

## Data Model and Repository Pattern

HerpAI-Ingestion implements the repository pattern as defined in the OpenBioCure CoreLib to provide a clean separation between domain entities and data access logic. This architectural approach ensures maintainability, testability, and flexibility in the persistence layer.

### Domain Entities

The system defines these core domain entities:

```python
from openbiocure_corelib.data.entity import BaseEntity
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import Optional, List
from datetime import datetime

class Document(BaseEntity):
    """Document entity representing a biomedical document."""
    
    __tablename__ = "documents"
    
    source: Mapped[str] = mapped_column(nullable=False)
    source_id: Mapped[str] = mapped_column(nullable=False, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(nullable=True)
    publication_date: Mapped[datetime] = mapped_column(nullable=False)
    doi: Mapped[Optional[str]] = mapped_column(nullable=True, index=True)
    url: Mapped[Optional[str]] = mapped_column(nullable=True)
    document_type: Mapped[str] = mapped_column(nullable=False)
    processing_status: Mapped[str] = mapped_column(nullable=False)
    storage_path: Mapped[Optional[str]] = mapped_column(nullable=True)
    
    # Relationships
    authors: Mapped[List["Author"]] = relationship(
        secondary="document_authors",
        back_populates="documents"
    )
    entity_mentions: Mapped[List["EntityMention"]] = relationship(back_populates="document")
    citations: Mapped[List["Citation"]] = relationship(
        foreign_keys="Citation.citing_document_id",
        back_populates="citing_document"
    )
    cited_by: Mapped[List["Citation"]] = relationship(
        foreign_keys="Citation.cited_document_id",
        back_populates="cited_document"
    )

class Author(BaseEntity):
    """Author entity representing a document author."""
    
    __tablename__ = "authors"
    
    name: Mapped[str] = mapped_column(nullable=False)
    orcid: Mapped[Optional[str]] = mapped_column(nullable=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(nullable=True)
    affiliation: Mapped[Optional[str]] = mapped_column(nullable=True)
    
    # Relationships
    documents: Mapped[List["Document"]] = relationship(
        secondary="document_authors",
        back_populates="authors"
    )

class DocumentAuthor(BaseEntity):
    """Junction table for document-author many-to-many relationship."""
    
    __tablename__ = "document_authors"
    
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    author_id: Mapped[str] = mapped_column(ForeignKey("authors.id"), nullable=False)
    author_position: Mapped[int] = mapped_column(nullable=False)
    is_corresponding: Mapped[bool] = mapped_column(nullable=False, default=False)

class EntityMention(BaseEntity):
    """Entity mention in a document."""
    
    __tablename__ = "entity_mentions"
    
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    entity_type: Mapped[str] = mapped_column(nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(nullable=False, index=True)
    text: Mapped[str] = mapped_column(nullable=False)
    start_offset: Mapped[int] = mapped_column(nullable=False)
    end_offset: Mapped[int] = mapped_column(nullable=False)
    confidence: Mapped[float] = mapped_column(nullable=False)
    
    # Relationships
    document: Mapped["Document"] = relationship(back_populates="entity_mentions")

class Citation(BaseEntity):
    """Citation relationship between documents."""
    
    __tablename__ = "citations"
    
    citing_document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    cited_document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    context: Mapped[Optional[str]] = mapped_column(nullable=True)
    
    # Relationships
    citing_document: Mapped["Document"] = relationship(
        foreign_keys=[citing_document_id],
        back_populates="citations"
    )
    cited_document: Mapped["Document"] = relationship(
        foreign_keys=[cited_document_id],
        back_populates="cited_by"
    )

class ConnectorExecution(BaseEntity):
    """Tracks connector execution history."""
    
    __tablename__ = "connector_executions"
    
    connector_name: Mapped[str] = mapped_column(nullable=False, index=True)
    query: Mapped[str] = mapped_column(nullable=False)
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=False)
    documents_found: Mapped[int] = mapped_column(nullable=False, default=0)
    documents_processed: Mapped[int] = mapped_column(nullable=False, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(nullable=True)
```

### Repository Interfaces

Following the repository pattern from OpenBioCure CoreLib, we define protocol interfaces for each entity:

```python
from typing import Protocol, List, Optional
from openbiocure_corelib.data.repository import IRepository
from openbiocure_corelib.data.specification import Specification

class IDocumentRepository(IRepository[Document], Protocol):
    """Repository interface for Document entities."""
    
    async def find_by_source_id(self, source: str, source_id: str) -> Optional[Document]: ...
    async def find_by_doi(self, doi: str) -> Optional[Document]: ...
    async def find_by_processing_status(self, status: str) -> List[Document]: ...
    async def update_processing_status(self, document_id: str, status: str) -> Document: ...

class IAuthorRepository(IRepository[Author], Protocol):
    """Repository interface for Author entities."""
    
    async def find_by_name(self, name: str) -> List[Author]: ...
    async def find_by_orcid(self, orcid: str) -> Optional[Author]: ...
    async def find_or_create(self, name: str, orcid: Optional[str] = None) -> Author: ...

class IEntityMentionRepository(IRepository[EntityMention], Protocol):
    """Repository interface for EntityMention entities."""
    
    async def find_by_document(self, document_id: str) -> List[EntityMention]: ...
    async def find_by_entity(self, entity_type: str, entity_id: str) -> List[EntityMention]: ...
    async def delete_by_document(self, document_id: str) -> None: ...

class ICitationRepository(IRepository[Citation], Protocol):
    """Repository interface for Citation entities."""
    
    async def find_citations_for_document(self, document_id: str) -> List[Citation]: ...
    async def find_citing_documents(self, document_id: str) -> List[Document]: ...
    async def delete_by_document(self, document_id: str) -> None: ...

class IConnectorExecutionRepository(IRepository[ConnectorExecution], Protocol):
    """Repository interface for ConnectorExecution entities."""
    
    async def find_by_connector(self, connector_name: str) -> List[ConnectorExecution]: ...
    async def find_latest_by_connector(self, connector_name: str) -> Optional[ConnectorExecution]: ...
    async def update_status(self, execution_id: str, status: str, end_time: Optional[datetime] = None) -> ConnectorExecution: ...
```

### Specifications

We implement reusable specifications for common query patterns:

```python
from openbiocure_corelib.data.specification import Specification

class DocumentBySourceIdSpecification(Specification[Document]):
    """Specification for finding documents by source and source_id."""
    
    def __init__(self, source: str, source_id: str):
        self.source = source
        self.source_id = source_id
    
    def to_expression(self):
        return (Document.source == self.source) & (Document.source_id == self.source_id)

class DocumentByDoiSpecification(Specification[Document]):
    """Specification for finding documents by DOI."""
    
    def __init__(self, doi: str):
        self.doi = doi
    
    def to_expression(self):
        return Document.doi == self.doi

class DocumentByProcessingStatusSpecification(Specification[Document]):
    """Specification for finding documents by processing status."""
    
    def __init__(self, status: str):
        self.status = status
    
    def to_expression(self):
        return Document.processing_status == self.status

class AuthorByOrcidSpecification(Specification[Author]):
    """Specification for finding authors by ORCID."""
    
    def __init__(self, orcid: str):
        self.orcid = orcid
    
    def to_expression(self):
        return Author.orcid == self.orcid

class EntityMentionByDocumentSpecification(Specification[EntityMention]):
    """Specification for finding entity mentions by document."""
    
    def __init__(self, document_id: str):
        self.document_id = document_id
    
    def to_expression(self):
        return EntityMention.document_id == self.document_id

class EntityMentionByEntityTypeAndIdSpecification(Specification[EntityMention]):
    """Specification for finding entity mentions by entity type and ID."""
    
    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
    
    def to_expression(self):
        return (EntityMention.entity_type == self.entity_type) & (EntityMention.entity_id == self.entity_id)
```

### Repository Implementations

The concrete implementations leverage the base Repository class from OpenBioCure CoreLib:

```python
from openbiocure_corelib.data.repository import Repository
from openbiocure_corelib.data.db_context import IDbContext
from datetime import datetime, UTC

class DocumentRepository(Repository[Document], IDocumentRepository):
    """Repository implementation for Document entities."""
    
    # No explicit __init__ needed - the engine will handle dependency injection
    # The Repository base class from OpenBioCure CoreLib handles the db_context
    
    async def find_by_source_id(self, source: str, source_id: str) -> Optional[Document]:
        """Find a document by source and source_id."""
        return await self.find_one(DocumentBySourceIdSpecification(source, source_id))
    
    async def find_by_doi(self, doi: str) -> Optional[Document]:
        """Find a document by DOI."""
        return await self.find_one(DocumentByDoiSpecification(doi))
    
    async def find_by_processing_status(self, status: str) -> List[Document]:
        """Find documents by processing status."""
        return await self.find(DocumentByProcessingStatusSpecification(status))
    
    async def update_processing_status(self, document_id: str, status: str) -> Document:
        """Update the processing status of a document."""
        document = await self.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document not found: {document_id}")
        
        document.processing_status = status
        document.updated_at = datetime.now(UTC)
        
        return await self.update(document)

class AuthorRepository(Repository[Author], IAuthorRepository):
    """Repository implementation for Author entities."""
    
    # No explicit __init__ needed - the engine will handle dependency injection

## Directory Structure

The HerpAI-Ingestion project follows a modular directory structure that clearly separates the connector SDK, core ingestion system, and individual connectors:

```sh
herpai-ingestion/
├── README.md
├── pyproject.toml
├── LICENSE
│
├── herpai_connector_sdk/        # The connector SDK (future separate package)
│   ├── __init__.py
│   ├── interfaces.py            # Core interfaces (IConnector)
│   ├── base.py                  # Base implementations (BaseConnector)
│   ├── models.py                # Data models (Document)
│   ├── exceptions.py            # Custom exceptions
│   └── utils/                   # Utilities for connectors
│
├── herpai_ingestion/            # Main ingestion system
│   ├── __init__.py
│   ├── cli/                     # Command-line interface
│   │   ├── __init__.py
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   ├── ingest.py        # Ingestion command
│   │   │   ├── worker.py        # Worker command
│   │   │   └── scheduler.py     # Scheduler command
│   │   └── main.py              # CLI entry point
│   │
│   ├── api/                     # REST API
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── ingestion.py     # Ingestion endpoints
│   │   │   └── connectors.py    # Connector endpoints
│   │   └── main.py              # API entry point
│   │
│   ├── domain/                  # Domain entities
│   │   ├── __init__.py
│   │   ├── document.py          # Document entity
│   │   ├── author.py            # Author entity
│   │   ├── entity_mention.py    # EntityMention entity
│   │   └── connector_execution.py # Connector execution entity
│   │
│   ├── repository/              # Repository interfaces & implementations
│   │   ├── __init__.py
│   │   ├── interfaces/
│   │   │   ├── __init__.py
│   │   │   ├── document_repository.py
│   │   │   └── connector_execution_repository.py
│   │   ├── specifications/
│   │   │   ├── __init__.py
│   │   │   ├── document_specifications.py
│   │   │   └── connector_execution_specifications.py
│   │   └── implementations/
│   │       ├── __init__.py
│   │       ├── document_repository.py
│   │       └── connector_execution_repository.py
│   │
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── ingestion_service.py # Main ingestion orchestration
│   │   ├── document_processor.py # Document processing
│   │   ├── storage_manager.py    # Storage management
│   │   └── connector_registry.py # Connector registry
│   │
│   ├── workers/                 # Background workers
│   │   ├── __init__.py
│   │   ├── tasks/
│   │   │   ├── __init__.py
│   │   │   ├── document_processing_task.py
│   │   │   └── ingest_task.py
│   │   ├── executors/
│   │   │   ├── __init__.py
│   │   │   ├── local_executor.py
│   │   │   └── rabbitmq_executor.py
│   │   └── worker.py            # Worker process entry point
│   │
│   ├── storage/                 # Storage providers
│   │   ├── __init__.py
│   │   ├── interfaces.py        # Storage interfaces
│   │   ├── local_storage.py     # Local file storage
│   │   ├── azure_storage.py     # Azure Blob storage
│   │   └── s3_storage.py        # S3 storage
│   │
│   ├── scheduling/              # Scheduled jobs
│   │   ├── __init__.py
│   │   ├── scheduler.py         # Scheduler implementation
│   │   └── jobs.py              # Job definitions
│   │
│   ├── startup/                 # Startup tasks
│   │   ├── __init__.py
│   │   ├── connector_discovery_task.py
│   │   └── storage_initialization_task.py
│   │
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── logging.py           # Logging utilities
│       └── file_utils.py        # File handling utilities
│
├── connectors/                  # All connectors in one place for now
│   ├── pubmed/
│   │   ├── __init__.py
│   │   ├── connector.py         # PubMed connector implementation
│   │   └── connector.yaml       # Specification file
│   ├── clinicaltrials/
│   │   ├── __init__.py
│   │   ├── connector.py
│   │   └── connector.yaml
│   └── europepmc/
│       ├── __init__.py
│       ├── connector.py
│       └── connector.yaml
│
└── tests/                       # Centralized tests
    ├── sdk/                     # Connector SDK tests
    ├── ingestion/               # Ingestion system tests
    │   ├── services/
    │   ├── workers/
    │   └── repository/
    └── connectors/              # Connector implementation tests
        ├── pubmed/
        ├── clinicaltrials/
        └── europepmc/
```

## Engine Initialization and Startup

The system leverages OpenBioCure CoreLib's engine for dependency resolution, startup tasks, and configuration:

```python
import asyncio
import logging
from openbiocure_corelib import engine
from openbiocure_corelib.core.startup import StartupTask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Define custom startup tasks
class ConnectorDiscoveryTask(StartupTask):
    """Startup task to discover and register available connectors."""
    
    # Run after database initialization (order 30)
    order = 40
    
    async def execute(self) -> None:
        """Execute the connector discovery."""
        logger.info("Discovering connectors...")
        
        # Resolve connector registry from the engine
        connector_registry = engine.resolve(ConnectorRegistry)
        
        # Discover available connectors
        connectors = await connector_registry.discover_connectors()
        
        logger.info(f"Discovered {len(connectors)} connectors: {', '.join(connectors)}")

async def main():
    # Initialize and start the engine
    # The engine will auto-discover our domain entities, repositories, and startup tasks
    engine.initialize()
    await engine.start()
    
    # Now we can resolve repositories and services
    document_repository = engine.resolve(IDocumentRepository)
    connector_registry = engine.resolve(ConnectorRegistry)
    
    # Create ingestion service
    ingestion_service = IngestionService(
        connector_registry=connector_registry
    )
    
    # Example ingestion
    result = await ingestion_service.ingest(
        source="pubmed",
        query="herpes simplex virus treatment",
        limit=100
    )
    
    logger.info(f"Processed {result['documents_processed']} documents")

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration System

The configuration system is built on the OpenBioCure CoreLib's configuration capabilities:

```yaml
# config.yaml
database:
  type: postgresql
  host: ${DB_HOST:-localhost}
  port: 5432
  database: herpai
  username: ${DB_USER}
  password: ${DB_PASSWORD}

storage:
  type: azure
  azure:
    account_name: ${AZURE_STORAGE_ACCOUNT}
    account_key: ${AZURE_STORAGE_KEY}
    container_name: herpai-datalake
    prefix: documents/

connectors:
  pubmed:
    enabled: true
    api_key: ${PUBMED_API_KEY:-}
  europepmc:
    enabled: true
  clinicaltrials:
    enabled: true

rabbitmq:
  host: ${RABBITMQ_HOST:-localhost}
  port: 5672
  username: ${RABBITMQ_USER:-guest}
  password: ${RABBITMQ_PASSWORD:-guest}

# Custom startup task configuration
startup_tasks:
  ConnectorDiscoveryTask:
    enabled: true
    scan_paths:
      - herpai_ingestion.connectors
      - custom_connectors

scheduler:
  enabled: true
  jobs:
    - source: pubmed
      query: "herpes simplex virus"
      schedule: "0 1 * * *"  # Daily at 1 AM
      limit: 1000
    - source: clinicaltrials
      query: "herpes zoster vaccine"
      schedule: "0 2 * * *"  # Daily at 2 AM
      limit: 100

processing:
  document_processor:
    grobid:
      url: ${GROBID_URL:-http://localhost:8070}
  entity_extractor:
    model: biobert
    threshold: 0.7
```