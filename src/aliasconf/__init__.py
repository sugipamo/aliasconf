"""
AliasConf - Configuration management with powerful alias support

AliasConf provides a flexible configuration management system that allows
multiple keys (aliases) to access the same configuration values. This enables
intuitive configuration access and easy migration between different naming
conventions.

Key Features:
- Multiple aliases for the same configuration value
- Tree-based hierarchical configuration structure
- BFS search for efficient configuration resolution
- Template variable expansion with missing key detection
- Type-safe configuration access with validation
- Support for YAML, JSON, and Python dict configuration sources

Example usage:
    >>> from aliasconf import ConfigManager
    >>>
    >>> # Load configuration from file
    >>> config = ConfigManager.from_file("config.yaml")
    >>>
    >>> # Access same value through different aliases
    >>> config.get("python.timeout")     # 30
    >>> config.get("py.timeout")        # 30 (alias)
    >>> config.get("python3.timeout")   # 30 (alias)
    >>>
    >>> # Create configuration from dict
    >>> config_dict = {
    ...     "python": {
    ...         "aliases": ["py", "python3"],
    ...         "timeout": 30,
    ...         "command": "python {script}"
    ...     }
    ... }
    >>> config = ConfigManager.from_dict(config_dict)
"""

from .core.manager import ConfigManager
from .core.node import ConfigNode
from .core.resolver import (
    create_config_root_from_dict,
    resolve_best,
    resolve_formatted_string,
    resolve_values,
)
from .exceptions.errors import (
    AliasConfError,
    ConfigNodeError,
    ConfigResolverError,
    ConfigValidationError,
)

__version__ = "0.1.1"
__author__ = "AliasConf Development Team"
__email__ = "support@aliasconf.dev"

__all__ = [
    # Core classes
    "ConfigManager",
    "ConfigNode",
    # Resolver functions
    "create_config_root_from_dict",
    "resolve_best",
    "resolve_formatted_string",
    "resolve_values",
    # Exceptions
    "AliasConfError",
    "ConfigNodeError",
    "ConfigResolverError",
    "ConfigValidationError",
    # Metadata
    "__version__",
]
