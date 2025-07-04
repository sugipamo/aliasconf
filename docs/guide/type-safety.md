# Type Safety Guide

AliasConf provides robust type safety features to ensure your configuration values are correctly typed and validated. This guide covers type conversion, validation, and best practices.

## Type Conversion

### Basic Type Conversion

Specify the expected type when retrieving configuration values:

```python
from aliasconf import ConfigManager

config = ConfigManager.from_dict({
    "server": {
        "port": "8080",
        "timeout": "30.5",
        "debug": "true",
        "max_connections": "100"
    }
})

# Automatic type conversion
port = config.get("server.port", int)              # 8080 (int)
timeout = config.get("server.timeout", float)      # 30.5 (float)
debug = config.get("server.debug", bool)           # True (bool)
connections = config.get("server.max_connections", int)  # 100 (int)
```

### Supported Type Conversions

AliasConf supports conversion to common Python types:

```python
config = ConfigManager.from_dict({
    "values": {
        "string": "hello",
        "integer": "42",
        "float": "3.14",
        "boolean_true": "true",
        "boolean_false": "false",
        "list": "a,b,c",
        "none": "null"
    }
})

# String (no conversion needed)
s = config.get("values.string", str)  # "hello"

# Numeric types
i = config.get("values.integer", int)  # 42
f = config.get("values.float", float)  # 3.14

# Boolean conversion
b1 = config.get("values.boolean_true", bool)   # True
b2 = config.get("values.boolean_false", bool)  # False

# List conversion (if supported)
lst = config.get("values.list", list)  # ["a", "b", "c"]
```

### Boolean Conversion Rules

Boolean conversion follows Python-like semantics:

```python
config = ConfigManager.from_dict({
    "flags": {
        "explicit_true": True,
        "explicit_false": False,
        "string_true": "true",
        "string_false": "false",
        "string_yes": "yes",
        "string_no": "no",
        "string_1": "1",
        "string_0": "0",
        "empty_string": "",
        "none_value": None
    }
})

# True values
assert config.get("flags.explicit_true", bool) is True
assert config.get("flags.string_true", bool) is True
assert config.get("flags.string_yes", bool) is True
assert config.get("flags.string_1", bool) is True

# False values
assert config.get("flags.explicit_false", bool) is False
assert config.get("flags.string_false", bool) is False
assert config.get("flags.string_no", bool) is False
assert config.get("flags.string_0", bool) is False
assert config.get("flags.empty_string", bool) is False
```

## Type Validation

### Validation Errors

Type conversion failures raise clear errors:

```python
from aliasconf import ConfigValidationError

config = ConfigManager.from_dict({
    "server": {
        "port": "not-a-number",
        "timeout": "30 seconds"
    }
})

try:
    port = config.get("server.port", int)
except ConfigValidationError as e:
    print(f"Validation error: {e}")
    # Handle error or use default
    port = 8080
```

### Custom Validators

You can implement custom validation logic:

```python
def validate_port(value):
    """Validate port is in valid range"""
    port = int(value)
    if not 1 <= port <= 65535:
        raise ConfigValidationError(f"Port {port} out of range (1-65535)")
    return port

def validate_email(value):
    """Basic email validation"""
    if "@" not in str(value):
        raise ConfigValidationError(f"Invalid email: {value}")
    return str(value)

# Usage
config = ConfigManager.from_dict({
    "server": {"port": "8080"},
    "admin": {"email": "admin@example.com"}
})

# Apply custom validators
port = validate_port(config.get("server.port"))
email = validate_email(config.get("admin.email"))
```

## Type-Safe Patterns

### Configuration Classes

Use dataclasses or Pydantic for type-safe configuration:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str
    timeout: Optional[float] = 30.0

@dataclass
class ServerConfig:
    host: str
    port: int
    debug: bool = False

# Load configuration with type safety
config = ConfigManager.from_dict({
    "database": {
        "host": "localhost",
        "port": "5432",
        "username": "user",
        "password": "secret",
        "database": "myapp"
    },
    "server": {
        "host": "0.0.0.0",
        "port": "8080",
        "debug": "true"
    }
})

# Create typed configuration objects
db_config = DatabaseConfig(
    host=config.get("database.host"),
    port=config.get("database.port", int),
    username=config.get("database.username"),
    password=config.get("database.password"),
    database=config.get("database.database"),
    timeout=config.get("database.timeout", float, default=30.0)
)

server_config = ServerConfig(
    host=config.get("server.host"),
    port=config.get("server.port", int),
    debug=config.get("server.debug", bool)
)
```

### Type Hints with Defaults

Use type hints and defaults for safety:

```python
from typing import List, Dict, Optional

config = ConfigManager.from_dict({
    "app": {
        "name": "MyApp",
        "features": ["feature1", "feature2"],
        "settings": {
            "timeout": 30,
            "retries": 3
        }
    }
})

