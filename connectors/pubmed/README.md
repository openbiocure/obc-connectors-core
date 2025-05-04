# PubMed YAML-Driven Connector

This connector uses a YAML-driven approach to interact with the PubMed/NCBI E-utilities API. Instead of implementing API interactions in code, all functionality is defined through the `connector.yaml` configuration file.

## How It Works

The connector uses two files:
- `connector.py`: A minimal class that inherits from `BaseConnector`
- `connector.yaml`: The main configuration file that defines all connector behavior

### YAML Configuration Structure

```yaml
name: pubmed                 # Connector identifier
display_name: String        # Human-readable name
description: String        # Connector description
version: String           # Version number

capabilities:             # What the connector can do
  SUPPORTS_FULLTEXT: boolean
  SUPPORTS_ADVANCED_SEARCH: boolean
  # ... other capabilities

api:
  base_url: String       # Base API URL with environment variable support
  
  rate_limit:           # API rate limiting configuration
    requests_per_second: number
    with_api_key: number
    
  default_params:       # Parameters added to all requests
    param1: value
    param2: "{template}"  # Templates use {name} syntax
    
  endpoints:            # API endpoint definitions
    endpoint_name:      # e.g., search, get_document
      path: String     # Endpoint path
      method: GET/POST # HTTP method
      params:          # Request parameters
        param: value   # Static value
        param: "{template}"  # Dynamic value
      response:        # Response handling
        mapping:       # Maps API response to structured data
          field: path.to.value
          field:
            path: xpath.or.jsonpath
            transform:
              type: date|integer|text|concat
              # Transform-specific config
```

### Key Features

1. **Environment Variables**
   ```yaml
   base_url: ${HERPAI_PUBMED_API_URL|default_value}
   ```
   - Use `${VAR_NAME|default}` syntax
   - Supports fallback values

2. **Parameter Templates**
   ```yaml
   params:
     term: "{query}"    # Replaced with actual query
     limit: "{limit|100}"  # With default value
   ```

3. **Response Mapping**
   ```yaml
   mapping:
     title:            # Target field
       path: .//ArticleTitle   # XPath for XML
       default: Untitled      # Default if not found
     
     authors:          # List of objects
       path: .//Author
       list: true      # Indicates multiple items
       mapping:        # Sub-fields for each item
         name:
           transform:
             type: concat
             fields: [LastName, ForeName]
   ```

4. **Data Transformations**
   ```yaml
   transform:
     type: date        # Date transformation
     year: .//Year     # Source fields
     month: .//Month
     day: .//Day
     month_names:      # Custom mappings
       Jan: 1
       Feb: 2
   ```

5. **Pagination Support**
   ```yaml
   pagination:
     type: batch
     size: "{batch_size|100}"
     iterator:
       method: get_document
       for_each: document_ids
   ```

6. **Error Handling**
   ```yaml
   error_handling:
     retry:
       max_attempts: 3
       delay_seconds: 1
     error_mappings:
       429: RateLimitExceeded
   ```

### Example: Search Implementation

The search functionality:
```yaml
search:
  path: esearch.fcgi
  method: GET
  params:
    term: "{query}"
    retmode: json
  response:
    mapping:
      total_results:
        path: esearchresult.count
        transform:
          type: integer
      document_ids: esearchresult.idlist
```

This configuration:
1. Calls `esearch.fcgi` endpoint
2. Sends the search query as `term`
3. Expects JSON response
4. Extracts and transforms the results

### Example: Document Retrieval

Getting a specific document:
```yaml
get_document:
  path: efetch.fcgi
  method: GET
  params:
    id: "{id}"
    retmode: xml
  response:
    mapping:
      title:
        path: .//ArticleTitle
      authors:
        path: .//Author
        list: true
        mapping:
          name:
            transform:
              type: concat
              fields: [LastName, ForeName]
```

This configuration:
1. Calls `efetch.fcgi` endpoint
2. Retrieves XML document data
3. Extracts title and authors
4. Formats author names by concatenating fields

## Benefits

1. **Declarative**: Define what you want, not how to get it
2. **Maintainable**: Easy to update API changes
3. **Readable**: Clear structure and purpose
4. **Reusable**: Common patterns across connectors
5. **Testable**: Configuration can be validated

## Environment Variables

- `HERPAI_PUBMED_API_URL`: Base API URL
- `HERPAI_PUBMED_API_KEY`: Optional API key
- `HERPAI_PUBMED_RATE_LIMIT`: Requests per second
- `HERPAI_PUBMED_MAX_RETRIES`: Maximum retry attempts 