# Test Suite for OpenBioCure Connectors Core

This directory contains a comprehensive test suite designed to ensure code quality and prevent regressions when adding new connectors.

## Test Structure

```
tests/
├── conftest.py                    # Pytest configuration and shared fixtures
├── test_runner.py                 # Custom test runner script
├── unit/                          # Unit tests for individual components
│   ├── test_models.py            # Data model tests
│   ├── test_connector_capabilities.py  # Capability system tests
│   └── test_rate_limiter.py      # Rate limiter tests
├── integration/                   # Integration tests
│   └── test_connector_loader.py  # Connector loader tests
├── connectors/                    # Connector-specific tests
│   ├── test_connector_base.py    # Base test class for connectors
│   └── test_pubmed_connector.py  # PubMed connector tests
└── fixtures/                      # Test fixtures and mock data
```

## Test Categories

### 1. Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Functions, classes, and methods
- **Dependencies**: Minimal, mostly mocked
- **Speed**: Fast (< 1 second per test)

### 2. Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions
- **Scope**: Multiple components working together
- **Dependencies**: Some real dependencies, mocked external services
- **Speed**: Medium (1-10 seconds per test)

### 3. Connector Tests (`tests/connectors/`)
- **Purpose**: Test specific connector implementations
- **Scope**: End-to-end connector functionality
- **Dependencies**: Real APIs (with network tests)
- **Speed**: Variable (1-60 seconds per test)

## Test Markers

Pytest markers help categorize and control test execution:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.connector` - Connector-specific tests
- `@pytest.mark.slow` - Tests that take > 10 seconds
- `@pytest.mark.network` - Tests requiring network access
- `@pytest.mark.mock` - Tests using mocking
- `@pytest.mark.regression` - Regression prevention tests
- `@pytest.mark.smoke` - Basic functionality smoke tests

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only
pytest tests/connectors/              # Connector tests only

# Run with markers
pytest -m unit                       # Unit tests only
pytest -m "not network"              # Exclude network tests
pytest -m smoke                      # Smoke tests only
```

### Using the Test Runner

```bash
# Run all tests with coverage
python tests/test_runner.py

# Run specific test types
python tests/test_runner.py --type unit
python tests/test_runner.py --type integration
python tests/test_runner.py --type connectors

# Run connector-specific tests
python tests/test_runner.py --connector pubmed
python tests/test_runner.py --connector openalex

# Run with network tests
python tests/test_runner.py --network

# Run all checks (tests + linting + formatting)
python tests/test_runner.py --all-checks
```

### Makefile Commands

```bash
# Run all tests
make test

# Run unit tests
make test-unit

# Run integration tests
make test-integration

# Run connector tests
make test-connectors

# Run with coverage
make coverage

# Run linting
make lint

# Run formatting
make format
```

## Test Configuration

### pytest.ini
Main pytest configuration with:
- Test discovery patterns
- Coverage settings
- Marker definitions
- Output formatting

### conftest.py
Shared fixtures and configuration:
- `mock_connector` - Mock connector for testing
- `sample_document` - Sample document data
- `sample_search_result` - Sample search results
- `connector_test_data` - Test data for connectors
- `error_scenarios` - Common error cases

## Writing Tests

### For New Connectors

1. **Create connector test file**:
   ```python
   # tests/connectors/test_your_connector.py
   from tests.connectors.test_connector_base import ConnectorTestBase

   class TestYourConnector(ConnectorTestBase):
       def get_connector_class(self):
           from connectors.your_connector.connector import YourConnector
           return YourConnector

       def get_connector_name(self):
           return "your_connector"

       def get_valid_queries(self):
           return ["test query 1", "test query 2"]

       def get_valid_doc_ids(self):
           return ["doc1", "doc2"]

       def get_expected_capabilities(self):
           return {
               "supports_document_content": True,
               "supports_json_content": False,
               # ... other capabilities
           }
   ```

2. **Add connector-specific tests**:
   ```python
   @pytest.mark.asyncio
   async def test_your_connector_specific_feature(self):
       """Test connector-specific functionality."""
       connector = self.create_connector()
       # Your test logic here
   ```

### For New SDK Components

1. **Create unit test file**:
   ```python
   # tests/unit/test_your_component.py
   import pytest
   from obc_connector_sdk.your_component import YourComponent

   class TestYourComponent:
       def test_basic_functionality(self):
           """Test basic functionality."""
           component = YourComponent()
           assert component is not None
   ```

2. **Add integration tests if needed**:
   ```python
   # tests/integration/test_your_component_integration.py
   import pytest

   class TestYourComponentIntegration:
       @pytest.mark.asyncio
       async def test_component_interaction(self):
           """Test component interaction."""
           # Integration test logic
   ```

## Test Data and Fixtures

### Mock Data
- Use `conftest.py` fixtures for common test data
- Create connector-specific fixtures as needed
- Use realistic but minimal test data

### Network Tests
- Mark network tests with `@pytest.mark.network`
- Use real APIs sparingly
- Implement proper error handling
- Consider rate limiting

### Error Testing
- Test all error scenarios
- Use `pytest.raises()` for expected exceptions
- Test edge cases and boundary conditions

## Continuous Integration

### GitHub Actions
The `.github/workflows/test.yml` file defines CI pipeline:

1. **Matrix Testing**: Python 3.9, 3.10, 3.11
2. **Code Quality**: Linting, formatting, type checking
3. **Test Execution**: Unit, integration, connector tests
4. **Coverage Reporting**: Codecov integration
5. **Regression Testing**: Full test suite on main branch

### Pre-commit Hooks
Configure pre-commit hooks for:
- Code formatting (black, isort)
- Linting (flake8, mypy)
- Test execution
- Security scanning

## Coverage Requirements

- **Minimum Coverage**: 80%
- **Critical Components**: 90%+
- **New Code**: 90%+
- **Exclusions**: Generated code, test files

## Best Practices

### Test Naming
- Use descriptive test names
- Follow pattern: `test_<functionality>_<scenario>`
- Group related tests in classes

### Test Organization
- One test file per module/component
- Group tests by functionality
- Use fixtures for common setup

### Assertions
- Use specific assertions
- Test both positive and negative cases
- Verify error conditions

### Performance
- Keep unit tests fast (< 1 second)
- Use mocking for slow operations
- Mark slow tests appropriately

### Maintenance
- Update tests when changing code
- Remove obsolete tests
- Keep test data current

## Troubleshooting

### Common Issues

1. **Import Errors**:
   - Check Python path
   - Verify package installation
   - Use relative imports

2. **Network Test Failures**:
   - Check internet connection
   - Verify API availability
   - Check rate limits

3. **Mock Issues**:
   - Verify mock setup
   - Check mock call arguments
   - Use proper async mocking

4. **Coverage Issues**:
   - Check excluded files
   - Verify test execution
   - Review coverage configuration

### Debug Commands

```bash
# Run specific test with verbose output
pytest tests/unit/test_models.py::TestDocument::test_document_creation -v -s

# Run with debugging
pytest --pdb tests/connectors/test_pubmed_connector.py

# Show test collection
pytest --collect-only

# Run with coverage details
pytest --cov=obc_connector_sdk --cov-report=html
```

## Contributing

When adding new tests:

1. Follow existing patterns
2. Add appropriate markers
3. Update documentation
4. Ensure CI passes
5. Maintain coverage requirements

For questions or issues, please refer to the main project documentation or create an issue.
