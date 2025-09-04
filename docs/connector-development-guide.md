# Connector Development Guide

This guide explains how to create new connectors for the OpenBioCure Connectors Core system.

## Overview

Connectors are the core components that interface with external data sources. They provide a standardized way to search, retrieve, and process data from various APIs and databases.

## Architecture

### Core Components

1. **IConnector Interface** - Defines the contract all connectors must implement
2. **BaseConnector** - Provides common functionality and utilities
3. **ConnectorCapability** - Enumeration of connector features
4. **ConnectorRegistry** - Manages connector discovery and configuration

### Data Flow

```
User Request → Connector → External API → Data Processing → Standardized Response
```

## Creating a New Connector

### Step 1: Create Connector Directory

```bash
mkdir -p connectors/your_connector
cd connectors/your_connector
```

### Step 2: Create Connector Implementation

Create `connector.py`:

```python
"""Your Connector Implementation."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from obc_connector_sdk.base_connector import BaseConnector

logger = logging.getLogger(__name__)


class YourConnector(BaseConnector):
    """Your connector implementation."""

    def __init__(self):
        super().__init__(
            base_url="https://api.yourservice.com/",
            rate_limit=10,  # Adjust based on API limits
        )

    async def search(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """Search for documents."""
        params = {
            "q": query,
            "limit": limit,
        }

        try:
            response = await self.make_request("search", params)

            # Extract results
            documents = response.get("results", [])
            document_ids = [doc.get("id") for doc in documents]
            total_count = response.get("total", 0)

            return {
                "query": query,
                "total_results": total_count,
                "document_ids": document_ids,
                "metadata": {"source": "your_service"},
            }
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "query": query,
                "total_results": 0,
                "document_ids": [],
                "metadata": {"source": "your_service", "error": str(e)},
            }

    async def get_by_id(self, doc_id: str) -> Dict[str, Any]:
        """Get document by ID."""
        try:
            response = await self.make_request(f"documents/{doc_id}")

            return {
                "id": doc_id,
                "title": response.get("title", "Untitled"),
                "abstract": response.get("abstract"),
                "authors": self._extract_authors(response),
                "publication_date": self._extract_date(response),
                "doi": response.get("doi"),
                "url": response.get("url"),
                "source": "your_service",
                "metadata": response.get("metadata", {}),
            }
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            return {"id": doc_id, "error": str(e), "source": "your_service"}

    def _extract_authors(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract authors from response."""
        authors = []
        for author_data in response.get("authors", []):
            authors.append({
                "name": author_data.get("name", ""),
                "orcid": author_data.get("orcid"),
                "affiliation": author_data.get("affiliation"),
            })
        return authors

    def _extract_date(self, response: Dict[str, Any]) -> Optional[datetime]:
        """Extract publication date."""
        date_str = response.get("publication_date")
        if date_str:
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError:
                return None
        return None

    async def authenticate(self, config: Dict[str, Any]) -> None:
        """Configure authentication."""
        if config.get("api_key"):
            self.api_key = config["api_key"]
            logger.info("Connector configured with API key")

    async def get_updates(self, since: datetime) -> List[Dict[str, Any]]:
        """Get updates since a specific date."""
        date_str = since.strftime("%Y-%m-%d")
        query = f"updated_since:{date_str}"
        return await self.search(query, limit=1000)
```

### Step 3: Create Connector Configuration

Create `connector.yaml`:

```yaml
name: your_connector
display_name: Your Service Connector
description: Connects to Your Service API for data retrieval
version: 1.0.0

capabilities:
  supports_fulltext: true
  supports_advanced_search: true
  supports_date_filtering: true
  requires_authentication: true
  supports_native_pagination: true
  supports_document_content: true
  supports_json_content: true

api:
  base_url: https://api.yourservice.com/
  rate_limit:
    requests_per_second: 10
    daily_limit: 10000
  endpoints:
    search:
      path: "search"
      method: "GET"
      params: {}
      response:
        mapping:
          id: "id"
          title: "title"
          abstract: "abstract"
          authors: "authors"
    documents:
      path: "documents"
      method: "GET"
      params: {}
      response:
        mapping:
          id: "id"
          title: "title"
          content: "content"

configuration:
  properties:
    - name: api_key
      type: string
      required: true
      description: API key for authentication
      sensitive: true
    - name: batch_size
      type: integer
      required: false
      default: 100
      description: Number of items to retrieve in each batch
```

### Step 4: Create Package Init File

Create `__init__.py`:

```python
"""Your connector package."""
```

## Capabilities

Define what your connector can do using the `ConnectorCapability` enum:

### Content Type Capabilities
- `SUPPORTS_DOCUMENT_CONTENT` - Traditional document-based content
- `SUPPORTS_JSON_CONTENT` - JSON-structured data
- `SUPPORTS_STRING_CONTENT` - Plain text content
- `SUPPORTS_BINARY_CONTENT` - Binary data

