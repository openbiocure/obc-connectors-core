# OpenBioCure Connectors Core Documentation

Welcome to the OpenBioCure Connectors Core documentation. This directory contains comprehensive guides and references for using and developing connectors.

## Documentation Structure

### Getting Started
- **[Quick Start Guide](quick-start.md)** - Get up and running in minutes
- **[Connector Development Guide](connector-development-guide.md)** - How to create new connectors

### Connector Documentation
- **[OpenAlex Connector](connectors/openalex.md)** - Complete guide to the OpenAlex connector

## Quick Navigation

### For Users
1. Start with the [Quick Start Guide](quick-start.md)
2. Explore available connectors in the [connectors/](connectors/) directory
3. Check the main [README](../README.md) for project overview

### For Developers
1. Read the [Connector Development Guide](connector-development-guide.md)
2. Study existing connector implementations:
   - [PubMed Connector](../connectors/pubmed/)
   - [OpenAlex Connector](../connectors/openalex/)
3. Review the [Connector SDK](../obc_connector_sdk/) source code

## Available Connectors

### PubMed Connector
- **Purpose**: Access to biomedical literature via NCBI E-utilities API
- **Features**: Search, document retrieval, metadata extraction
- **Documentation**: See [connectors/pubmed/](../connectors/pubmed/)

### OpenAlex Connector
- **Purpose**: Access to comprehensive scholarly data
- **Features**: Full-text search, author/institution search, citation networks
- **Documentation**: [OpenAlex Connector Guide](connectors/openalex.md)

## Development Resources

### Architecture
- **Connector SDK**: Core framework and utilities
- **Base Classes**: Common functionality for all connectors
- **Capabilities System**: Feature discovery and validation
- **Configuration**: YAML-based connector specifications

### Testing
- **Unit Tests**: Individual connector testing
- **Integration Tests**: End-to-end functionality
- **CLI Testing**: Command-line interface validation
- **Validation Tools**: Configuration and schema validation

### Code Quality
- **Linting**: Code style and quality checks
- **Formatting**: Automated code formatting
- **Type Checking**: Static type analysis
- **Documentation**: Comprehensive inline documentation

## Contributing

### Adding New Connectors
1. Follow the [Connector Development Guide](connector-development-guide.md)
2. Implement the `IConnector` interface
3. Create comprehensive tests
4. Add documentation
5. Submit a pull request

### Documentation Updates
1. Update relevant documentation files
2. Add examples and usage patterns
3. Ensure consistency with existing docs
4. Test all code examples

## Support

### Getting Help
1. **Documentation**: Check this directory first
2. **Examples**: Review existing connector implementations
3. **Issues**: Open a GitHub issue for bugs or questions
4. **Discussions**: Join community discussions

### Reporting Issues
When reporting issues, please include:
- Connector name and version
- Error messages and logs
- Steps to reproduce
- Environment details (Python version, OS, etc.)

## Resources

### External APIs
- [OpenAlex API Documentation](https://docs.openalex.org/)
- [PubMed E-utilities API](https://www.ncbi.nlm.nih.gov/books/NBK25501/)

### Related Projects
- [OpenBioCure CoreLib](https://github.com/openbiocure/corelib)
- [OpenBioCure Platform](https://github.com/openbiocure/platform)

### Community
- [GitHub Repository](https://github.com/openbiocure/obc-connectors-core)
- [Issue Tracker](https://github.com/openbiocure/obc-connectors-core/issues)
- [Discussions](https://github.com/openbiocure/obc-connectors-core/discussions)

---

*This documentation is maintained by the OpenBioCure community. Contributions and improvements are welcome!*
