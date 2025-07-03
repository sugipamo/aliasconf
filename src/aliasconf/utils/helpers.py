"""
Helper utilities for AliasConf.

This module provides various utility functions for common operations
like dictionary merging, path normalization, and validation.
"""

from typing import Any, Dict, List, Tuple, Union

from ..exceptions.errors import ConfigValidationError


def deep_merge_dicts(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dictionaries.

    The overlay dictionary takes precedence over the base dictionary.
    Nested dictionaries are merged recursively, while other values
    are completely replaced.

    Args:
        base: Base dictionary to merge into
        overlay: Dictionary to merge over the base

    Returns:
        New dictionary with merged values

    Example:
        >>> base = {"a": {"x": 1, "y": 2}, "b": 3}
        >>> overlay = {"a": {"y": 20, "z": 30}, "c": 4}
        >>> result = deep_merge_dicts(base, overlay)
        >>> print(result)  # {"a": {"x": 1, "y": 20, "z": 30}, "b": 3, "c": 4}
    """
    result = base.copy()

    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = deep_merge_dicts(result[key], value)
        else:
            # Replace value completely
            result[key] = value

    return result


def normalize_path(path: Union[str, List[str], Tuple[str, ...]]) -> List[str]:
    """Normalize a configuration path to a list of strings.

    Handles various input formats and converts them to a standardized
    list format for consistent path processing.

    Args:
        path: Path in various formats (string with dots, list, tuple)

    Returns:
        Normalized path as list of strings

    Raises:
        ConfigValidationError: If path format is invalid

    Example:
        >>> normalize_path("python.timeout")  # ["python", "timeout"]
        >>> normalize_path(["python", "timeout"])  # ["python", "timeout"]
        >>> normalize_path(("python", "timeout"))  # ["python", "timeout"]
    """
    if isinstance(path, str):
        if not path.strip():
            raise ConfigValidationError("Path cannot be empty string")
        # Check for empty components
        parts = path.split(".")
        for i, part in enumerate(parts):
            if not part.strip():
                if i == 0:
                    raise ConfigValidationError("Path cannot start with a dot")
                elif i == len(parts) - 1:
                    raise ConfigValidationError("Path cannot end with a dot")
                else:
                    raise ConfigValidationError(
                        "Path cannot contain empty components (double dots)"
                    )
        # Split on dots and return stripped parts
        return [part.strip() for part in parts]
    elif isinstance(path, (list, tuple)):
        if not path:
            raise ConfigValidationError("Path cannot be empty")
        # Convert all elements to strings and validate
        normalized = []
        for part in path:
            if not isinstance(part, (str, int)):
                raise ConfigValidationError(
                    f"Path parts must be strings or integers: {part}"
                )
            str_part = str(part).strip()
            if not str_part:
                raise ConfigValidationError("Path parts cannot be empty")
            normalized.append(str_part)
        return normalized
    else:
        raise ConfigValidationError(
            f"Invalid path type: {type(path)}. Expected str, list, or tuple"
        )


def validate_aliases(aliases: Any) -> List[str]:
    """Validate and normalize a list of aliases.

    Ensures aliases are provided as a list of strings and performs
    basic validation on each alias.

    Args:
        aliases: Aliases to validate (should be list of strings)

    Returns:
        Validated and normalized list of aliases

    Raises:
        ConfigValidationError: If aliases format is invalid

    Example:
        >>> validate_aliases(["py", "python3"])  # ["py", "python3"]
        >>> validate_aliases("py")  # Raises ConfigValidationError
    """
    if not isinstance(aliases, list):
        raise ConfigValidationError(f"Aliases must be a list, got {type(aliases)}")

    if not aliases:
        raise ConfigValidationError("Aliases list cannot be empty")

    validated = []
    for alias in aliases:
        if not isinstance(alias, str):
            raise ConfigValidationError(
                f"Each alias must be a string, got {type(alias)}: {alias}"
            )

        alias = alias.strip()
        if not alias:
            raise ConfigValidationError("Aliases cannot be empty strings")

        if alias in validated:
            raise ConfigValidationError(f"Duplicate alias found: {alias}")

        validated.append(alias)

    return validated


def is_template_string(value: str) -> bool:
    """Check if a string contains template placeholders.

    Args:
        value: String to check for template syntax

    Returns:
        True if string contains {key} placeholders, False otherwise

    Example:
        >>> is_template_string("Hello {name}")  # True
        >>> is_template_string("Hello world")   # False
    """
    import re

    pattern = re.compile(r"{(\w+)}")
    return bool(pattern.search(value))


def flatten_dict(
    data: Dict[str, Any],
    parent_key: str = "",
    separator: str = ".",
) -> Dict[str, Any]:
    """Flatten a nested dictionary structure.

    Converts a nested dictionary into a flat dictionary with compound keys.

    Args:
        data: Dictionary to flatten
        parent_key: Key prefix for nested items
        separator: Separator to use between key parts

    Returns:
        Flattened dictionary

    Example:
        >>> nested = {"a": {"b": {"c": 1}, "d": 2}, "e": 3}
        >>> flattened = flatten_dict(nested)
        >>> print(flattened)  # {"a.b.c": 1, "a.d": 2, "e": 3}
    """
    items: List[Tuple[str, Any]] = []

    for key, value in data.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, separator).items())
        else:
            items.append((new_key, value))

    return dict(items)


def unflatten_dict(
    data: Dict[str, Any],
    separator: str = ".",
) -> Dict[str, Any]:
    """Unflatten a dictionary with compound keys.

    Converts a flat dictionary with compound keys back to nested structure.

    Args:
        data: Flattened dictionary to unflatten
        separator: Separator used between key parts

    Returns:
        Nested dictionary structure

    Example:
        >>> flat = {"a.b.c": 1, "a.d": 2, "e": 3}
        >>> nested = unflatten_dict(flat)
        >>> print(nested)  # {"a": {"b": {"c": 1}, "d": 2}, "e": 3}
    """
    result: Dict[str, Any] = {}

    for key, value in data.items():
        keys = key.split(separator)
        current = result

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

    return result


def safe_get_nested(
    data: Dict[str, Any],
    path: Union[str, List[str]],
    default: Any = None,
) -> Any:
    """Safely get a value from nested dictionary structure.

    Traverses nested dictionaries using a path and returns the value
    if found, or a default value if any part of the path doesn't exist.

    Args:
        data: Dictionary to search in
        path: Path to the desired value (string with dots or list)
        default: Default value to return if path not found

    Returns:
        Value at the specified path, or default if not found

    Example:
        >>> data = {"a": {"b": {"c": 42}}}
        >>> safe_get_nested(data, "a.b.c")  # 42
        >>> safe_get_nested(data, "a.b.x", "not found")  # "not found"
    """
    try:
        normalized_path = normalize_path(path)
        current = data

        for key in normalized_path:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]

        return current
    except (ConfigValidationError, KeyError, TypeError):
        return default


def validate_config_structure(data: Any, allow_empty: bool = False) -> None:
    """Validate basic configuration structure requirements.

    Performs basic validation on configuration data to ensure it meets
    minimum requirements for processing.

    Args:
        data: Configuration data to validate
        allow_empty: Whether to allow empty configurations

    Raises:
        ConfigValidationError: If configuration structure is invalid
    """
    if data is None:
        raise ConfigValidationError("Configuration data cannot be None")

    if not isinstance(data, dict):
        raise ConfigValidationError(
            f"Configuration must be a dictionary, got {type(data)}"
        )

    if not allow_empty and not data:
        raise ConfigValidationError("Configuration cannot be empty")

    # Check for reserved keys that might conflict with internal operations
    reserved_keys = {"__aliasconf_internal__", "__meta__"}
    for key in data:
        if key in reserved_keys:
            raise ConfigValidationError(f"Configuration key '{key}' is reserved")

        if not isinstance(key, str):
            raise ConfigValidationError(
                f"Configuration keys must be strings, got {type(key)}: {key}"
            )

        if not key.strip():
            raise ConfigValidationError("Configuration keys cannot be empty strings")
