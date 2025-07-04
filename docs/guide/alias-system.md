# Alias System Guide

The alias system is the core feature that sets AliasConf apart from other configuration management libraries. This guide explores advanced patterns and best practices.

## Understanding Aliases

An alias in AliasConf is an alternative name for accessing a configuration node. When you define aliases for a node, you can access that node and all its children through any of the defined aliases.

### Basic Alias Definition

```python
from aliasconf import ConfigManager

config = ConfigManager.from_dict({
    "database": {
        "aliases": ["db", "datastore", "storage"],
        "host": "localhost",
        "port": 5432
    }
})

# All these access the same value
assert config.get("database.host") == "localhost"
assert config.get("db.host") == "localhost"
assert config.get("datastore.host") == "localhost"
assert config.get("storage.host") == "localhost"
```

## Alias Resolution

### How Aliases Work

1. When you access a path like `"db.host"`, AliasConf:
   - Checks if "db" is a direct key
   - If not found, searches for nodes that have "db" as an alias
   - Resolves to the actual node and continues path traversal

2. Aliases are resolved recursively at each level of the path

### Nested Aliases

Aliases can be defined at any level in your configuration hierarchy:

```python
config = ConfigManager.from_dict({
    "services": {
        "aliases": ["backends"],
        "payment": {
            "aliases": ["billing", "payments"],
            "api": {
                "aliases": ["rest", "http"],
                "endpoint": "https://api.payment.com"
            }
        }
    }
})

# Multiple combinations work
paths = [
    "services.payment.api.endpoint",
    "backends.payment.api.endpoint",
    "services.billing.api.endpoint",
    "backends.payments.rest.endpoint",
    "backends.billing.http.endpoint"
]

for path in paths:
    assert config.get(path) == "https://api.payment.com"
```

## Advanced Patterns

### Migration Strategy

Use aliases to smoothly migrate from old to new configuration structures:

```python
# Supporting both old and new configuration formats
config = ConfigManager.from_dict({
    # New structure
    "database": {
        "aliases": ["db"],
        "primary": {
            "host": "primary.db.com",
            "port": 5432
        },
        "replica": {
            "host": "replica.db.com",
            "port": 5432
        }
    },
    # Compatibility aliases for old structure
    "db_host": {
        "aliases": ["database.primary.host"]
    },
    "db_replica_host": {
        "aliases": ["database.replica.host"]
    }
})

# Old code continues to work
old_style_host = config.get("db_host")

# New code uses better structure
new_style_host = config.get("database.primary.host")

assert old_style_host == new_style_host
```

### Team-Specific Naming

Different teams can use their preferred terminology:

```python
config = ConfigManager.from_dict({
    "user_service": {
        "aliases": [
            "auth_service",      # Security team name
            "account_service",   # Frontend team name
            "identity_service"   # Platform team name
        ],
        "endpoint": "https://users.api.com",
        "timeout": 30
    }
})

# Each team uses their preferred name
security_endpoint = config.get("auth_service.endpoint")
frontend_endpoint = config.get("account_service.endpoint")
platform_endpoint = config.get("identity_service.endpoint")

assert security_endpoint == frontend_endpoint == platform_endpoint
```

### Dynamic Alias Addition

You can add aliases programmatically:

```python
config = ConfigManager.from_dict({
    "services": {
        "user": {
            "endpoint": "https://user.api.com"
        }
    }
})

# Add alias dynamically (if your implementation supports it)
# This is a conceptual example - actual API may vary
config.add_alias("services.user", "auth")

# Now accessible via new alias
assert config.get("services.auth.endpoint") == "https://user.api.com"
```

## Best Practices

### 1. Semantic Aliases

Choose aliases that make semantic sense:

```python
# Good: Clear relationship between aliases
{
    "cache": {
        "aliases": ["redis", "memory_store", "cache_layer"],
        "host": "cache.example.com"
    }
}

# Avoid: Unrelated or confusing aliases
{
    "cache": {
        "aliases": ["database", "file_system"],  # Confusing!
        "host": "cache.example.com"
    }
}
```

### 2. Document Your Aliases

Always document why aliases exist:

```python
config = ConfigManager.from_dict({
    "messaging": {
        "aliases": [
            "queue",      # Legacy name from v1
            "broker",     # Industry standard term
            "events"      # Internal team terminology
        ],
        "_comment": "Aliases support migration from v1 (queue) while adopting industry standards",
        "host": "rabbitmq.example.com"
    }
})
```

### 3. Avoid Circular References

Be careful not to create circular alias references:

```python
# DON'T DO THIS - Circular reference
{
    "serviceA": {
        "aliases": ["serviceB"],
        "value": 1
    },
    "serviceB": {
        "aliases": ["serviceA"],  # Circular!
        "value": 2
    }
}
```

### 4. Use Aliases for API Versioning

Support multiple API versions:

```python
config = ConfigManager.from_dict({
    "api": {
        "v3": {
            "aliases": ["current", "latest"],
            "endpoint": "https://api.v3.example.com"
        },
        "v2": {
            "aliases": ["stable"],
            "endpoint": "https://api.v2.example.com"
        },
        "v1": {
            "aliases": ["legacy"],
            "endpoint": "https://api.v1.example.com"
        }
    }
})

# Client code can use version-agnostic names
current_api = config.get("api.current.endpoint")
stable_api = config.get("api.stable.endpoint")
```

## Performance Considerations

1. **Alias Resolution Overhead**: While minimal, alias resolution does add a small overhead. For performance-critical paths, consider caching resolved values.

2. **Number of Aliases**: Having many aliases doesn't significantly impact performance due to efficient internal indexing.

3. **Deep Nesting**: Deeply nested aliases are resolved efficiently using indexed lookups.

## Debugging Aliases

When debugging alias resolution:

```python
# Check if a path exists (including through aliases)
if config.has("some.alias.path"):
    value = config.get("some.alias.path")
    print(f"Found value: {value}")
else:
    print("Path not found")

# Get all aliases for a node (if API supports)
# This is a conceptual example
# aliases = config.get_aliases("database")
# print(f"Aliases for database: {aliases}")
```

## Next Steps

- Explore [Template Expansion](templates.md) with aliases
- Learn about [Type Safety](type-safety.md) in alias resolution
- See more [Practical Examples](../examples/basic.md)