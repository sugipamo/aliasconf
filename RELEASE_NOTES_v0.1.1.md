# AliasConf v0.1.1 - Initial PyPI Release

We're excited to announce the first public release of AliasConf - a powerful configuration management library with unique alias functionality for Python applications.

## 🎉 Features

- 🔗 **Powerful Alias System**: Access configuration values with multiple names
- 🌳 **Hierarchical Configuration**: Organize settings in nested structures  
- 🔒 **Type Safety**: Built-in type checking and validation
- 📝 **Multiple Formats**: Support for YAML and JSON
- 🚀 **High Performance**: Optimized with caching and indexing
- 🔧 **Zero Dependencies**: No external runtime dependencies

## 📦 Installation

```bash
pip install aliasconf
```

## 🚀 Quick Start

```python
from aliasconf import ConfigManager

# Create and load configuration
config = ConfigManager()
config.load({
    "database": {
        "host": "localhost",
        "port": 5432
    }
})

# Set up aliases
config.set_alias("db_host", "database.host")
config.set_alias("db_port", "database.port")

# Access via alias
print(config.get("db_host"))  # "localhost"
print(config.get("db_port"))  # 5432
```

## 📊 Project Status

- ✅ Core functionality complete
- ✅ 85% test coverage
- ✅ Performance optimized (10x faster than initial implementation)
- ✅ CI/CD pipeline established
- ✅ Cross-platform support (Linux, macOS, Windows)

## 📚 Documentation

- GitHub: https://github.com/sugipamo/aliasconf
- Issues: https://github.com/sugipamo/aliasconf/issues

## 🔮 What's Next

- Environment variable support
- TOML format support  
- CLI tools
- Framework integrations (FastAPI, Flask, Django)

## 🙏 Thank You

Thank you for trying AliasConf! We welcome your feedback and contributions.

---

*This is the initial release of AliasConf. Please report any issues on our GitHub repository.*