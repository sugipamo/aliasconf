"""
Exception classes for AliasConf configuration management.

This module defines all custom exceptions used throughout the AliasConf library.
All exceptions inherit from AliasConfError for easy catching.
"""

from .errors import (
    AliasConfError,
    ConfigNodeError,
    ConfigResolverError,
    ConfigValidationError,
)

__all__ = [
    "AliasConfError",
    "ConfigNodeError",
    "ConfigResolverError",
    "ConfigValidationError",
]
