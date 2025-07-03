"""
Template formatting utilities for AliasConf.

This module provides utilities for formatting template strings with partial
data, allowing for graceful handling of missing keys.
"""

import re
from functools import lru_cache
from typing import Any, Dict, List, Tuple


def format_with_missing_keys(template: str, **kwargs: Any) -> Tuple[str, List[str]]:
    """Format template with partial data, returning missing keys.

    This function formats a template string with the provided keyword arguments,
    but gracefully handles missing keys by leaving them in their original form
    and returning a list of missing keys.

    Args:
        template: Template string containing {key} placeholders
        **kwargs: Format variables provided as keyword arguments

    Returns:
        Tuple containing:
        - formatted_string: The template with available keys replaced
        - missing_keys: List of keys that were found in template but not provided

    Example:
        >>> template = "Hello {name}, your score is {score}"
        >>> formatted, missing = format_with_missing_keys(template, name="Alice")
        >>> print(formatted)  # "Hello Alice, your score is {score}"
        >>> print(missing)    # ["score"]
    """
    keys = extract_format_keys(template)
    missing = []
    formatted = template

    # Handle each key separately to support dotted paths
    for key in keys:
        if key in kwargs:
            # Simple replacement for keys that are directly in kwargs
            formatted = formatted.replace('{' + key + '}', str(kwargs[key]))
        else:
            missing.append(key)

    return formatted, missing


@lru_cache(maxsize=512)
def extract_format_keys(template: str) -> List[str]:
    """Extract format keys from template string.

    Uses regex to find all {key} patterns in the template string and returns
    the list of keys. Results are cached for performance.

    Args:
        template: Template string to extract keys from

    Returns:
        List of keys found in the template

    Example:
        >>> keys = extract_format_keys("Hello {name}, your {type} is {value}")
        >>> print(keys)  # ["name", "type", "value"]
    """
    pattern = re.compile(r'{([\w.]+)}')
    return pattern.findall(template)


def validate_template_syntax(template: str) -> Tuple[bool, str]:
    """Validate that a template string has valid syntax.

    Checks for common template syntax errors like unmatched braces.

    Args:
        template: Template string to validate

    Returns:
        Tuple containing:
        - is_valid: True if template syntax is valid
        - error_message: Error message if invalid, empty string if valid

    Example:
        >>> valid, error = validate_template_syntax("Hello {name}")
        >>> print(valid)  # True
        >>> print(error)  # ""
        >>>
        >>> valid, error = validate_template_syntax("Hello {name")
        >>> print(valid)  # False
        >>> print(error)  # "Unmatched opening brace at position 6"
    """
    brace_count = 0
    in_placeholder = False

    for i, char in enumerate(template):
        if char == '{':
            if in_placeholder:
                # Nested braces are not allowed
                return False, f"Unmatched nested opening brace at position {i}"
            brace_count += 1
            if brace_count == 1:
                in_placeholder = True
        elif char == '}':
            if brace_count == 0:
                return False, f"Unmatched closing brace at position {i}"
            brace_count -= 1
            if brace_count == 0:
                in_placeholder = False

    if brace_count > 0:
        # Find the position of the unmatched opening brace
        for i, char in enumerate(template):
            if char == '{':
                brace_count -= 1
                if brace_count == 0:
                    return False, f"Unmatched opening brace at position {i}"

    return True, ""


def recursive_format(template: str, context: Dict[str, Any], max_iterations: int = 5) -> str:
    """Recursively format a template until no more substitutions are possible.

    This function repeatedly applies formatting to handle cases where template
    variables themselves contain template syntax.

    Args:
        template: Template string to format
        context: Dictionary of values for formatting
        max_iterations: Maximum number of formatting iterations to prevent infinite loops

    Returns:
        Fully formatted string

    Raises:
        ValueError: If maximum iterations exceeded

    Example:
        >>> context = {
        ...     "name": "Alice",
        ...     "greeting": "Hello {name}",
        ...     "message": "{greeting}, welcome!"
        ... }
        >>> result = recursive_format("{message}", context)
        >>> print(result)  # "Hello Alice, welcome!"
    """
    result = template

    for _iteration in range(max_iterations):
        prev_result = result
        formatted, missing_keys = format_with_missing_keys(result, **context)
        result = formatted

        # If no changes occurred, we're done
        if result == prev_result:
            return result

    # One more attempt after max_iterations
    formatted, missing_keys = format_with_missing_keys(result, **context)
    if formatted == result:
        return result

    raise ValueError(f"Maximum formatting iterations ({max_iterations}) exceeded")
