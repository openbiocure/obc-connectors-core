#!/bin/bash

# Script to generate the HerpAI-Ingestion project structure
# Author: OpenBioCure
# Usage: ./generate_herpai_ingestion.sh

set -e  # Exit on error

echo "Creating HerpAI-Ingestion project structure"

# Create the directory structure
mkdir -p src/{cli,core,connectors,processors,storage,services,scheduler,startup}
mkdir -p examples
mkdir -p tests

# Create README.md
cat > README.md << 'EOF'
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
EOF

# Create LICENSE
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2023 OpenBioCure

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# Create pyproject.toml
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "herpai-ingestion"
version = "0.1.0"
description = "A comprehensive library for ingesting biomedical data from various sources"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "OpenBioCure", email = "openbiocure@gmail.com"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
    "Topic :: Scientific/Engineering :: Medical Science Apps."
]
dependencies = [
    "herpai-lib",
    "aiohttp",
    "boto3",
    "azure-storage-blob",
    "requests",
    "schedule",
    "pika",
    "python-dotenv",
    "tenacity",
    "lxml",
    "beautifulsoup4"
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
    "black",
    "isort",
    "mypy",
    "flake8",
    "tox",
    "coverage",
    "pytest-cov",
    "pre-commit"
]
docs = [
    "sphinx",
    "sphinx-rtd-theme",
    "myst-parser"
]

[project.scripts]
herpai = "src.cli.main:app"

[tool.black]
line-length = 88
target-version = ["py39"]

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
EOF

# Create config.yaml
cat > config.yaml << 'EOF'
# HerpAI-Ingestion Configuration

app:
  name: "HerpAI-Ingestion"
  log_level: "INFO"

database:
  host: "localhost"
  port: 5432
  database: "herpai"
  username: "postgres"
  password: "postgres"
  dialect: "postgresql"
  driver: "asyncpg"
  pool_size: 5
  max_overflow: 10
  schema: "public"

storage:
  type: "azure"  # Options: s3, nfs, azure
  azure:
    account_name: ""
    account_key: ""
    container_name: "herpai-datalake"
    prefix: "documents/"
  s3:
    bucket: "herpai-datalake"
    prefix: "documents/"
    region: "us-east-1"
    access_key: ""  # Leave empty to use IAM role or environment variables
    secret_key: ""
  nfs:
    mount_point: "/mnt/data"
    path: "documents/"

rabbitmq:
  host: "localhost"
  port: 5672
  username: "guest"
  password: "guest"
  vhost: "/"
  exchange: "herpai"
  queue_prefix: "herpai_ingestion_"
  routing_key_prefix: "herpai.ingestion."
  retry:
    max_attempts: 5
    initial_interval: 1.0  # seconds
    max_interval: 60.0     # seconds
    multiplier: 2.0

grobid:
  host: "localhost"