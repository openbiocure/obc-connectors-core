# Comprehensive Test Suite for OpenBioCure Connectors Core

## 🎯 Overview

This document outlines the comprehensive test suite designed to ensure code quality and prevent regressions when adding new connectors to the OpenBioCure Connectors Core project.

## 📊 Test Suite Statistics

- **Total Test Files**: 8
- **Total Test Cases**: 42 (Unit + Integration)
- **Test Categories**: 3 (Unit, Integration, Connector)
- **Coverage Target**: 80% minimum
- **Test Execution Time**: ~4 seconds (unit + integration)

## 🏗️ Test Architecture

### 1. **Unit Tests** (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Files**: 3
- **Test Cases**: 29
- **Coverage**: Core SDK components
- **Speed**: Fast (< 1 second per test)

#### Test Files:
- `test_models.py` - Data model tests (Author, Document)
- `test_connector_capabilities.py` - Capability system tests
- `test_rate_limiter.py` - Rate limiting utility tests

### 2. **Integration Tests** (`tests/integration/`)
- **Purpose**: Test component interactions
- **Files**: 1
- **Test Cases**: 13
- **Coverage**: Connector loader and system integration
- **Speed**: Medium (1-10 seconds per test)

#### Test Files:
- `test_connector_loader.py` - Connector loading and management tests

### 3. **Connector Tests** (`tests/connectors/`)
- **Purpose**: Test specific connector implementations
- **Files**: 2
- **Test Cases**: Variable (depends on connector)
- **Coverage**: End-to-end connector functionality
- **Speed**: Variable (1-60 seconds per test)

#### Test Files:
- `test_connector_base.py` - Base test class for all connectors
- `test_pubmed_connector.py` - PubMed connector specific tests
- `test_pubmed_connector_simple.py` - Simplified PubMed tests

## 🧪 Test Categories & Markers

### Pytest Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.connector` - Connector-specific tests
- `@pytest.mark.slow` - Tests that take > 10 seconds
- `@pytest.mark.network` - Tests requiring network access
- `@pytest.mark.mock` - Tests using mocking
- `@pytest.mark.regression` - Regression prevention tests
- `@pytest.mark.smoke` - Basic functionality smoke tests

### Test Execution Strategies
- **Fast Tests**: Unit + Integration (no network)
- **Full Tests**: All tests including network
- **Smoke Tests**: Basic functionality verification
- **Regression Tests**: Prevent breaking changes

## 🛠️ Test Infrastructure

### Configuration Files
- `pytest.ini` - Main pytest configuration
- `conftest.py` - Shared fixtures and configuration
- `.github/workflows/test.yml` - CI/CD pipeline

### Test Runner
- `tests/test_runner.py` - Custom test runner script
- Support for different test types and markers
- Coverage reporting and linting integration

### Fixtures & Utilities
- Mock data generators
- HTTP client mocking
- Connector configuration fixtures
- Error scenario testing

## 📈 Coverage & Quality

### Coverage Requirements
- **Minimum Coverage**: 80%
- **Critical Components**: 90%+
- **New Code**: 90%+
- **Exclusions**: Generated code, test files

### Quality Gates
- All unit tests must pass
- Integration tests must pass
- Code coverage must meet minimum requirements
- Linting and formatting must pass
- No critical security issues

## 🚀 Running Tests

### Basic Commands
```bash
# Run all tests
pytest

# Run specific categories
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only
pytest tests/connectors/              # Connector tests only

# Run with markers
pytest -m unit                       # Unit tests only
pytest -m "not network"              # Exclude network tests
pytest -m smoke                      # Smoke tests only
```

### Using Test Runner
```bash
# Run all tests with coverage
python tests/test_runner.py

# Run specific test types
python tests/test_runner.py --type unit
python tests/test_runner.py --type integration
python tests/test_runner.py --type connectors

# Run with network tests
python tests/test_runner.py --network

# Run all checks (tests + linting + formatting)
python tests/test_runner.py --all-checks
```

### Makefile Commands
```bash
make test                    # Run all tests
make test-unit              # Run unit tests
make test-integration       # Run integration tests
make test-connectors        # Run connector tests
make test-smoke             # Run smoke tests
make test-regression        # Run regression tests
make test-no-network        # Run tests without network
make coverage               # Run with coverage report
make lint                   # Run linting
make format                 # Run code formatting
```

## 🔧 CI/CD Pipeline

### GitHub Actions Workflow
- **Matrix Testing**: Python 3.9, 3.10, 3.11
- **Code Quality**: Linting, formatting, type checking
- **Test Execution**: Unit, integration, connector tests
- **Coverage Reporting**: Codecov integration
- **Regression Testing**: Full test suite on main branch

### Pre-commit Hooks (Recommended)
- Code formatting (black, isort)
- Linting (flake8, mypy)
- Test execution
- Security scanning

## 📝 Writing Tests

### For New Connectors
1. Create connector test file: `tests/connectors/test_{connector_name}_connector.py`
2. Inherit from `ConnectorTestBase` for standard tests
3. Add connector-specific tests
4. Include both mocked and real API tests
5. Test error scenarios and edge cases

### For New SDK Components
1. Create unit test file: `tests/unit/test_{component_name}.py`
2. Test all public methods and properties
3. Test error conditions and edge cases
4. Use appropriate fixtures and mocks
5. Maintain high test coverage

## 🎯 Test Strategy for 30 New Connectors

### Phase 1: Foundation (Completed)
- ✅ Unit tests for core SDK components
- ✅ Integration tests for connector loader
- ✅ Base test framework for connectors
- ✅ CI/CD pipeline setup

### Phase 2: Connector Testing (In Progress)
- 🔄 Create connector-specific test templates
- 🔄 Implement automated connector validation
- 🔄 Add connector capability testing
- 🔄 Create connector performance benchmarks

### Phase 3: Regression Prevention
- 📋 Implement regression test suite
- 📋 Add connector compatibility testing
- 📋 Create connector upgrade testing
- 📋 Add performance regression detection

### Phase 4: Advanced Testing
- 📋 Add load testing for connectors
- 📋 Implement chaos engineering tests
- 📋 Add security testing for connectors
- 📋 Create connector monitoring tests

## 🚨 Current Status & Next Steps

### ✅ Completed
- Comprehensive unit test suite (29 tests)
- Integration test suite (13 tests)
- Test infrastructure and configuration
- CI/CD pipeline setup
- Test documentation and guidelines

### 🔄 In Progress
- Connector-specific test implementation
- Test coverage optimization
- Performance testing setup

### 📋 Next Steps
1. **Fix Connector Tests**: Resolve aiohttp event loop issues in connector tests
2. **Add More Connectors**: Create tests for OpenAlex and other connectors
3. **Enhance Coverage**: Increase test coverage to 90%+
4. **Performance Testing**: Add load and performance tests
5. **Documentation**: Create connector testing guidelines

## 📚 Resources

- [Test Suite README](tests/README.md) - Detailed testing documentation
- [Pytest Documentation](https://docs.pytest.org/) - Testing framework docs
- [GitHub Actions](.github/workflows/test.yml) - CI/CD configuration
- [Makefile](Makefile) - Test commands and automation

## 🤝 Contributing

When adding new tests:
1. Follow existing patterns and naming conventions
2. Add appropriate pytest markers
3. Update documentation as needed
4. Ensure CI pipeline passes
5. Maintain coverage requirements

For questions or issues, please refer to the main project documentation or create an issue.

---

**Last Updated**: September 6, 2025  
**Test Suite Version**: 1.0.0  
**Maintainer**: OpenBioCure Team
