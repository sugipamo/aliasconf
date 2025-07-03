# Quick Start Guide

This guide will help you get started with AliasConf in just a few minutes.

## Installation

Install AliasConf using pip:

```bash
pip install aliasconf
```

## Basic Usage

### 1. Create a Configuration

You can create a configuration from a dictionary:

```python
from aliasconf import ConfigManager

config = ConfigManager.from_dict({
    "app": {
        "name": "My Application",
        "version": "1.0.0",
        "debug": True
    },
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "myapp_db"
    }
})
```

### 2. Access Configuration Values

Use the `get` method with dot notation:

```python
# Get values
app_name = config.get("app.name")  # "My Application"
db_host = config.get("database.host")  # "localhost"

# With type conversion
db_port = config.get("database.port", int)  # 5432 (as integer)
debug_mode = config.get("app.debug", bool)  # True (as boolean)
```

### 3. Use Aliases

The real power of AliasConf comes from aliases:

```python
config = ConfigManager.from_dict({
    "database": {
        "aliases": ["db", "datastore", "storage"],
        "host": "prod.example.com",
        "port": 5432,
        "credentials": {
            "user": "appuser",
            "password": "secret"
        }
    }
})

# Access the same value through different aliases
assert config.get("database.host") == "prod.example.com"
assert config.get("db.host") == "prod.example.com"
assert config.get("datastore.host") == "prod.example.com"
assert config.get("storage.host") == "prod.example.com"
```

## Loading from Files

### YAML Configuration

Create a `config.yaml` file:

```yaml
app:
  aliases: ["application", "service"]
  name: "My Service"
  version: "2.0.0"
  
database:
  aliases: ["db", "datastore"]
  connection:
    host: "localhost"
    port: 5432
    timeout: 30
    
logging:
  aliases: ["log", "logger"]
  level: "INFO"
  file: "/var/log/app.log"
```

Load it in Python:

```python
config = ConfigManager.from_file("config.yaml")

# Access through any alias
log_level = config.get("logging.level")  # "INFO"
log_level = config.get("log.level")      # "INFO"
log_level = config.get("logger.level")   # "INFO"
```

### JSON Configuration

```python
# config.json
{
    "api": {
        "aliases": ["backend", "server"],
        "host": "0.0.0.0",
        "port": 8000,
        "cors": {
            "enabled": true,
            "origins": ["*"]
        }
    }
}

# Load JSON configuration
config = ConfigManager.from_file("config.json")
```

## Template Expansion

AliasConf supports template strings for dynamic values:

```python
config = ConfigManager.from_dict({
    "base": {
        "url": "https://api.example.com",
        "version": "v1"
    },
    "endpoints": {
        "users": "{base.url}/{base.version}/users",
        "posts": "{base.url}/{base.version}/posts",
        "health": "{base.url}/health"
    }
})

# Templates are automatically expanded
users_endpoint = config.get("endpoints.users")
# Returns: "https://api.example.com/v1/users"
```

## Error Handling

AliasConf provides clear error messages:

```python
from aliasconf import ConfigNotFoundError, ConfigValidationError

try:
    # Non-existent key
    value = config.get("missing.key")
except ConfigNotFoundError as e:
    print(f"Configuration not found: {e}")

try:
    # Type conversion error
    port = config.get("app.name", int)  # Can't convert string to int
except ConfigValidationError as e:
    print(f"Validation error: {e}")
```

## Default Values

Provide defaults for optional configuration:

```python
# Returns value or default if not found
timeout = config.get("api.timeout", default=30)
retries = config.get("api.retries", default=3)

# With type conversion
max_connections = config.get("db.max_connections", int, default=100)
```

## Checking Configuration Existence

```python
if config.has("feature.flags.new_ui"):
    enable_new_ui = config.get("feature.flags.new_ui", bool)
else:
    enable_new_ui = False
```

## Complete Example

Here's a complete example putting it all together:

```python
from aliasconf import ConfigManager

# Configuration with aliases and templates
config = ConfigManager.from_dict({
    "service": {
        "aliases": ["app", "application"],
        "name": "payment-service",
        "version": "3.2.1",
        "environment": "production"
    },
    "database": {
        "aliases": ["db", "datastore"],
        "primary": {
            "host": "db-primary.example.com",
            "port": 5432,
            "name": "payments_prod"
        },
        "replica": {
            "host": "db-replica.example.com",
            "port": 5432,
            "name": "payments_prod"
        },
        "connection_string": "postgresql://{database.primary.host}:{database.primary.port}/{database.primary.name}"
    },
    "cache": {
        "aliases": ["redis", "cache_store"],
        "host": "cache.example.com",
        "port": 6379,
        "ttl": 3600
    }
})

# Access configuration
service_name = config.get("app.name")  # "payment-service" (via alias)
db_host = config.get("db.primary.host")  # "db-primary.example.com" (via alias)
cache_ttl = config.get("cache.ttl", int)  # 3600 (with type conversion)

# Template expansion
conn_string = config.get("database.connection_string")
# Returns: "postgresql://db-primary.example.com:5432/payments_prod"

# Check and get with default
if config.has("cache.password"):
    cache_password = config.get("cache.password")
else:
    cache_password = None
```

## Next Steps

- Learn about [Advanced Alias Patterns](../guide/alias-system.md)
- Explore [Template Expansion](../guide/templates.md)
- Read about [Type Safety](../guide/type-safety.md)
- Check out more [Examples](../examples/basic.md)