# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-07-04

### Fixed
- Environment variable loading with alias resolution (`use_aliases=True` parameter)
- Test suite security warnings for hardcoded test credentials
- Improved test coverage to 85.37%

### Changed
- Enhanced `ConfigManager.load_from_env()` to properly resolve aliases when `use_aliases=True`
- Added helper methods for alias mapping collection and dictionary flattening
- Test credentials now use explicit `test_` prefix to indicate they are for testing only

## [0.1.1] - 2025-07-04

### Added
- Initial release of AliasConf
- Core configuration management functionality
- Powerful alias system for configuration keys
- Type-safe configuration access
- Template expansion support
- Performance optimizations with LRU cache
- Comprehensive test suite (84.81% coverage)
- Full CI/CD pipeline with multi-OS support

### Features
- **Alias System**: Access configuration values through multiple names
- **Nested Configuration**: Support for deeply nested configuration structures
- **Type Safety**: Automatic type conversion and validation
- **File Format Support**: YAML configuration file loading
- **Configuration Merging**: Merge multiple configuration sources
- **Template Variables**: Dynamic value expansion with `{path}` syntax
- **Performance**: Optimized with caching for large configurations
- **Developer Experience**: Full type hints and IDE autocompletion support

### Technical Details
- Supports Python 3.9, 3.10, 3.11, and 3.12
- Cross-platform compatibility (Windows, macOS, Linux)
- Zero runtime dependencies (PyYAML only for YAML support)
- Extensive test coverage across all modules
- GitHub Actions CI/CD with automated testing and deployment

[0.1.2]: https://github.com/sugipamo/aliasconf/releases/tag/v0.1.2
[0.1.1]: https://github.com/sugipamo/aliasconf/releases/tag/v0.1.1