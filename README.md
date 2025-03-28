# HerpAI-Ingestion

A comprehensive library for ingesting, processing, and storing biomedical data from various sources.

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Overview

HerpAI-Ingestion is a powerful toolkit designed for the extraction, transformation, and loading of biomedical data from multiple public repositories. It implements a unified interface for accessing diverse data sources, processes documents using advanced tools like GROBID, and provides robust storage solutions for both structured metadata and raw documents.

## Features

- **Multiple Source Connectors**: Unified interface for PubMed, Europe PMC, ClinicalTrials.gov, and more
- **Document Processing**: PDF parsing and structured extraction using GROBID
- **Data Lake Storage**: Support for S3, NFS, and Azure Blob Storage backends
- **Metadata Cataloging**: PostgreSQL database for structured metadata storage and querying
- **Pagination**: Source-specific pagination with checkpoint recovery
- **Distributed Processing**: RabbitMQ integration for scalable processing
- **Scheduled Ingestion**: Cron-based scheduling for automated data updates
- **Retry Mechanisms**: Comprehensive error handling with exponential backoff

## Installation

```bash
pip install herpai-ingestion
```

## Quick Start

```python
from herpai_ingestion.cli import main

# Run the CLI directly
if __name__ == "__main__":
    main()
```

Or use the CLI:

```bash
# Setup your config.yaml file first
herpai ingest --source pubmed --query "covid-19" --limit 100
```

## Configuration

HerpAI-Ingestion uses a YAML configuration file. You can specify the path with `--config` or use the default location at `./config.yaml`.

Example config:

```yaml
database:
  host: localhost
  port: 5432
  database: herpai
  username: user
  password: password

storage:
  type: azure
  azure:
    account_name: your_account_name
    account_key: your_account_key
    container_name: herpai-datalake
    prefix: documents/
  
sources:
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
  ingestion_schedule: "0 0 * * *"  # Daily at midnight
```

## CLI Usage

HerpAI-Ingestion provides a comprehensive CLI:

```
Commands:
  ingest      Run ingestion from a specific source
  process     Process documents (PDF parsing, etc.)
  catalog     Manage the metadata catalog
  scheduler   Manage scheduled ingestion jobs
  sources     List and query available data sources
  storage     Perform data lake operations
```

## Architecture

The library follows a modular architecture:

- **Connectors**: Source-specific adapters for data retrieval
- **Processors**: Document processing and data extraction
- **Storage**: Data lake and metadata storage services
- **Services**: Business logic implementation
- **Scheduler**: Cron-based scheduling system
- **CLI**: Command-line interface

## Development

### Prerequisites

- Python 3.9+
- PostgreSQL
- RabbitMQ
- GROBID server (for PDF processing)

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
