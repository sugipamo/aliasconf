# AliasConf

**Powerful configuration management with alias support for Python**

[![PyPI version](https://badge.fury.io/py/aliasconf.svg)](https://badge.fury.io/py/aliasconf)
[![Python Versions](https://img.shields.io/pypi/pyversions/aliasconf.svg)](https://pypi.org/project/aliasconf/)
[![License](https://img.shields.io/pypi/l/aliasconf.svg)](https://github.com/yourusername/aliasconf/blob/main/LICENSE)
[![codecov](https://codecov.io/gh/yourusername/aliasconf/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/aliasconf)

## What is AliasConf?

AliasConf is a Python library that revolutionizes configuration management by introducing a powerful alias system. It allows you to access the same configuration value through multiple names, making it perfect for:

- **Configuration migrations** - Smoothly transition from old to new configuration schemas
- **Multi-team projects** - Different teams can use their preferred naming conventions
- **API compatibility** - Maintain backward compatibility while modernizing your configuration structure
- **Flexibility** - Access configuration values in the way that makes most sense for your context

## Key Features

### 🔄 Powerful Alias System
Access the same configuration value through multiple names:

```python
from aliasconf import ConfigManager

config = ConfigManager.from_dict({
    "server": {
        "aliases": ["backend", "api"],
        "host": "api.example.com",
        "port": 8080
    }
})

# All of these return the same value
assert config.get("server.host") == "api.example.com"
assert config.get("backend.host") == "api.example.com" 
assert config.get("api.host") == "api.example.com"
```

### 🎯 Type-Safe Access
Get configuration values with automatic type conversion and validation:

```python
# Specify expected type for automatic conversion
timeout = config.get("server.timeout", int)  # Returns int
enable_ssl = config.get("server.ssl", bool)  # Returns bool

# Type validation with helpful error messages
config.get("server.port", str)  # Raises ConfigValidationError
```

### 📝 Template Expansion
Use template strings with automatic variable resolution:

```python
config = ConfigManager.from_dict({
    "base_url": "https://api.example.com",
    "endpoints": {
        "users": "{base_url}/users",
        "posts": "{base_url}/posts"
    }
})

users_endpoint = config.get("endpoints.users")  
# Returns: "https://api.example.com/users"
```

### 🚀 Minimal Update Overhead
One of AliasConf's design goals is to make configuration updates as simple as possible:

```python
# Before: Update needed in multiple places
config['db']['host'] = 'newhost'
config['database']['host'] = 'newhost'
config['backend']['db']['host'] = 'newhost'

# After: Update once, accessible everywhere
config.set("db.host", "newhost")
# Automatically available through all aliases
```

## Quick Example

Here's a complete example showing AliasConf in action:

```python
from aliasconf import ConfigManager

# Load from file
config = ConfigManager.from_file("config.yaml")

# Or create from dictionary
config = ConfigManager.from_dict({
    "database": {
        "aliases": ["db", "datastore"],
        "connection": {
            "host": "localhost",
            "port": 5432,
            "timeout": 30
        }
    },
    "api": {
        "aliases": ["backend", "server"],
        "host": "0.0.0.0",
        "port": "{env.PORT|8000}",
        "debug": false
    }
})

# Access via primary key or any alias
assert config.get("database.connection.host") == "localhost"
assert config.get("db.connection.host") == "localhost"
assert config.get("datastore.connection.host") == "localhost"

# Type-safe access
port = config.get("db.connection.port", int)  # 5432
debug = config.get("api.debug", bool)  # False

# Check existence
if config.has("db.connection.ssl"):
    ssl_mode = config.get("db.connection.ssl")
```

## Why AliasConf?

### The Problem

Configuration management in large projects often faces these challenges:

1. **Naming Inconsistencies**: Different teams use different names for the same configuration
2. **Migration Difficulty**: Changing configuration structure breaks existing code
3. **Multiple Access Patterns**: Different parts of the codebase expect different structures
4. **Backward Compatibility**: Need to support old configuration formats

### The AliasConf Solution

AliasConf solves these problems by decoupling configuration access from structure:

- **One Value, Multiple Names**: Access configuration through any alias
- **Smooth Migrations**: Add new names while keeping old ones working
- **Team Flexibility**: Each team can use their preferred naming
- **Zero Breaking Changes**: Add aliases without touching existing code

## Installation

```bash
pip install aliasconf
```

## Next Steps

- 📖 Read the [Getting Started Guide](getting-started/quickstart.md)
- 🔍 Explore [Configuration Examples](examples/basic.md)
- 🏗️ Learn about [Advanced Features](guide/alias-system.md)
- 📚 Check the [API Reference](api/manager.md)

## Contributing

AliasConf is open source and welcomes contributions! Check out our [Contributing Guide](contributing/setup.md) to get started.

## License

AliasConf is released under the MIT License. See [LICENSE](https://github.com/yourusername/aliasconf/blob/main/LICENSE) for details.