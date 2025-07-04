# Basic Examples

This page demonstrates basic usage patterns of AliasConf through practical examples.

## Simple Configuration

```python
from aliasconf import ConfigManager

# Basic configuration
config = ConfigManager.from_dict({
    "app": {
        "name": "MyApp",
        "version": "1.0.0"
    },
    "server": {
        "host": "localhost",
        "port": 8080
    }
})

# Access values
app_name = config.get("app.name")  # "MyApp"
server_port = config.get("server.port", int)  # 8080
```

## Using Aliases

```python
# Configuration with aliases
config = ConfigManager.from_dict({
    "database": {
        "aliases": ["db", "datastore"],
        "host": "localhost",
        "port": 5432,
        "name": "mydb"
    }
})

# Access through different aliases
assert config.get("database.host") == "localhost"
assert config.get("db.host") == "localhost"
assert config.get("datastore.host") == "localhost"
```

## Template Expansion

```python
# Using templates
config = ConfigManager.from_dict({
    "environment": "production",
    "region": "us-east-1",
    "service": {
        "name": "api-service",
        "url": "https://{service.name}.{region}.example.com/{environment}"
    }
})

# Template is automatically expanded
service_url = config.get("service.url")
# Returns: "https://api-service.us-east-1.example.com/production"
```

## Nested Aliases

```python
# Complex nested structure with aliases
config = ConfigManager.from_dict({
    "services": {
        "aliases": ["backends", "apis"],
        "payment": {
            "aliases": ["billing", "payments"],
            "endpoint": "https://payment.example.com",
            "timeout": 30
        }
    }
})

# Multiple ways to access the same value
assert config.get("services.payment.endpoint") == "https://payment.example.com"
assert config.get("backends.billing.endpoint") == "https://payment.example.com"
assert config.get("apis.payments.endpoint") == "https://payment.example.com"
```

## Configuration Migration Example

```python
# Old configuration structure
old_config = {
    "db_host": "localhost",
    "db_port": 5432,
    "api_key": "secret123"
}

# New structure with aliases for backward compatibility
new_config = ConfigManager.from_dict({
    "database": {
        "aliases": ["db"],
        "connection": {
            "host": old_config["db_host"],
            "port": old_config["db_port"]
        }
    },
    "auth": {
        "api_key": old_config["api_key"]
    },
    # Aliases for backward compatibility
    "db_host": {
        "aliases": ["database.connection.host"]
    },
    "db_port": {
        "aliases": ["database.connection.port"]
    },
    "api_key": {
        "aliases": ["auth.api_key"]
    }
})

# Old code continues to work
assert new_config.get("db_host") == "localhost"
# New code can use better structure
assert new_config.get("database.connection.host") == "localhost"
```

## Error Handling

```python
from aliasconf import ConfigNotFoundError, ConfigValidationError

config = ConfigManager.from_dict({
    "timeout": "30",
    "retries": 3
})

# Handle missing configuration
try:
    value = config.get("missing.key")
except ConfigNotFoundError:
    value = "default_value"

# Handle type conversion errors
try:
    # This will fail because "thirty" cannot be converted to int
    config.set("timeout", "thirty")
    timeout = config.get("timeout", int)
except ConfigValidationError as e:
    print(f"Invalid configuration: {e}")
    timeout = 30  # Use default
```

## Loading from Files

```python
# config.yaml
"""
app:
  aliases: ["application", "service"]
  name: "MyService"
  version: "2.0.0"
  
database:
  aliases: ["db"]
  host: "${DB_HOST|localhost}"
  port: "${DB_PORT|5432}"
  
logging:
  level: "INFO"
  format: "[{app.name}] {message}"
"""

# Load and use
config = ConfigManager.from_file("config.yaml")

# Access with aliases
app_name = config.get("service.name")  # "MyService" via alias
db_host = config.get("db.host")  # from environment or "localhost"

# Template in logging format
log_format = config.get("logging.format")  # "[MyService] {message}"
```

## Next Steps

- Learn about [Advanced Alias Patterns](../guide/alias-system.md)
- Explore [Template Features](../guide/templates.md)
- Understand [Type Safety](../guide/type-safety.md)