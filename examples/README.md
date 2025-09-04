# Examples

This directory contains example scripts demonstrating how to use the OpenBioCure Connectors Core.

## Available Examples

### OpenAlex Connector Example

**File:** `openalex_example.py`

A comprehensive example demonstrating all features of the OpenAlex connector:

- **Basic Search** - Search for academic papers
- **Document Retrieval** - Get detailed information about specific papers
- **Author Search** - Find works by specific authors
- **Institution Search** - Find works from specific institutions
- **Incremental Updates** - Get recently published works
- **Configuration** - Set up authentication and rate limiting

#### Running the Example

```bash
# Make sure you're in the project root directory
cd /path/to/obc-connectors-core

# Activate virtual environment
source .venv/bin/activate

# Run the example
python examples/openalex_example.py
```

#### Expected Output

The example will demonstrate:
- Searching for papers about "machine learning"
- Retrieving detailed information about the first result
- Showing author information, concepts, and citation data
- Demonstrating various search capabilities

### PubMed Connector Example

**File:** `pubmed_example.py`

A comprehensive example demonstrating all features of the PubMed connector:

- **Basic Search** - Search for biomedical literature
- **Document Retrieval** - Get detailed information about specific papers
- **Advanced Search** - Use field tags and filters
- **MeSH Term Search** - Search using Medical Subject Headings
- **Journal Search** - Find works in specific journals
- **Incremental Updates** - Get recently published works
- **Configuration** - Set up API key for higher rate limits
- **Error Handling** - Demonstrate error handling patterns

#### Running the Example

```bash
# Make sure you're in the project root directory
cd /path/to/obc-connectors-core

# Activate virtual environment
source .venv/bin/activate

# Run the example
python examples/pubmed_example.py
```

#### Expected Output

The example will demonstrate:
- Searching for papers about "cancer research"
- Retrieving detailed information about the first result
- Showing author information, MeSH terms, and journal data
- Demonstrating advanced search capabilities
- Error handling for invalid queries and documents

## Creating Your Own Examples

### Basic Template

```python
#!/usr/bin/env python3
"""Your Connector Example"""

import asyncio
from connectors.your_connector.connector import YourConnector

async def main():
    connector = YourConnector()

    try:
        # Your code here
        results = await connector.search("your query", limit=10)
        print(f"Found {results['total_results']} results")

    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Best Practices

1. **Error Handling** - Always include try/finally blocks
2. **Resource Cleanup** - Close connectors properly
3. **Logging** - Use appropriate logging levels
4. **Documentation** - Include clear comments and docstrings
5. **Configuration** - Show how to configure connectors

## Contributing Examples

When adding new examples:

1. **Follow naming convention** - `{connector_name}_example.py`
2. **Include comprehensive examples** - Show multiple features
3. **Add documentation** - Update this README
4. **Test thoroughly** - Ensure examples work correctly
5. **Handle errors gracefully** - Show proper error handling

## Troubleshooting

### Common Issues

1. **Import errors** - Make sure virtual environment is activated
2. **Network errors** - Check internet connection and API availability
3. **Rate limiting** - Add email/API key configuration for better limits
4. **Authentication** - Ensure proper API keys are configured

### Getting Help

- Check the main [documentation](../docs/)
- Review connector-specific documentation
- Open an issue on GitHub
- Join community discussions
