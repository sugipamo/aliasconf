"""
Core functionality for AliasConf configuration management.

This module contains the core classes and functions that power AliasConf's
configuration management system with alias support.
"""

from .manager import ConfigManager
from .node import ConfigNode
from .resolver import (
    create_config_root_from_dict,
    resolve_best,
    resolve_formatted_string,
    resolve_values,
)

__all__ = [
    "ConfigManager",
    "ConfigNode",
    "create_config_root_from_dict",
    "resolve_best",
    "resolve_formatted_string",
    "resolve_values",
]
