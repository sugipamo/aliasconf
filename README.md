# AliasConf

🔧 **Configuration management with powerful alias support**

AliasConf is a Python library that provides flexible configuration management with a unique focus on **alias support**. It allows you to access the same configuration values through multiple different names, making your configurations more intuitive and migration-friendly.

## ✨ Key Features

- 🏷️ **Multiple Aliases**: Access the same configuration value through different names
- 🌳 **Tree Structure**: Hierarchical configuration with parent-child relationships  
- 🔍 **Smart Resolution**: BFS-based efficient configuration path resolution
- 📝 **Template Expansion**: Dynamic variable substitution with `{key}` syntax
- 🛡️ **Type Safety**: Type-safe configuration access with automatic conversion
- 📁 **Multiple Formats**: Support for YAML, JSON, and Python dictionaries
- ⚡ **High Performance**: Optimized with caching and efficient algorithms

## 🚀 Quick Start

### Installation

```bash
pip install aliasconf
```

### Basic Usage

```python
from aliasconf import ConfigManager

# Load from dictionary
config_dict = {
    "python": {
        "aliases": ["py", "python3"],  # Multiple names for the same config
        "timeout": 30,
        "command": "python {script}"
    },
    "database": {
        "host": "localhost",
        "port": 5432
    }
}

config = ConfigManager.from_dict(config_dict)

# Access same value through different aliases
timeout1 = config.get("python.timeout", int)   # 30
timeout2 = config.get("py.timeout", int)       # 30 (same value!)
timeout3 = config.get("python3.timeout", int)  # 30 (same value!)

# Type-safe access
port = config.get("database.port", int)        # Returns int: 5432
host = config.get("database.host", str)        # Returns str: "localhost"

# Template formatting
command = config.get_formatted("python.command", {"script": "test.py"})
print(command)  # "python test.py"
```

### Load from Files

```python
# Load from YAML file
config = ConfigManager.from_file("config.yaml")

# Load and merge multiple files
config = ConfigManager.from_files(
    "base_config.yaml",
    "environment_config.yaml", 
    "local_config.yaml"
)
```

## 📖 Configuration Examples

### YAML Configuration with Aliases

```yaml
# config.yaml
python:
  aliases: ["py", "python3"]
  timeout: 30
  command: "python {script}"
  
cpp:
  aliases: ["c++", "cxx"]  
  timeout: 60
  command: "g++ {source} -o {output}"

database:
  host: "localhost"
  port: 5432
  url: "postgresql://{host}:{port}/mydb"
```

### JSON Configuration

```json
{
  "python": {
    "aliases": ["py", "python3"],
    "timeout": 30,
    "command": "python {script}"
  },
  "settings": {
    "debug": true,
    "log_level": "INFO"
  }
}
```

## 🔧 Advanced Features

### Template Variable Expansion

```python
config_dict = {
    "app": {
        "name": "MyApp",
        "version": "1.0.0"
    },
    "messages": {
        "welcome": "Welcome to {name} v{version}!",
        "goodbye": "Thanks for using {name}!"
    }
}

config = ConfigManager.from_dict(config_dict)

# Template expansion with context
message = config.get_formatted("messages.welcome", {
    "name": config.get("app.name", str),
    "version": config.get("app.version", str)
})
print(message)  # "Welcome to MyApp v1.0.0!"
```

### Configuration Merging

```python
base_config = ConfigManager.from_dict({
    "app": {"name": "MyApp", "debug": False}
})

dev_config = ConfigManager.from_dict({
    "app": {"debug": True},
    "database": {"host": "localhost"}
})

# Merge configurations (dev_config takes precedence)
merged = base_config.merge(dev_config)
```

### Type Conversion

```python
# Automatic type conversion
timeout = config.get("python.timeout", int)        # int
debug = config.get("app.debug", bool)              # bool  
version = config.get("app.version", str)           # str
ratio = config.get("performance.ratio", float)     # float

# With defaults
max_workers = config.get("workers.max", int, 4)    # Default: 4
```

## 🆚 Why AliasConf?

### Comparison with Other Libraries

| Feature | AliasConf | Pydantic | OmegaConf | Dynaconf |
|---------|-----------|----------|-----------|----------|
| Multiple Aliases | ✅ **Native** | ❌ Limited | ❌ No | ⚠️ Manual |
| Type Safety | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Limited |
| Template Expansion | ✅ Advanced | ❌ No | ✅ Basic | ✅ Yes |
| File Merging | ✅ Yes | ❌ Manual | ✅ Yes | ✅ Yes |
| Learning Curve | 🟢 Easy | 🟡 Medium | 🟡 Medium | 🟡 Medium |

### The Alias Advantage

```python
# With AliasConf - One configuration, multiple access patterns
config = {
    "python": {
        "aliases": ["py", "python3", "python-lang"],
        "timeout": 30
    }
}

# All of these work and return the same value:
config.get("python.timeout", int)      # 30
config.get("py.timeout", int)          # 30  
config.get("python3.timeout", int)     # 30
config.get("python-lang.timeout", int) # 30

# Perfect for:
# - API backwards compatibility
# - Team migration from old naming conventions  
# - Supporting multiple naming styles
# - Gradual refactoring
```

## 🧪 Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/aliasconf --cov-report=html
```

## 📚 Documentation

- [Full Documentation](https://aliasconf.readthedocs.io/)
- [API Reference](https://aliasconf.readthedocs.io/en/latest/api/)
- [Examples](https://github.com/username/aliasconf/tree/main/examples)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the need for better configuration alias support
- Built with performance and usability in mind
- Designed for real-world configuration management challenges

---

⭐ **Star this repository if you find it useful!**