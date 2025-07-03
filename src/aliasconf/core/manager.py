"""
Main configuration manager for AliasConf.

This module provides the ConfigManager class, which serves as the primary
interface for loading, managing, and accessing configuration data with
alias support.
"""

import json
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

import yaml

from ..exceptions.errors import (
    AliasConfError,
    ConfigResolverError,
    ConfigValidationError,
)
from ..utils.helpers import (
    deep_merge_dicts,
    normalize_path,
    validate_config_structure,
)
from .cache import ConfigCache
from .node import ConfigNode
from .optimized_resolver import (
    clear_global_cache,
    resolve_best_optimized,
)
from .resolver import (
    create_config_root_from_dict,
    resolve_best,
    resolve_formatted_string,
    resolve_values,
)

T = TypeVar("T")


class ConfigManager:
    """Main configuration manager with alias support.

    The ConfigManager provides a high-level interface for working with
    configuration data that supports multiple aliases for the same values.
    It can load configuration from various sources and provides type-safe
    access to configuration values.

    Key Features:
    - Load configuration from YAML, JSON, or Python dictionaries
    - Multiple aliases for the same configuration values
    - Type-safe configuration access with automatic conversion
    - Template variable expansion using configuration values
    - Hierarchical configuration structure with inheritance
    - Configuration validation and error handling

    Example:
        >>> # Load from file
        >>> config = ConfigManager.from_file("config.yaml")
        >>>
        >>> # Access values through different aliases
        >>> timeout = config.get("python.timeout", int)  # 30
        >>> timeout = config.get("py.timeout", int)      # 30 (same value)
        >>>
        >>> # Template expansion
        >>> command = config.get_formatted("python.command", {"script": "test.py"})
        >>> print(command)  # "python test.py"
    """

    def __init__(self, root_node: Optional[ConfigNode] = None):
        """Initialize ConfigManager.

        Args:
            root_node: Pre-built configuration tree root node
        """
        self._root = root_node
        self._cache: Dict[Tuple[Tuple[str, ...], type], Any] = {}
        self._config_cache = ConfigCache()
        self._use_optimized = True  # Flag to enable/disable optimization

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfigManager":
        """Create ConfigManager from a dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            New ConfigManager instance

        Raises:
            ConfigValidationError: If data structure is invalid

        Example:
            >>> config_dict = {
            ...     "python": {
            ...         "aliases": ["py", "python3"],
            ...         "timeout": 30
            ...     }
            ... }
            >>> config = ConfigManager.from_dict(config_dict)
        """
        validate_config_structure(data, allow_empty=True)
        root = create_config_root_from_dict(data)
        instance = cls(root)
        # Pre-build index for optimization
        if instance._use_optimized and instance._root:
            instance._config_cache.initialize(instance._root)
        return instance

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "ConfigManager":
        """Load configuration from a file.

        Supports YAML and JSON file formats. Format is determined by file extension.

        Args:
            file_path: Path to configuration file

        Returns:
            New ConfigManager instance

        Raises:
            AliasConfError: If file cannot be loaded or parsed

        Example:
            >>> config = ConfigManager.from_file("config.yaml")
            >>> config = ConfigManager.from_file("config.json")
        """
        path = Path(file_path)

        if not path.exists():
            raise AliasConfError(f"Configuration file not found: {file_path}")

        try:
            with open(path, encoding="utf-8") as f:
                if path.suffix.lower() in [".yml", ".yaml"]:
                    data = yaml.safe_load(f)
                elif path.suffix.lower() == ".json":
                    data = json.load(f)
                else:
                    raise AliasConfError(f"Unsupported file format: {path.suffix}")

        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise AliasConfError(f"Failed to parse configuration file: {e}") from e
        except OSError as e:
            raise AliasConfError(f"Failed to read configuration file: {e}") from e

        if data is None:
            data = {}

        return cls.from_dict(data)

    @classmethod
    def from_files(cls, *file_paths: Union[str, Path]) -> "ConfigManager":
        """Load and merge configuration from multiple files.

        Files are merged in order, with later files taking precedence over earlier ones.
        Preserves alias information during merge.

        Args:
            *file_paths: Paths to configuration files to merge

        Returns:
            New ConfigManager instance with merged configuration

        Example:
            >>> config = ConfigManager.from_files(
            ...     "base_config.yaml",
            ...     "environment_config.yaml",
            ...     "local_config.yaml"
            ... )
        """
        if not file_paths:
            raise AliasConfError("At least one file path must be provided")

        # Load raw data from files and merge them
        merged_data: Dict[str, Any] = {}

        for file_path in file_paths:
            path = Path(file_path)
            if not path.exists():
                raise AliasConfError(f"Configuration file not found: {path}")

            try:
                with open(path) as f:
                    if path.suffix in [".yaml", ".yml"]:
                        data = yaml.safe_load(f)
                    elif path.suffix == ".json":
                        data = json.load(f)
                    else:
                        raise AliasConfError(f"Unsupported file format: {path.suffix}")

                if data:
                    merged_data = deep_merge_dicts(merged_data, data)

            except (yaml.YAMLError, json.JSONDecodeError) as e:
                raise AliasConfError(
                    f"Failed to parse configuration file {path}: {e}"
                ) from e
            except OSError as e:
                raise AliasConfError(
                    f"Failed to read configuration file {path}: {e}"
                ) from e

        return cls.from_dict(merged_data)

    def get(
        self,
        path: Union[str, List[str]],
        return_type: Type[T],
        default: Optional[T] = None,
    ) -> T:
        """Get a configuration value with type safety.

        Resolves the configuration path through the tree structure and returns
        the value converted to the specified type.

        Args:
            path: Configuration path (e.g., "python.timeout" or ["python", "timeout"])
            return_type: Expected return type (str, int, bool, float, etc.)
            default: Default value if path not found

        Returns:
            Configuration value converted to specified type

        Raises:
            ConfigResolverError: If path cannot be resolved
            ConfigValidationError: If value cannot be converted to specified type

        Example:
            >>> timeout = config.get("python.timeout", int)  # Returns int
            >>> name = config.get("app.name", str, "default")  # Returns str with default
        """
        if self._root is None:
            if default is not None:
                return default
            raise ConfigResolverError("No configuration loaded")

        # Normalize path and create cache key
        normalized_path = normalize_path(path)
        cache_key = (tuple(normalized_path), return_type)

        if cache_key in self._cache:
            return cast(T, self._cache[cache_key])

        try:
            # Use optimized resolver if enabled
            if self._use_optimized:
                node = resolve_best_optimized(
                    self._root, normalized_path, self._config_cache
                )
            else:
                node = resolve_best(self._root, normalized_path)

            if node is None:
                if default is not None:
                    return default
                raise ConfigResolverError(f"Configuration path not found: {path}")

            value = self._convert_value(node.value, return_type)
            self._cache[cache_key] = value
            return value

        except Exception:
            if default is not None:
                return default
            raise

    def get_all(self, path: Union[str, List[str]], return_type: Type[T]) -> List[T]:
        """Get all values matching a configuration path.

        Returns all configuration values that match the given path, useful
        when multiple nodes might match due to aliases or wildcards.

        Args:
            path: Configuration path
            return_type: Expected return type for each value

        Returns:
            List of values converted to specified type
        """
        if self._root is None:
            return []

        normalized_path = normalize_path(path)
        values = resolve_values(self._root, normalized_path)
        return [self._convert_value(value, return_type) for value in values]

    def has(self, path: Union[str, List[str]]) -> bool:
        """Check if a configuration path exists.

        Args:
            path: Configuration path to check

        Returns:
            True if path exists, False otherwise
        """
        if self._root is None:
            return False

        try:
            normalized_path = normalize_path(path)
            node = resolve_best(self._root, normalized_path)
            return node is not None
        except Exception:
            return False

    @overload
    def get_formatted(
        self, path: Union[str, List[str]], context: Optional[Dict[str, Any]] = None
    ) -> str: ...

    @overload
    def get_formatted(
        self,
        path: Union[str, List[str]],
        context: Optional[Dict[str, Any]],
        return_type: Type[T],
    ) -> T: ...

    def get_formatted(
        self,
        path: Union[str, List[str]],
        context: Optional[Dict[str, Any]] = None,
        return_type: Any = str,
    ) -> Any:
        """Get a configuration value with template formatting.

        Retrieves a configuration value and formats it as a template using
        the provided context and other configuration values.

        Args:
            path: Configuration path
            context: Template variables for formatting
            return_type: Expected return type

        Returns:
            Formatted value converted to specified type

        Example:
            >>> # Config: {"python": {"command": "python {script}"}}
            >>> cmd = config.get_formatted("python.command", {"script": "test.py"})
            >>> print(cmd)  # "python test.py"
        """
        if self._root is None:
            raise ConfigResolverError("No configuration loaded")

        # Get the raw template value
        template = self.get(path, str)

        # Format the template
        if context is None:
            context = {}

        formatted = resolve_formatted_string(template, self._root, context)
        return self._convert_value(formatted, return_type)

    def merge(self, other: "ConfigManager") -> "ConfigManager":
        """Merge this configuration with another ConfigManager.

        Creates a new ConfigManager with the configurations merged together.
        The other configuration takes precedence over this one.

        Args:
            other: ConfigManager to merge with

        Returns:
            New ConfigManager with merged configuration
        """
        if self._root is None:
            return other
        if other._root is None:
            return self

        self_data = self._root.value if self._root.value else {}
        other_data = other._root.value if other._root.value else {}

        merged_data = deep_merge_dicts(self_data, other_data)
        return ConfigManager.from_dict(merged_data)

    def to_dict(self, include_aliases: bool = False) -> Dict[str, Any]:
        """Convert configuration back to dictionary format.

        Args:
            include_aliases: Whether to include alias information in output

        Returns:
            Dictionary representation of the configuration
        """
        if self._root is None:
            return {}

        def node_to_dict(node: ConfigNode) -> Any:
            if isinstance(node.value, dict):
                result = {}
                # Add aliases if requested and available
                if include_aliases and node.aliases:
                    result["aliases"] = node.aliases
                # Add value content
                result.update(node.value)
                # Process child nodes
                for child in node.next_nodes:
                    result[child.key] = node_to_dict(child)
                return result
            else:
                return node.value

        # Process from root's children
        result = {}
        for child in self._root.next_nodes:
            result[child.key] = node_to_dict(child)

        return result

    def _convert_value(self, value: Any, target_type: Type[T]) -> T:
        """Convert a value to the specified type.

        Args:
            value: Value to convert
            target_type: Target type for conversion

        Returns:
            Converted value

        Raises:
            ConfigValidationError: If conversion fails
        """
        if value is None:
            raise ConfigValidationError(
                "Cannot convert None to any type without a default value"
            )

        if target_type is str:
            return cast(T, str(value))
        elif target_type is int:
            if isinstance(value, bool):
                raise ConfigValidationError("Cannot convert bool to int")
            try:
                return cast(T, int(value))
            except (ValueError, TypeError) as e:
                raise ConfigValidationError(
                    f"Cannot convert {value} to int: {e}"
                ) from e
        elif target_type is bool:
            if isinstance(value, bool):
                return cast(T, value)
            elif isinstance(value, str):
                if value.lower() in ("true", "1", "yes", "on"):
                    return cast(T, True)
                elif value.lower() in ("false", "0", "no", "off"):
                    return cast(T, False)
                else:
                    raise ConfigValidationError(
                        f"Cannot convert string '{value}' to bool"
                    )
            else:
                raise ConfigValidationError(f"Cannot convert {type(value)} to bool")
        elif target_type is float:
            try:
                return cast(T, float(value))
            except (ValueError, TypeError) as e:
                raise ConfigValidationError(
                    f"Cannot convert {value} to float: {e}"
                ) from e
        elif target_type is list:
            if isinstance(value, list):
                return cast(T, value)
            else:
                raise ConfigValidationError(f"Cannot convert {type(value)} to list")
        elif target_type is dict:
            if isinstance(value, dict):
                return cast(T, value)
            else:
                raise ConfigValidationError(f"Cannot convert {type(value)} to dict")
        else:
            # For other types, try direct conversion
            if isinstance(value, target_type):
                return value
            else:
                raise ConfigValidationError(
                    f"Cannot convert {type(value)} to {target_type}"
                )

    def clear_cache(self) -> None:
        """Clear all internal caches.

        This should be called when the configuration structure changes.
        """
        self._cache.clear()
        self._config_cache.clear()
        clear_global_cache()

    def __repr__(self) -> str:
        """Return string representation of ConfigManager."""
        if self._root is None:
            return "ConfigManager(empty)"
        return "ConfigManager(loaded)"
