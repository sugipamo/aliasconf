# Changelog

All notable changes to AliasConf will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial development version

## [0.1.0] - 2024-07-03

### Added
- Core ConfigNode implementation with alias support
- ConfigManager for high-level configuration management
- Support for multiple aliases per configuration value
- BFS-based configuration path resolution
- Template string formatting with variable expansion
- Type-safe configuration access with automatic conversion
- Support for YAML and JSON configuration files
- Configuration merging capabilities
- Comprehensive error handling with custom exceptions
- Caching for improved performance
- Utility functions for path normalization and validation
- Full test suite with pytest
- Documentation and examples
- MIT license

### Features
- **Multiple Aliases**: Access same values through different names
- **Tree Structure**: Hierarchical configuration with parent-child relationships
- **Smart Resolution**: Efficient BFS-based path resolution algorithm
- **Template Expansion**: Dynamic variable substitution with {key} syntax
- **Type Safety**: Automatic type conversion with validation
- **Multiple Formats**: YAML, JSON, and Python dictionary support
- **Configuration Merging**: Combine multiple configuration sources
- **Performance**: Optimized with caching and efficient algorithms

### Technical Details
- Python 3.8+ support
- Zero required dependencies for core functionality
- Optional dependencies: PyYAML for YAML support
- Comprehensive type hints throughout
- 100% test coverage target
- Modern Python packaging with pyproject.toml
- Code quality tools: black, isort, mypy, ruff

[Unreleased]: https://github.com/username/aliasconf/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/username/aliasconf/releases/tag/v0.1.0