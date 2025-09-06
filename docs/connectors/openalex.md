# OpenAlex Connector

The OpenAlex connector provides access to the OpenAlex API, a comprehensive database of scholarly works, authors, institutions, and more. OpenAlex is a free and open catalog of the world's scholarly papers.

## Overview

OpenAlex is a free, open catalog of the world's scholarly papers. It provides access to:
- Academic papers and research articles
- Author information and profiles
- Institution data
- Citation networks
- Open access information
- Research concepts and topics

## Features

### Core Capabilities
- ✅ **Full-text search** - Search across all scholarly works
- ✅ **Advanced search** - Complex queries with filters
- ✅ **Date filtering** - Search by publication date ranges
- ✅ **Author search** - Find works by specific authors
- ✅ **Institution search** - Find works from specific institutions
- ✅ **Citation network** - Access citation relationships
- ✅ **Incremental updates** - Get updates since a specific date
- ✅ **Native pagination** - Efficient handling of large result sets

### Data Types Supported
- **Document content** - Academic papers and articles
- **JSON content** - Structured API responses
- **Metadata extraction** - Authors, concepts, keywords, citations

## Configuration

### Basic Configuration

```yaml
# connectors/openalex/connector.yaml
name: openalex
display_name: OpenAlex
description: Connects to the OpenAlex API for academic literature and research data
version: 1.0.0

capabilities:
  supports_fulltext: true
  supports_advanced_search: true
  supports_date_filtering: true
  requires_authentication: false
  supports_native_pagination: true
  supports_document_content: true
  supports_json_content: true
  supports_author_search: true
  supports_institution_search: true
  supports_citation_network: true
  supports_incremental_updates: true

api:
  base_url: https://api.openalex.org/
  rate_limit:
    requests_per_second: 10
    daily_limit: 100000
```

### Optional Configuration

```python
# Email for better rate limits (recommended)
config = {
    "email": "your-email@example.com"
}

await connector.authenticate(config)
```

## Usage Examples

### Basic Search

```python
from connectors.openalex.connector import OpenAlexConnector

async def search_example():
    connector = OpenAlexConnector()

    # Search for papers about machine learning
    results = await connector.search("machine learning", limit=10)

    print(f"Found {results['total_results']} results")
    for doc_id in results['document_ids']:
        print(f"- {doc_id}")

    await connector.close()
```

### Document Retrieval

```python
async def get_document_example():
    connector = OpenAlexConnector()

    # Get a specific document
    doc = await connector.get_by_id("W2033731173")

    print(f"Title: {doc['title']}")
    print(f"Authors: {[author['name'] for author in doc['authors']]}")
    print(f"DOI: {doc['doi']}")
    print(f"Publication Date: {doc['publication_date']}")

    await connector.close()
```

### Author Search

```python
async def author_search_example():
    connector = OpenAlexConnector()

    # Search for works by a specific author
    results = await connector.search_by_author("Seyedali Mirjalili", limit=5)

    print(f"Found {results['total_results']} works by this author")
    for doc_id in results['document_ids']:
        print(f"- {doc_id}")

    await connector.close()
```

### Institution Search

```python
async def institution_search_example():
    connector = OpenAlexConnector()

    # Search for works from a specific institution
    results = await connector.search_by_institution("Stanford University", limit=5)

    print(f"Found {results['total_results']} works from this institution")
    for doc_id in results['document_ids']:
        print(f"- {doc_id}")

    await connector.close()
```

### Incremental Updates

```python
from datetime import datetime, timedelta

async def incremental_updates_example():
    connector = OpenAlexConnector()

    # Get works published in the last 7 days
    since_date = datetime.now() - timedelta(days=7)
    results = await connector.get_updates(since_date)

    print(f"Found {len(results['document_ids'])} new works")

    await connector.close()
```

## CLI Usage

### Search for Papers

```bash
# Search for papers about cancer research
.venv/bin/python -m obc_ingestion.cli debug test openalex --query "cancer research" --limit 5

# Search for papers about machine learning
.venv/bin/python -m obc_ingestion.cli debug test openalex --query "machine learning" --limit 10
```

### Get Specific Document

```bash
# Get a specific document by OpenAlex ID
.venv/bin/python -m obc_ingestion.cli debug test openalex --id "W2033731173"
```

### With Email Configuration

