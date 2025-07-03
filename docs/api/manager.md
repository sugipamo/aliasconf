# ConfigManager API Reference

The `ConfigManager` class is the main interface for working with AliasConf configurations.

## Class: ConfigManager

::: aliasconf.ConfigManager
    options:
      show_source: true
      show_bases: false
      members:
        - __init__
        - from_dict
        - from_file
        - from_files
        - get
        - get_formatted
        - has
        - set
        - to_dict
        - clear_cache

## Examples

### Basic Usage

```python
from aliasconf import ConfigManager

# Create from dictionary
config = ConfigManager.from_dict({
    "app": {
        "name": "MyApp",
        "version": "1.0.0"
    }
})

# Access values
app_name = config.get("app.name")  # "MyApp"
```

### Using Aliases

```python
config = ConfigManager.from_dict({
    "database": {
        "aliases": ["db", "datastore"],
        "host": "localhost",
        "port": 5432
    }
})

# Access through any alias
host = config.get("db.host")  # "localhost"
host = config.get("datastore.host")  # "localhost"
```

### Type Conversion

```python
# Automatic type conversion
port = config.get("db.port", int)  # 5432 as integer
debug = config.get("app.debug", bool)  # True/False as boolean

# With default values
timeout = config.get("db.timeout", int, default=30)
```

### Template Expansion

```python
config = ConfigManager.from_dict({
    "base_url": "https://api.example.com",
    "endpoints": {
        "users": "{base_url}/users",
        "posts": "{base_url}/posts"
    }
})

# Automatic template expansion
users_url = config.get("endpoints.users")
# Returns: "https://api.example.com/users"

# With additional context
config_with_context = ConfigManager.from_dict({
    "greeting": "Hello {name}!"
})

personalized = config.get_formatted("greeting", {"name": "Alice"})
# Returns: "Hello Alice!"
```

### Loading from Files

```python
# Load from YAML
config = ConfigManager.from_file("config.yaml")

# Load from JSON
config = ConfigManager.from_file("config.json")

# Load and merge multiple files
config = ConfigManager.from_files([
    "base.yaml",
    "environment.yaml",
    "local.yaml"
])
```

### Error Handling

```python
from aliasconf import ConfigNotFoundError, ConfigValidationError

try:
    value = config.get("missing.key")
except ConfigNotFoundError:
    # Handle missing configuration
    pass

try:
    # This will fail if value cannot be converted to int
    port = config.get("app.name", int)
except ConfigValidationError:
    # Handle validation error
    pass
```

## Method Details

### `__init__(root_node: Optional[ConfigNode] = None)`

Initialize a new ConfigManager instance.

**Parameters:**
- `root_node`: Pre-built configuration tree root node (optional)

**Example:**
```python
# Usually you won't call this directly
# Use from_dict() or from_file() instead
config = ConfigManager()
```

### `from_dict(data: Dict[str, Any]) -> ConfigManager`

Create a ConfigManager from a dictionary.

**Parameters:**
- `data`: Configuration dictionary

**Returns:**
- New ConfigManager instance

**Raises:**
- `ConfigValidationError`: If data structure is invalid

### `from_file(file_path: Union[str, Path]) -> ConfigManager`

Load configuration from a file.

**Parameters:**
- `file_path`: Path to configuration file (YAML or JSON)

**Returns:**
- New ConfigManager instance

**Raises:**
- `AliasConfError`: If file cannot be read or parsed

### `get(path: str, return_type: Optional[Type[T]] = None, default: Optional[Any] = None) -> Any`

Get a configuration value by path.

**Parameters:**
- `path`: Dot-separated path to the value
- `return_type`: Expected type for automatic conversion (optional)
- `default`: Default value if path not found (optional)

**Returns:**
- Configuration value, optionally converted to specified type

**Raises:**
- `ConfigNotFoundError`: If path not found and no default provided
- `ConfigValidationError`: If type conversion fails

### `get_formatted(path: str, context: Optional[Dict[str, Any]] = None, default: Optional[str] = None) -> str`

Get a formatted string with template expansion.

**Parameters:**
- `path`: Dot-separated path to the template string
- `context`: Additional context for template expansion (optional)
- `default`: Default value if path not found (optional)

**Returns:**
- Formatted string with templates expanded

### `has(path: str) -> bool`

Check if a configuration path exists.

**Parameters:**
- `path`: Dot-separated path to check

**Returns:**
- True if path exists, False otherwise

### `set(path: str, value: Any) -> None`

Set a configuration value.

**Parameters:**
- `path`: Dot-separated path where to set the value
- `value`: Value to set

**Note:** This modifies the configuration in-memory only.

### `to_dict() -> Dict[str, Any]`

Convert configuration to a plain dictionary.

**Returns:**
- Dictionary representation of the configuration

**Note:** This returns the configuration without alias information.

### `clear_cache() -> None`

Clear the internal resolution cache.

**Note:** The cache is automatically managed, but you can clear it manually if needed for memory optimization.