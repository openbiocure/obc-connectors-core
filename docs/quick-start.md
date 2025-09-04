# Quick Start Guide

Get up and running with OpenBioCure Connectors Core in minutes.

## Installation

### Prerequisites

- Python 3.9 or higher
- Git

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/openbiocure/obc-connectors-core.git
   cd obc-connectors-core
   ```

2. **Create virtual environment:**
   ```bash
   make venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   make install-deps
   ```

4. **Install development dependencies:**
   ```bash
   make install-dev-deps
   ```

## Basic Usage

### Test Available Connectors

```bash
# List available connectors
.venv/bin/python -m obc_ingestion.cli debug test --help

# Test PubMed connector
.venv/bin/python -m obc_ingestion.cli debug test pubmed --query "machine learning" --limit 5

# Test OpenAlex connector
.venv/bin/python -m obc_ingestion.cli debug test openalex --query "artificial intelligence" --limit 5
```

### Using Connectors in Code

```python
import asyncio
from connectors.openalex.connector import OpenAlexConnector

async def main():
    # Create connector
    connector = OpenAlexConnector()
    
    # Search for papers
    results = await connector.search("machine learning", limit=10)
    print(f"Found {results['total_results']} results")
    
    # Get a specific document
    if results['document_ids']:
        doc_id = results['document_ids'][0]
        doc = await connector.get_by_id(doc_id)
        print(f"Title: {doc['title']}")
        print(f"Authors: {[author['name'] for author in doc['authors']]}")
    
    # Clean up
    await connector.close()

# Run the example
asyncio.run(main())
```

## Available Connectors

### PubMed Connector

Access to the PubMed/NCBI E-utilities API for biomedical literature.

```bash
# Search PubMed
.venv/bin/python -m obc_ingestion.cli debug test pubmed --query "cancer research" --limit 5

# Get specific paper
.venv/bin/python -m obc_ingestion.cli debug test pubmed --id "12345678"
```

**Features:**
- Search biomedical literature
- Retrieve paper metadata
- Author and publication information
- DOI and citation data

### OpenAlex Connector

Access to the OpenAlex API for comprehensive scholarly data.

```bash
# Search OpenAlex
.venv/bin/python -m obc_ingestion.cli debug test openalex --query "artificial intelligence" --limit 5

# Get specific work
.venv/bin/python -m obc_ingestion.cli debug test openalex --id "W2033731173"
```

**Features:**
- Search academic papers
- Author and institution data
- Citation networks
- Open access information
- Research concepts and topics

## Configuration

### Environment Variables

Create a `.env` file for configuration:

```bash
# Database configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=obc_ingestion
DB_USER=postgres
DB_PASSWORD=your_password

# API Keys (optional)
PUBMED_API_KEY=your_pubmed_key
OPENALEX_EMAIL=your_email@example.com
```

### Connector Configuration

Each connector can be configured with specific settings:

```python
# Configure OpenAlex with email for better rate limits
config = {"email": "your-email@example.com"}
await connector.authenticate(config)

# Configure PubMed with API key
config = {"api_key": "your-pubmed-api-key"}
await connector.authenticate(config)
```

## Development

### Running Tests

```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration
make test-connectors
```

### Code Quality

```bash
# Format code
make format

# Check formatting
make check-format

# Run linters
make lint

# Run all quality checks
make quality-check
```

### Adding New Connectors

1. **Create connector directory:**
   ```bash
   mkdir -p connectors/your_connector
   ```

2. **Implement connector:**
   ```python
   # connectors/your_connector/connector.py
   from obc_connector_sdk.base_connector import BaseConnector
   
   class YourConnector(BaseConnector):
       # Implementation here
   ```

3. **Create configuration:**
   ```yaml
   # connectors/your_connector/connector.yaml
   name: your_connector
   display_name: Your Connector
   # Configuration here
   ```

4. **Test your connector:**
   ```bash
   .venv/bin/python -m obc_ingestion.cli debug test your_connector --query "test"
   ```

See the [Connector Development Guide](connector-development-guide.md) for detailed instructions.

## Docker Development

### Start Development Environment

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### Services Included

- **PostgreSQL** - Database (port 5432)
- **RabbitMQ** - Message queue (port 5672, management UI: 15672)
- **Qdrant** - Vector database (port 6333)
- **MinIO** - Object storage (port 9000, console: 9001)
- **GROBID** - PDF processing (port 8070)

### Access Services

- **RabbitMQ Management:** http://localhost:15672 (guest/guest)
- **MinIO Console:** http://localhost:9001 (minioadmin/minioadmin)
- **Qdrant Dashboard:** http://localhost:6333/dashboard

## Troubleshooting

### Common Issues

1. **Import errors:**
   ```bash
   # Make sure virtual environment is activated
   source .venv/bin/activate
   
   # Reinstall dependencies
   make install-deps
   ```

2. **API rate limits:**
   ```bash
   # Add email for OpenAlex
   .venv/bin/python -m obc_ingestion.cli debug test openalex --api-key "your-email@example.com"
   
   # Add API key for PubMed
   .venv/bin/python -m obc_ingestion.cli debug test pubmed --api-key "your-pubmed-key"
   ```

3. **Network issues:**
   ```bash
   # Check internet connection
   ping api.openalex.org
   ping eutils.ncbi.nlm.nih.gov
   ```

4. **Validation errors:**
   ```bash
   # Validate connector configurations
   .venv/bin/python tools/validate_connectors.py
   ```

### Getting Help

1. **Check documentation:** [Connector Development Guide](connector-development-guide.md)
2. **Review examples:** Look at existing connectors
3. **Open an issue:** GitHub Issues
4. **Community:** Join discussions

## Next Steps

1. **Explore connectors:** Try different search queries and parameters
2. **Read documentation:** Understand the full capabilities
3. **Create your own:** Build a connector for your data source
4. **Contribute:** Submit improvements and new connectors

## Examples

### Search and Process Results

```python
import asyncio
from connectors.openalex.connector import OpenAlexConnector

async def process_papers():
    connector = OpenAlexConnector()
    
    # Search for papers
    results = await connector.search("machine learning in healthcare", limit=20)
    
    print(f"Found {results['total_results']} papers")
    
    # Process each paper
    for doc_id in results['document_ids'][:5]:  # Process first 5
        doc = await connector.get_by_id(doc_id)
        
        print(f"\nTitle: {doc['title']}")
        print(f"DOI: {doc.get('doi', 'N/A')}")
        print(f"Authors: {len(doc['authors'])}")
        print(f"Concepts: {len(doc['metadata']['concepts'])}")
        
        # Extract key concepts
        concepts = doc['metadata']['concepts'][:3]  # Top 3 concepts
        print(f"Key concepts: {[c['display_name'] for c in concepts]}")
    
    await connector.close()

asyncio.run(process_papers())
```

### Batch Processing

```python
import asyncio
from connectors.pubmed.connector import PubMedConnector

async def batch_process():
    connector = PubMedConnector()
    
    queries = [
        "cancer treatment",
        "diabetes research", 
        "heart disease prevention"
    ]
    
    all_results = []
    
    for query in queries:
        print(f"Searching: {query}")
        results = await connector.search(query, limit=10)
        all_results.extend(results['document_ids'])
        print(f"Found {len(results['document_ids'])} papers")
    
    print(f"\nTotal papers found: {len(all_results)}")
    
    await connector.close()

asyncio.run(batch_process())
```

This quick start guide should get you up and running quickly. For more detailed information, see the full documentation in the `docs/` directory.
