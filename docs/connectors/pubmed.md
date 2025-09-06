# PubMed Connector

The PubMed connector provides access to the PubMed/NCBI E-utilities API, a comprehensive database of biomedical literature and research articles.

## Overview

PubMed is a free search engine accessing primarily the MEDLINE database of references and abstracts on life sciences and biomedical topics. It provides access to:
- Biomedical literature and research articles
- Author information and affiliations
- Publication metadata and citations
- Abstract and full-text links
- MeSH (Medical Subject Headings) terms
- Clinical trial information

## Features

### Core Capabilities
- ✅ **Full-text search** - Search across biomedical literature
- ✅ **Advanced search** - Complex queries with filters
- ✅ **Date filtering** - Search by publication date ranges
- ✅ **Author search** - Find works by specific authors
- ✅ **Journal filtering** - Search within specific journals
- ✅ **MeSH term search** - Search using medical subject headings
- ✅ **Incremental updates** - Get updates since a specific date
- ✅ **Native pagination** - Efficient handling of large result sets

### Data Types Supported
- **Document content** - Research papers and articles
- **XML content** - Structured API responses
- **Metadata extraction** - Authors, journals, MeSH terms, citations

## Configuration

### Basic Configuration

```yaml
# connectors/pubmed/connector.yaml
name: pubmed
display_name: PubMed
description: Connects to the PubMed/NCBI E-utilities API for biomedical literature
version: 1.0.0

capabilities:
  supports_fulltext: true
  supports_advanced_search: true
  supports_date_filtering: true
  requires_authentication: false
  supports_native_pagination: true
  supports_document_content: true
  supports_xml_content: true
  supports_author_search: true
  supports_journal_search: true
  supports_mesh_search: true
  supports_incremental_updates: true

api:
  base_url: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
  rate_limit:
    requests_per_second: 3
    daily_limit: 10000
```

### Optional Configuration

```python
# API key for higher rate limits (optional)
config = {
    "api_key": "your-ncbi-api-key"
}

await connector.authenticate(config)
```

## Usage Examples

### Basic Search

```python
from connectors.pubmed.connector import PubMedConnector

async def search_example():
    connector = PubMedConnector()

    # Search for papers about cancer research
    results = await connector.search("cancer research", limit=10)

    print(f"Found {results['total_results']} results")
    for doc_id in results['document_ids']:
        print(f"- {doc_id}")

    await connector.close()
```

### Document Retrieval

```python
async def get_document_example():
    connector = PubMedConnector()

    # Get a specific document
    doc = await connector.get_by_id("12345678")

    print(f"Title: {doc['title']}")
    print(f"Authors: {[author['name'] for author in doc['authors']]}")
    print(f"Journal: {doc['journal']}")
    print(f"Publication Date: {doc['publication_date']}")
    print(f"DOI: {doc['doi']}")

    await connector.close()
```

### Advanced Search

```python
async def advanced_search_example():
    connector = PubMedConnector()

    # Search with filters
    query = "cancer[Title] AND 2023[Publication Date] AND review[Publication Type]"
    results = await connector.search(query, limit=20)

    print(f"Found {results['total_results']} review articles about cancer from 2023")

    await connector.close()
```

### MeSH Term Search

```python
async def mesh_search_example():
    connector = PubMedConnector()

    # Search using MeSH terms
    query = "Neoplasms[MeSH Terms] AND Therapy[MeSH Terms]"
    results = await connector.search(query, limit=15)

    print(f"Found {results['total_results']} papers about cancer therapy")

    await connector.close()
```

### Incremental Updates

```python
from datetime import datetime, timedelta

async def incremental_updates_example():
    connector = PubMedConnector()

    # Get papers published in the last 7 days
    since_date = datetime.now() - timedelta(days=7)
    results = await connector.get_updates(since_date)

    print(f"Found {len(results['document_ids'])} new papers")

    await connector.close()
```

## CLI Usage

### Search for Papers

```bash
# Search PubMed
.venv/bin/python -m obc_ingestion.cli debug test pubmed --query "machine learning" --limit 5

# Search with advanced filters
.venv/bin/python -m obc_ingestion.cli debug test pubmed --query "cancer[Title] AND 2023[Publication Date]" --limit 10

# Search using MeSH terms
.venv/bin/python -m obc_ingestion.cli debug test pubmed --query "Neoplasms[MeSH Terms]" --limit 5
```

### Get Specific Document

```bash
# Get a specific paper by PMID
.venv/bin/python -m obc_ingestion.cli debug test pubmed --id "12345678"
```

### With API Key

```bash
# Configure with API key for higher rate limits
.venv/bin/python -m obc_ingestion.cli debug test pubmed --query "cancer research" --api-key "your-ncbi-api-key"
```

## Data Model

### Document Structure

