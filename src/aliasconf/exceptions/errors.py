"""
Custom exception classes for AliasConf.

This module defines all the custom exceptions that can be raised by the
AliasConf library during configuration management operations.
"""


class AliasConfError(Exception):
    """Base exception class for all AliasConf errors.

    All custom exceptions in AliasConf inherit from this base class,
    making it easy to catch any AliasConf-related error.
    """

    pass


class ConfigNodeError(AliasConfError):
    """Exception raised for ConfigNode-related errors.

    This includes errors in:
    - Node creation and initialization
    - Parent-child relationship management
    - Node traversal operations
    - Alias matching operations
    """

    pass


class ConfigResolverError(AliasConfError):
    """Exception raised for configuration resolution errors.

    This includes errors in:
    - Path resolution through the configuration tree
    - Template variable expansion
    - Configuration value retrieval
    - BFS search operations
    """

    pass


class ConfigValidationError(AliasConfError):
    """Exception raised for configuration validation errors.

    This includes errors in:
    - Configuration schema validation
    - Type conversion and checking
    - Required value validation
    - Configuration constraint violations
    """

    pass