```bash
# Configure with email for better rate limits
.venv/bin/python -m obc_ingestion.cli debug test openalex --query "artificial intelligence" --api-key "your-email@example.com"
```

## Data Model

### Document Structure

```python
{
    "id": "W2033731173",
    "title": "Let a biogeography-based optimizer train your Multi-Layer Perceptron",
    "abstract": "Abstract text...",  # May be None if not available
    "authors": [
        {
            "name": "Seyedali Mirjalili",
            "orcid": "https://orcid.org/0000-0002-1443-9458",
            "affiliation": "Griffith University",
            "position": "first"
        }
    ],
    "publication_date": datetime(2014, 2, 3),
    "doi": "10.1016/j.ins.2014.01.038",
    "url": "https://openalex.org/W2033731173",
    "source": "openalex",
    "metadata": {
        "type": "article",
        "language": "en",
        "is_oa": False,
        "oa_url": None,
        "cited_by_count": 311,
        "concepts": [
            {
                "id": "https://openalex.org/C114466953",
                "display_name": "Initialization",
                "score": 0.80425894,
                "level": 2
            }
        ],
        "keywords": ["Initialization", "Maxima and minima", "Computer science"]
    }
}
```

### Search Result Structure

```python
{
    "query": "machine learning",
    "total_results": 23,
    "document_ids": ["W2033731173", "W2849545935", "W4404895947"],
    "metadata": {
        "source": "openalex",
        "page": 1,
        "per_page": 10,
        "results_returned": 3
    }
}
```

## Rate Limits

OpenAlex has generous rate limits:
- **10 requests per second** (without email)
- **100,000 requests per day** (with email)
- **No authentication required** (but email recommended)

### Best Practices

1. **Include your email** in requests for better rate limits
2. **Respect rate limits** - the connector automatically handles this
3. **Use pagination** for large result sets
4. **Cache results** when possible to reduce API calls

## Error Handling

The connector includes comprehensive error handling:

```python
try:
    results = await connector.search("query")
    if results.get("error"):
        print(f"Search failed: {results['error']}")
    else:
        print(f"Found {results['total_results']} results")
except Exception as e:
    print(f"Connector error: {e}")
```

### Common Error Scenarios

- **403 Forbidden**: Usually indicates rate limiting or invalid query
- **404 Not Found**: Document ID doesn't exist
- **Network errors**: Connection issues (automatically retried)

## Advanced Features

### Abstract Processing

OpenAlex provides abstracts in an "inverted index" format. The connector automatically converts this to readable text:

```python
# The connector handles this conversion automatically
abstract = doc.get("abstract")  # Returns readable text or None
```

### Concept Extraction

OpenAlex provides rich concept information:

```python
concepts = doc["metadata"]["concepts"]
for concept in concepts:
    print(f"{concept['display_name']}: {concept['score']}")
```

### Open Access Information

```python
is_open_access = doc["metadata"]["is_oa"]
if is_open_access:
    oa_url = doc["metadata"]["oa_url"]
    print(f"Open access available at: {oa_url}")
```

## Integration with OpenBioCure

The OpenAlex connector integrates seamlessly with the OpenBioCure ecosystem:

1. **Standard Interface**: Implements the `IConnector` interface
2. **Capability Discovery**: Declares its capabilities in the YAML config
3. **Error Handling**: Uses standard exception handling
4. **Rate Limiting**: Built-in rate limiting support
5. **Async Operations**: Full async/await support

## Troubleshooting

### Common Issues

1. **Empty search results**: Check your query syntax
2. **Rate limit errors**: Add your email to the configuration
3. **Missing abstracts**: Not all papers have abstracts in OpenAlex
4. **Network timeouts**: Check your internet connection

### Debug Mode

Enable debug logging to see detailed API interactions:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your connector code here
```

## Contributing

To contribute to the OpenAlex connector:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Testing

```bash
# Run connector tests
.venv/bin/python -m obc_ingestion.cli debug test openalex --query "test query" --limit 5

# Run validation
.venv/bin/python tools/validate_connectors.py
```

## Resources

- [OpenAlex API Documentation](https://docs.openalex.org/)
- [OpenAlex Website](https://openalex.org/)
- [OpenBioCure Connector SDK](https://github.com/openbiocure/obc-connectors-core)
- [OpenAlex Python Library](https://github.com/Mearman/openalex-python) (alternative client)
