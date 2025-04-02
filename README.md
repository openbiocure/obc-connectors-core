# HerpAI-Ingestion

A flexible and scalable library for ingesting, processing, and storing biomedical data from various sources, built for the HerpAI Project to enrich AI Agents with domain-specific knowledge and power Retrieval-Augmented Generation (RAG) systems.

## 💬 Join the Community

Come chat with us on Discord: [HerpAI Discord Server](https://discord.gg/72dWs7J9)

## Overview

HerpAI-Ingestion is a powerful toolkit designed for the extraction, transformation, and loading (ETL) of biomedical data from multiple public repositories. Built on top of the HerpAI-CoreLib, it implements a unified interface for accessing diverse data sources while maintaining a clean separation between business logic and deployment infrastructure.

### Purpose and Integration with HerpAI Project

This library serves as a critical component in the HerpAI ecosystem, with the primary purpose of:

1. **Knowledge Acquisition**: Systematically gathering domain-specific knowledge about herpes viruses and related treatments from authoritative sources
2. **Data Enrichment**: Processing and structuring this data for consumption by AI systems
3. **RAG Enablement**: Providing the knowledge foundation for Retrieval-Augmented Generation (RAG) systems that power HerpAI Agents
4. **Domain Specialization**: Ensuring HerpAI's AI capabilities are grounded in accurate, up-to-date biomedical information

The ingested data flows directly into HerpAI's knowledge stores, allowing AI agents to retrieve and reference specific scientific information when answering queries, making recommendations, or analyzing research trends.

## Architecture

HerpAI-Ingestion follows a modular, decoupled architecture with these key components:

1. **Core Business Logic**: Pure code that handles data ingestion independent of deployment model
2. **Abstract Interfaces**: Clear separation between components via well-defined interfaces
3. **Adapters**: Implementations for different environments (local, distributed, Kubernetes)
4. **Message Queue**: Optional RabbitMQ integration for distributed processing

This architecture allows the system to run in various environments without changing the core business logic.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Sources     │     │     Workers     │     │     Storage     │
│  ┌───────────┐  │     │  ┌───────────┐  │     │  ┌───────────┐  │
│  │  PubMed   │  │     │  │  Queue    │  │     │  │ Document  │  │
│  └───────────┘  │     │  │  Worker   │  │     │  │ Repository│  │
│  ┌───────────┐  │     │  └───────────┘  │     │  └───────────┘  │
│  │ Clinical  │  │     │  ┌───────────┐  │     │  ┌───────────┐  │
│  │  Trials   │◄─┼─────┼─►│  Task     │◄─┼─────┼─►│ Metadata  │  │
│  └───────────┘  │     │  │ Executor  │  │     │  │  Storage  │  │
│  ┌───────────┐  │     │  └───────────┘  │     │  └───────────┘  │
│  │ Europe PMC│  │     │  ┌───────────┐  │     │  ┌───────────┐  │
│  └───────────┘  │     │  │ Deployment│  │     │  │ Document  │  │
│       ...       │     │  │  Adapter  │  │     │  │  Storage  │  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         ▲                      ▲                       ▲
         │                      │                       │
         ▼                      ▼                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                        Message Queue                              │
│                          (RabbitMQ)                               │
└──────────────────────────────────────────────────────────────────┘
```

## Features

- **Multiple Source Connectors**: Unified interface for PubMed, Europe PMC, ClinicalTrials.gov, and more
- **Document Processing**: PDF parsing and structured extraction using GROBID
- **Data Lake Storage**: Support for S3, NFS, and Azure Blob Storage backends
- **Metadata Cataloging**: Database storage for structured metadata and querying
- **Deployment Flexibility**: Run locally, in containers, or in Kubernetes
- **Distributed Processing**: Optional RabbitMQ integration for scalable processing
- **Scheduled Ingestion**: Cron-based scheduling for automated data updates
- **Retry Mechanisms**: Comprehensive error handling with exponential backoff

## Installation

```bash
pip install herpai-ingestion
```

## Quick Start

### Basic Usage

```python
from herpai_ingestion.services import IngestionService
from herpai_ingestion.workers import LocalProcessExecutor
import asyncio

async def main():
    # Create a local executor for direct processing
    executor = LocalProcessExecutor()
    
    # Create ingestion service
    service = IngestionService(task_executor=executor)
    
    # Run ingestion from PubMed
    result = await service.ingest_from_pubmed(
        query="herpes simplex virus treatment",
        limit=100
    )
    
    print(f"Processed {result['documents_processed']} documents")

if __name__ == "__main__":
    asyncio.run(main())
```

### CLI Usage

```bash
# Basic ingestion (processes locally)
herpai ingest --source pubmed --query "HSV1 pathogenesis" --limit 100

# Enqueue task for asynchronous processing
herpai ingest --source pubmed --query "HSV2 vaccine" --limit 100 --async

# Start a worker to process queued tasks
herpai worker start --rabbitmq-url amqp://guest:guest@localhost/

# Schedule regular ingestion
herpai scheduler add --name "daily-pubmed" --source pubmed --query "herpes zoster" --schedule "0 0 * * *"
```

## Configuration

HerpAI-Ingestion uses a YAML configuration file. You can specify the path with `--config` or use the default location at `./config.yaml`.

Example config:

```yaml
database:
  type: sqlite
  connection: ":memory:"  # In-memory SQLite database

storage:
  type: azure
  azure:
    account_name: your_account_name
    account_key: your_account_key
    container_name: herpai-datalake
    prefix: documents/
  
connectors:
  pubmed:
    api_key: your_api_key
    batch_size: 100
  europepmc:
    enabled: true
  clinicaltrials:
    enabled: true

rabbitmq:
  host: localhost
  port: 5672
  username: guest
  password: guest
  
scheduler:
  enabled: true
  jobs:
    - source: pubmed
      query: "herpes simplex virus"
      schedule: "0 1 * * *"  # Daily at 1 AM
      limit: 1000
```

## Deployment Models

HerpAI-Ingestion supports multiple deployment models:

### Local Development

Run everything locally for development and testing:

```bash
# Start RabbitMQ (optional)
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management

# Start workers locally
herpai worker start

# Run ingestion
herpai ingest --source pubmed --query "HSV transmission" --async
```

### Docker Compose

For a self-contained deployment:

```yaml
# docker-compose.yml
version: '3'

services:
  rabbitmq:
    image: rabbitmq:management
    ports:
      - "5672:5672"
      - "15672:15672"
  
  api:
    image: herpai-ingestion:latest
    command: python -m herpai_ingestion.api
    ports:
      - "8000:8000"
    environment:
      - RABBITMQ_HOST=rabbitmq
    volumes:
      - ./config.yaml:/app/config.yaml
  
  worker:
    image: herpai-ingestion:latest
    command: python -m herpai_ingestion.cli worker start
    environment:
      - RABBITMQ_HOST=rabbitmq
    volumes:
      - ./config.yaml:/app/config.yaml
```

### Kubernetes

For production environments:

```bash
# Deploy using Helm
helm install herpai-ingestion ./charts/herpai-ingestion
```

The Kubernetes deployment includes:
- API server deployment
- Worker deployment
- RabbitMQ StatefulSet (or external service)
- Configuration via ConfigMaps and Secrets

## Extending the System

### Adding a New Source

1. Create a connector class:

```python
# herpai_ingestion/connectors/new_source.py
from .base import BaseConnector

class NewSourceConnector(BaseConnector):
    async def search(self, query, limit=None):
        # Implementation...
        pass
        
    async def get_by_id(self, id):
        # Implementation...
        pass
```

2. Create a task implementation:

```python
# herpai_ingestion/core/new_source_ingestion.py
class NewSourceIngestionTask:
    def __init__(self, query, limit=None):
        self.query = query
        self.limit = limit
    
    async def execute(self, document_repository):
        # Task implementation...
        pass
```

3. Add to the service:

```python
# herpai_ingestion/services/ingestion_service.py
async def ingest_from_new_source(self, query, limit=None, async_processing=True):
    task_params = {"query": query, "limit": limit}
    
    if async_processing and self.task_queue:
        return await self.task_queue.enqueue_task("NewSource", task_params)
    elif self.task_executor:
        return await self.task_executor.execute_task("NewSource", task_params)
```

## Development

### Prerequisites

- Python 3.9+
- RabbitMQ (optional, for distributed processing)
- HerpAI-CoreLib

### Setting Up Development Environment

1. Clone the repository
   ```bash
   git clone https://github.com/openbiocure/HerpAI-Ingestion.git
   cd HerpAI-Ingestion
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -e ".[dev]"
   ```

4. Run tests
   ```bash
   pytest
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.