```python
{
    "id": "12345678",
    "title": "Machine Learning in Cancer Diagnosis",
    "abstract": "Abstract text...",  # May be None if not available
    "authors": [
        {
            "name": "John Smith",
            "affiliation": "Harvard Medical School",
            "position": "first"
        }
    ],
    "journal": "Nature Medicine",
    "publication_date": datetime(2023, 6, 15),
    "doi": "10.1038/s41591-023-02345-6",
    "pmid": "12345678",
    "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
    "source": "pubmed",
    "metadata": {
        "publication_type": "Journal Article",
        "language": "English",
        "mesh_terms": [
            "Machine Learning",
            "Neoplasms",
            "Diagnosis"
        ],
        "keywords": ["artificial intelligence", "cancer", "diagnosis"],
        "citation_count": 45,
        "pmc_id": "PMC1234567"
    }
}
```

### Search Result Structure

```python
{
    "query": "cancer research",
    "total_results": 150000,
    "document_ids": ["12345678", "87654321", "11223344"],
    "metadata": {
        "source": "pubmed",
        "page": 1,
        "per_page": 10,
        "results_returned": 3
    }
}
```

## Rate Limits

PubMed E-utilities has specific rate limits:
- **3 requests per second** (without API key)
- **10 requests per second** (with API key)
- **10,000 requests per day** (with API key)
- **No authentication required** (but API key recommended)

### Best Practices

1. **Include your API key** for higher rate limits
2. **Respect rate limits** - the connector automatically handles this
3. **Use pagination** for large result sets
4. **Cache results** when possible to reduce API calls
5. **Use MeSH terms** for more precise searches

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

- **429 Too Many Requests**: Rate limiting (automatically retried)
- **400 Bad Request**: Invalid query syntax
- **404 Not Found**: Document ID doesn't exist
- **Network errors**: Connection issues (automatically retried)

## Advanced Features

### MeSH Term Search

PubMed uses Medical Subject Headings (MeSH) for precise searching:

```python
# Search using MeSH terms
query = "Neoplasms[MeSH Terms] AND Therapy[MeSH Terms]"
results = await connector.search(query, limit=20)
```

### Publication Type Filtering

```python
# Search for specific publication types
query = "cancer[Title] AND review[Publication Type]"
results = await connector.search(query, limit=10)
```

### Date Range Filtering

```python
# Search within date ranges
query = "cancer[Title] AND 2023[Publication Date]"
results = await connector.search(query, limit=20)
```

### Journal Filtering

```python
# Search within specific journals
query = "cancer[Title] AND Nature[Journal]"
results = await connector.search(query, limit=15)
```

## Integration with OpenBioCure

The PubMed connector integrates seamlessly with the OpenBioCure ecosystem:

1. **Standard Interface**: Implements the `IConnector` interface
2. **Capability Discovery**: Declares its capabilities in the YAML config
3. **Error Handling**: Uses standard exception handling
4. **Rate Limiting**: Built-in rate limiting support
5. **Async Operations**: Full async/await support

## Troubleshooting

### Common Issues

1. **Empty search results**: Check your query syntax
2. **Rate limit errors**: Add your API key to the configuration
3. **Missing abstracts**: Not all papers have abstracts in PubMed
4. **Network timeouts**: Check your internet connection
5. **Invalid PMIDs**: Ensure PMIDs are valid numeric identifiers

### Debug Mode

Enable debug logging to see detailed API interactions:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your connector code here
```

### Query Syntax Help

PubMed uses specific query syntax:

- **Field tags**: `[Title]`, `[Author]`, `[Journal]`, `[MeSH Terms]`
- **Boolean operators**: `AND`, `OR`, `NOT`
- **Phrase searching**: Use quotes for exact phrases
- **Wildcards**: Use `*` for truncation

## Contributing

To contribute to the PubMed connector:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Testing

```bash
# Run connector tests
.venv/bin/python -m obc_ingestion.cli debug test pubmed --query "test query" --limit 5

# Run validation
.venv/bin/python tools/validate_connectors.py
```

## Resources

- [PubMed E-utilities Documentation](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- [PubMed Website](https://pubmed.ncbi.nlm.nih.gov/)
- [MeSH Database](https://www.ncbi.nlm.nih.gov/mesh/)
- [OpenBioCure Connector SDK](https://github.com/openbiocure/obc-connectors-core)
- [NCBI API Key Registration](https://www.ncbi.nlm.nih.gov/account/settings/)

## Examples

### Search and Process Results

```python
import asyncio
from connectors.pubmed.connector import PubMedConnector

async def process_papers():
    connector = PubMedConnector()

    # Search for papers
    results = await connector.search("machine learning in healthcare", limit=20)

    print(f"Found {results['total_results']} papers")

    # Process each paper
    for doc_id in results['document_ids'][:5]:  # Process first 5
        doc = await connector.get_by_id(doc_id)

        print(f"\nTitle: {doc['title']}")
        print(f"Journal: {doc.get('journal', 'N/A')}")
        print(f"Authors: {len(doc['authors'])}")
        print(f"MeSH Terms: {len(doc['metadata']['mesh_terms'])}")

        # Extract key MeSH terms
        mesh_terms = doc['metadata']['mesh_terms'][:3]  # Top 3 terms
        print(f"Key MeSH terms: {mesh_terms}")

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

This comprehensive documentation covers all aspects of the PubMed connector, from basic usage to advanced features and troubleshooting.
