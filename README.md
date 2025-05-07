# HerpAI-Ingestion

A biomedical document ingestion system that processes and stores documents with their metadata, authors, entity mentions, and citations.

## Project Structure

The project uses SQLAlchemy for database models with the following entities:
- `Document`: Represents biomedical documents with metadata
- `Author`: Manages document authorship
- `EntityMention`: Tracks entity mentions within documents
- `Citation`: Handles document citations and references

## Dependencies

- Local Dependencies:
  - `openbiocure_corelib`: Local package from HerpAI-Lib repository
  - Location: `~/develop/HerpAI-Lib`

- Package Dependencies (from setup.py):
  - `click`
  - `dynaconf`
  - `aiohttp`

## Development Setup

1. IDE Configuration
   - Created `pyrightconfig.json` for local package resolution:
   ```json
   {
       "extraPaths": [
           "/Users/mohammad_shehab/develop/HerpAI-Lib"
       ]
   }
   ```

## What's Missing

1. Database Configuration
   - Connection settings
   - Migration scripts
   - Initial schema creation

2. Documentation
   - API documentation
   - Entity relationship diagrams
   - Usage examples

3. Core Functionality
   - Document ingestion pipeline
   - Entity extraction process
   - Citation parsing logic
   - Author matching/deduplication

4. Testing
   - Unit tests
   - Integration tests
   - Test data fixtures

5. Deployment
   - Environment configuration
   - Deployment instructions
   - Production setup guide

6. CI/CD
   - Build pipeline
   - Test automation
   - Deployment automation

## Version
Current version: 0.1.0 