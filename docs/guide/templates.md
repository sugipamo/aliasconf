# Template Expansion Guide

AliasConf provides powerful template expansion capabilities that allow you to create dynamic configuration values. This guide covers all aspects of the template system.

## Basic Template Syntax

Templates in AliasConf use curly braces `{}` to reference other configuration values:

```python
from aliasconf import ConfigManager

config = ConfigManager.from_dict({
    "app": {
        "name": "myapp",
        "version": "1.0.0"
    },
    "urls": {
        "base": "https://api.example.com",
        "versioned": "{urls.base}/v{app.version}",
        "health": "{urls.versioned}/health"
    }
})

# Templates are automatically expanded
assert config.get("urls.versioned") == "https://api.example.com/v1.0.0"
assert config.get("urls.health") == "https://api.example.com/v1.0.0/health"
```

## Template Resolution

### How Templates Work

1. When a value contains `{...}`, it's treated as a template
2. The content between braces is treated as a configuration path
3. The path is resolved (including alias resolution)
4. The template placeholder is replaced with the resolved value

### Nested Template Resolution

Templates can reference other templates:

```python
config = ConfigManager.from_dict({
    "env": "production",
    "region": "us-east-1",
    "service": "api",
    "base_domain": "example.com",
    
    "urls": {
        "pattern": "{service}.{env}.{region}.{base_domain}",
        "full": "https://{urls.pattern}",
        "health": "{urls.full}/health",
        "metrics": "{urls.full}/metrics"
    }
})

# Multi-level template expansion
assert config.get("urls.full") == "https://api.production.us-east-1.example.com"
assert config.get("urls.health") == "https://api.production.us-east-1.example.com/health"
```

## Advanced Template Features

### Multiple Placeholders

Templates can contain multiple placeholders:

```python
config = ConfigManager.from_dict({
    "db": {
        "host": "localhost",
        "port": 5432,
        "name": "myapp",
        "user": "dbuser"
    },
    "connection": {
        "url": "postgresql://{db.user}@{db.host}:{db.port}/{db.name}"
    }
})

url = config.get("connection.url")
assert url == "postgresql://dbuser@localhost:5432/myapp"
```

### Partial Templates

Mix static text with template placeholders:

```python
config = ConfigManager.from_dict({
    "app": {
        "name": "DataProcessor",
        "version": "2.1.0"
    },
    "logging": {
        "format": "[{app.name} v{app.version}] %(asctime)s - %(levelname)s - %(message)s",
        "file": "/var/log/{app.name}/app.log"
    }
})

log_format = config.get("logging.format")
# Returns: "[DataProcessor v2.1.0] %(asctime)s - %(levelname)s - %(message)s"
```

### Environment Variable Integration

Templates can reference environment variables:

```python
import os
os.environ["API_KEY"] = "secret123"
os.environ["DB_HOST"] = "prod.db.com"

config = ConfigManager.from_dict({
    "database": {
        "host": "{env.DB_HOST|localhost}",  # With default
        "port": "{env.DB_PORT|5432}"
    },
    "api": {
        "key": "{env.API_KEY}",  # Required env var
        "timeout": "{env.API_TIMEOUT|30}"
    }
})

# Environment variables are resolved
assert config.get("database.host") == "prod.db.com"
assert config.get("database.port") == "5432"  # Uses default
```

## Template Patterns

### Configuration Profiles

Use templates to manage different environments:

```python
config = ConfigManager.from_dict({
    "profile": "development",  # Change this to switch profiles
    
    "profiles": {
        "development": {
            "db_host": "localhost",
            "db_name": "app_dev",
            "debug": True,
            "log_level": "DEBUG"
        },
        "production": {
            "db_host": "prod.db.example.com",
            "db_name": "app_prod",
            "debug": False,
            "log_level": "INFO"
        }
    },
    
    "database": {
        "host": "{profiles.{profile}.db_host}",
        "name": "{profiles.{profile}.db_name}"
    },
    "app": {
        "debug": "{profiles.{profile}.debug}",
        "log_level": "{profiles.{profile}.log_level}"
    }
})

# Configuration automatically uses the right profile
assert config.get("database.host") == "localhost"
assert config.get("app.debug") == True
```