### Feature Capabilities
- `SUPPORTS_FULLTEXT` - Can retrieve full text content
- `SUPPORTS_ADVANCED_SEARCH` - Complex search queries
- `SUPPORTS_DATE_FILTERING` - Date range filtering
- `REQUIRES_AUTHENTICATION` - Needs authentication
- `SUPPORTS_AUTHOR_SEARCH` - Search by author
- `SUPPORTS_INSTITUTION_SEARCH` - Search by institution
- `SUPPORTS_CITATION_NETWORK` - Citation relationships
- `SUPPORTS_INCREMENTAL_UPDATES` - Get updates since date

## Testing Your Connector

### Unit Testing

```python
import pytest
from connectors.your_connector.connector import YourConnector

@pytest.mark.asyncio
async def test_search():
    connector = YourConnector()
    results = await connector.search("test query", limit=5)

    assert "query" in results
    assert "total_results" in results
    assert "document_ids" in results
    assert results["query"] == "test query"

@pytest.mark.asyncio
async def test_get_by_id():
    connector = YourConnector()
    doc = await connector.get_by_id("test_id")

    assert "id" in doc
    assert doc["id"] == "test_id"
    assert "source" in doc
```

### Integration Testing

```bash
# Test your connector using the CLI
.venv/bin/python -m obc_ingestion.cli debug test your_connector --query "test" --limit 5

# Test with authentication
.venv/bin/python -m obc_ingestion.cli debug test your_connector --query "test" --api-key "your_key"
```

### Validation

```bash
# Validate your connector configuration
.venv/bin/python tools/validate_connectors.py
```

## Best Practices

### Error Handling

```python
async def search(self, query: str, limit: int = 100) -> Dict[str, Any]:
    try:
        response = await self.make_request("search", params)
        # Process response
        return processed_result
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {
            "query": query,
            "total_results": 0,
            "document_ids": [],
            "metadata": {"error": str(e)},
        }
```

### Rate Limiting

```python
def __init__(self):
    super().__init__(
        base_url="https://api.service.com/",
        rate_limit=10,  # Respect API limits
    )
```

### Data Extraction

```python
def _extract_authors(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract and normalize author data."""
    authors = []
    for author_data in response.get("authors", []):
        # Normalize data structure
        author = {
            "name": author_data.get("name", "").strip(),
            "orcid": author_data.get("orcid"),
            "affiliation": author_data.get("affiliation"),
        }
        if author["name"]:  # Only add if name exists
            authors.append(author)
    return authors
```

### Configuration

```python
async def authenticate(self, config: Dict[str, Any]) -> None:
    """Handle authentication configuration."""
    if config.get("api_key"):
        self.api_key = config["api_key"]
        # Update headers or other auth mechanisms
        self.http_client.headers.update({"Authorization": f"Bearer {self.api_key}"})

    if config.get("email"):
        self.email = config["email"]
        # Use email for better rate limits
```

## Common Patterns

### Pagination

```python
async def search_with_pagination(self, query: str, limit: int = 100) -> Dict[str, Any]:
    all_results = []
    page = 1
    per_page = min(limit, 100)  # API max per page

    while len(all_results) < limit:
        params = {
            "q": query,
            "page": page,
            "per_page": per_page,
        }

        response = await self.make_request("search", params)
        results = response.get("results", [])

        if not results:
            break

        all_results.extend(results)
        page += 1

    return all_results[:limit]
```

### Caching

```python
import asyncio
from functools import lru_cache

class YourConnector(BaseConnector):
    def __init__(self):
        super().__init__(base_url="...", rate_limit=10)
        self._cache = {}

    async def get_by_id(self, doc_id: str) -> Dict[str, Any]:
        # Check cache first
        if doc_id in self._cache:
            return self._cache[doc_id]

        # Fetch from API
        result = await self._fetch_from_api(doc_id)

        # Cache result
        self._cache[doc_id] = result
        return result
```

### Retry Logic

```python
import asyncio
from typing import Optional

async def make_request_with_retry(self, endpoint: str, params: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
    for attempt in range(max_retries):
        try:
            return await self.make_request(endpoint, params)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e

            # Exponential backoff
            wait_time = 2 ** attempt
            await asyncio.sleep(wait_time)
```

## Documentation

### Connector Documentation

Create comprehensive documentation for your connector:

1. **Overview** - What the connector does
2. **Configuration** - How to set it up
3. **Usage Examples** - Code examples
4. **Data Models** - Response structures
5. **Rate Limits** - API limitations
6. **Error Handling** - Common issues
7. **Troubleshooting** - Debug tips

### API Documentation

Document the external API you're connecting to:

- Endpoints and methods
- Authentication requirements
- Rate limits
- Response formats
- Error codes

## Contributing

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Implement your connector
4. Add tests
5. Update documentation
6. Submit pull request

### Code Review Checklist

- [ ] Connector implements `IConnector` interface
- [ ] Configuration YAML is valid
- [ ] Error handling is comprehensive
- [ ] Rate limiting is respected
- [ ] Tests are included
- [ ] Documentation is complete
- [ ] Code follows project style

## Examples

See the existing connectors for reference:

- **PubMed Connector** (`connectors/pubmed/`) - Simple implementation
- **OpenAlex Connector** (`connectors/openalex/`) - Advanced features

## Support

For questions or issues:

1. Check existing documentation
2. Review existing connector implementations
3. Open an issue on GitHub
4. Join the community discussions