# Type-safe access with defaults
app_name: str = config.get("app.name", str, default="DefaultApp")
version: str = config.get("app.version", str, default="1.0.0")
features: List[str] = config.get("app.features", list, default=[])
timeout: int = config.get("app.settings.timeout", int, default=30)
max_workers: Optional[int] = config.get("app.max_workers", int, default=None)
```

### Enum Types

Use enums for constrained values:

```python
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

config = ConfigManager.from_dict({
    "app": {
        "environment": "production",
        "log_level": "INFO"
    }
})

# Convert to enum types
env = Environment(config.get("app.environment"))
log_level = LogLevel(config.get("app.log_level"))

# Use in application
if env == Environment.PRODUCTION:
    # Production-specific settings
    pass
```

## Complex Type Handling

### Nested Structures

Handle complex nested types:

```python
from typing import List, Dict

config = ConfigManager.from_dict({
    "services": {
        "databases": [
            {"name": "primary", "host": "db1.example.com", "port": 5432},
            {"name": "replica", "host": "db2.example.com", "port": 5432}
        ],
        "caches": {
            "redis": {"host": "redis.example.com", "port": 6379},
            "memcached": {"host": "memcached.example.com", "port": 11211}
        }
    }
})

# Access complex structures
databases: List[Dict] = config.get("services.databases", list)
for db in databases:
    print(f"Database {db['name']} at {db['host']}:{db['port']}")

# Access nested dictionaries
redis_config: Dict = config.get("services.caches.redis", dict)
redis_host = redis_config["host"]
redis_port = int(redis_config["port"])
```

### JSON Schema Validation

Validate configuration against JSON schema:

```python
import json
from jsonschema import validate, ValidationError

# Define schema
schema = {
    "type": "object",
    "properties": {
        "server": {
            "type": "object",
            "properties": {
                "host": {"type": "string"},
                "port": {"type": "integer", "minimum": 1, "maximum": 65535}
            },
            "required": ["host", "port"]
        }
    }
}

config_dict = {
    "server": {
        "host": "localhost",
        "port": 8080
    }
}

# Validate before loading
try:
    validate(config_dict, schema)
    config = ConfigManager.from_dict(config_dict)
except ValidationError as e:
    print(f"Configuration validation failed: {e}")
```

## Best Practices

### 1. Always Specify Types

Be explicit about expected types:

```python
# Good: Explicit type specification
port = config.get("server.port", int)
timeout = config.get("server.timeout", float)

# Avoid: No type specification
port = config.get("server.port")  # Returns string "8080"
```

### 2. Use Defaults for Optional Values

Provide sensible defaults:

```python
# Good: Default values for optional configuration
debug = config.get("app.debug", bool, default=False)
workers = config.get("app.workers", int, default=4)
timeout = config.get("app.timeout", float, default=30.0)
```

### 3. Validate Early

Validate configuration at startup:

```python
def validate_config(config: ConfigManager):
    """Validate all required configuration at startup"""
    required = [
        ("database.host", str),
        ("database.port", int),
        ("server.port", int),
        ("auth.secret_key", str)
    ]
    
    errors = []
    for path, type_cls in required:
        try:
            config.get(path, type_cls)
        except (ConfigNotFoundError, ConfigValidationError) as e:
            errors.append(f"{path}: {e}")
    
    if errors:
        raise ConfigValidationError(f"Configuration errors: {'; '.join(errors)}")

# Validate at startup
try:
    validate_config(config)
except ConfigValidationError as e:
    print(f"Invalid configuration: {e}")
    sys.exit(1)
```

### 4. Document Expected Types

Document configuration structure and types:

```python
"""
Configuration Structure:
{
    "server": {
        "host": str,              # Server hostname
        "port": int,              # Port number (1-65535)
        "timeout": float,         # Timeout in seconds
        "debug": bool,            # Debug mode flag
        "workers": int            # Number of worker processes
    },
    "database": {
        "url": str,               # Database connection URL
        "pool_size": int,         # Connection pool size
        "timeout": float          # Query timeout in seconds
    }
}
"""
```

## Error Handling

Handle type errors gracefully:

```python
from aliasconf import ConfigValidationError, ConfigNotFoundError

def get_typed_config(config, path, type_cls, default=None):
    """Safely get typed configuration with error handling"""
    try:
        return config.get(path, type_cls)
    except ConfigNotFoundError:
        if default is not None:
            return default
        raise
    except ConfigValidationError as e:
        logger.warning(f"Invalid config at {path}: {e}, using default")
        if default is not None:
            return default
        raise

# Usage
port = get_typed_config(config, "server.port", int, default=8080)
```

## Next Steps

- Learn about [Template System](templates.md) type safety
- Explore [Alias Resolution](alias-system.md) with types
- See [Practical Examples](../examples/basic.md)