### Service Discovery

Templates for dynamic service endpoints:

```python
config = ConfigManager.from_dict({
    "services": {
        "namespace": "production",
        "domain": "internal.example.com",
        "registry": {
            "users": {
                "port": 8080,
                "version": "v2"
            },
            "orders": {
                "port": 8081,
                "version": "v1"
            },
            "inventory": {
                "port": 8082,
                "version": "v1"
            }
        }
    },
    
    "endpoints": {
        "users": "http://users.{services.namespace}.{services.domain}:{services.registry.users.port}/{services.registry.users.version}",
        "orders": "http://orders.{services.namespace}.{services.domain}:{services.registry.orders.port}/{services.registry.orders.version}"
    }
})

users_endpoint = config.get("endpoints.users")
# Returns: "http://users.production.internal.example.com:8080/v2"
```

### Template Functions

While basic AliasConf supports simple substitution, you might extend it with functions:

```python
# Conceptual example - actual implementation may vary
config = ConfigManager.from_dict({
    "values": {
        "timeout_seconds": 30,
        "rate_limit": 1000
    },
    "calculated": {
        "timeout_ms": "{multiply({values.timeout_seconds}, 1000)}",
        "rate_per_second": "{divide({values.rate_limit}, 60)}"
    }
})
```

## Best Practices

### 1. Keep Templates Simple

Avoid overly complex template chains:

```python
# Good: Clear and understandable
{
    "api": {
        "base": "https://api.example.com",
        "v1": "{api.base}/v1",
        "users": "{api.v1}/users"
    }
}

# Avoid: Too many levels of indirection
{
    "a": "{b}",
    "b": "{c}",
    "c": "{d}",
    "d": "{e}",
    "e": "value"  # Hard to track!
}
```

### 2. Document Template Dependencies

Make template relationships clear:

```python
config = ConfigManager.from_dict({
    "_templates": {
        "_description": "URL templates depend on: environment, region, service",
        "environment": "production",
        "region": "us-west-2",
        "service": "api"
    },
    "url": "https://{_templates.service}-{_templates.environment}.{_templates.region}.example.com"
})
```

### 3. Provide Defaults

Use default values for optional templates:

```python
config = ConfigManager.from_dict({
    "server": {
        "host": "{env.SERVER_HOST|0.0.0.0}",
        "port": "{env.SERVER_PORT|8080}",
        "workers": "{env.WORKERS|4}"
    }
})
```

### 4. Validate Template Results

Ensure expanded templates produce valid values:

```python
config = ConfigManager.from_dict({
    "ports": {
        "base": "8080",
        "admin": "{ports.base}1"  # Results in "80801"
    }
})

# Validate after expansion
admin_port = config.get("ports.admin", int)  # Will fail if not valid integer
```

## Error Handling

Handle template resolution errors gracefully:

```python
from aliasconf import ConfigNotFoundError, TemplateError

config = ConfigManager.from_dict({
    "template": "{missing.value}"
})

try:
    value = config.get("template")
except (ConfigNotFoundError, TemplateError) as e:
    print(f"Template resolution failed: {e}")
    value = "default"
```

## Performance Tips

1. **Cache Expanded Values**: Template expansion happens on each access. Cache results if accessed frequently.

2. **Avoid Circular References**: Circular template references will cause errors:
   ```python
   # DON'T DO THIS
   {
       "a": "{b}",
       "b": "{a}"  # Circular reference!
   }
   ```

3. **Limit Template Depth**: Deeply nested templates impact performance and readability.

## Next Steps

- Learn about [Type Safety](type-safety.md) with templates
- Explore [Alias System](alias-system.md) integration
- See [Practical Examples](../examples/basic.md)