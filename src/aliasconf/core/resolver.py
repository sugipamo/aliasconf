"""
Configuration resolver for AliasConf.

This module provides functions for creating configuration trees from dictionaries
and resolving configuration values through the tree structure with alias support.
"""

from collections import deque
from typing import Any, Dict, List, Optional, Tuple, Union

from ..exceptions.errors import ConfigResolverError
from ..utils.formatters import format_with_missing_keys
from .node import ConfigNode, add_edge, init_matches


def _find_key_in_tree(root: ConfigNode, key: str) -> Optional[Any]:
    """Find a key anywhere in the configuration tree using BFS.

    Args:
        root: Root node to start search from
        key: Key to search for

    Returns:
        Value if found, None otherwise
    """
    queue = deque([root])
    visited = set()

    while queue:
        current = queue.popleft()
        if id(current) in visited:
            continue
        visited.add(id(current))

        if current.key == key:
            value = current.value
            if isinstance(value, dict) and "value" in value:
                return value["value"]
            elif value is not None:
                return value

        # Add parent and child nodes to search queue
        if current.parent:
            queue.append(current.parent)
        queue.extend(current.next_nodes)

    return None


def _resolve_dotted_path(root: ConfigNode, parts: List[str]) -> Optional[Any]:
    """Resolve a dotted path like 'base.url' from the root.

    Args:
        root: Root node to start from
        parts: Path components

    Returns:
        Value if found, None otherwise
    """
    # Try to resolve from root
    from ..utils.helpers import normalize_path

    normalized = normalize_path('.'.join(parts))
    node = resolve_best(root, normalized)
    if node:
        value = node.value
        if isinstance(value, dict) and "value" in value:
            return value["value"]
        elif value is not None:
            return value

    return None


def create_config_root_from_dict(data: Any) -> ConfigNode:
    """Create a configuration tree from a dictionary.

    Recursively processes the input data to build a tree of ConfigNode objects.
    Handles both dictionary and list structures, processing aliases along the way.

    Args:
        data: Dictionary or other data structure to convert to ConfigNode tree

    Returns:
        Root ConfigNode of the created tree

    Raises:
        ConfigResolverError: If data is not a dictionary type

    Example:
        >>> config_dict = {
        ...     "python": {
        ...         "aliases": ["py", "python3"],
        ...         "timeout": 30,
        ...         "command": "python {script}"
        ...     },
        ...     "database": {
        ...         "host": "localhost",
        ...         "port": 5432
        ...     }
        ... }
        >>> root = create_config_root_from_dict(config_dict)
        >>> print(root.key)  # "root"
    """
    if not isinstance(data, dict):
        raise ConfigResolverError("Only dictionary data is supported")

    root = ConfigNode('root', data)
    init_matches(root, data)
    queue = [(root, data)]

    while queue:
        parent, current_data = queue.pop()

        if isinstance(current_data, dict):
            # Handle aliases at this level if they exist
            if "aliases" in current_data:
                aliases = current_data["aliases"]
                if not isinstance(aliases, list):
                    raise ConfigResolverError(f"aliases must be a list type: {aliases}")
                for alias in aliases:
                    parent.matches.add(alias)

            # Process each key-value pair
            for key, value in current_data.items():
                if key == "aliases":
                    continue  # Already processed above

                # Create a copy of value to avoid modifying the original
                node_value = value.copy() if isinstance(value, dict) else value
                node = ConfigNode(key, node_value)
                init_matches(node, node_value)
                add_edge(parent, node)
                queue.append((node, node_value))

        elif isinstance(current_data, list):  # type: ignore[unreachable]
            # Handle list structures by using index as key
            for index, value in enumerate(current_data):
                node = ConfigNode(str(index), value)
                init_matches(node, value)
                add_edge(parent, node)
                queue.append((node, value))

    return root


def resolve_by_match_desc(root: ConfigNode, path: Union[List[str], Tuple[str, ...]]) -> List[ConfigNode]:
    """Resolve nodes by matching path with descending priority.

    Uses a sophisticated matching algorithm that assigns priority scores
    based on how well each node matches the given path.

    Args:
        root: Root node to start resolution from
        path: Path to resolve as list or tuple of strings

    Returns:
        List of nodes sorted by match priority (best matches first)

    Raises:
        ConfigResolverError: If path is not a list or tuple
    """
    if not isinstance(path, (list, tuple)):
        raise ConfigResolverError(f"Path must be a list or tuple: {path}")
    return _resolve_by_match_desc(root, tuple(path))


def resolve_best(root: ConfigNode, path: Union[List[str], Tuple[str, ...]]) -> Optional[ConfigNode]:
    """Resolve the best matching config node for given path.

    Returns the single best matching node for the given path, or None if
    no matching node is found.

    Args:
        root: Root config node to start resolution from
        path: Path to resolve as list or tuple of strings

    Returns:
        Best matching config node, or None if no match found

    Example:
        >>> root = create_config_root_from_dict({
        ...     "python": {"aliases": ["py"], "timeout": 30}
        ... })
        >>> node = resolve_best(root, ["py", "timeout"])
        >>> print(node.value)  # 30
    """
    results = resolve_by_match_desc(root, path)
    return results[0] if results else None


def resolve_values(root: ConfigNode, path: Union[List[str], Tuple[str, ...]]) -> List[Any]:
    """Resolve values for all nodes matching the given path.

    Args:
        root: Root config node to start resolution from
        path: Path to resolve as list or tuple of strings

    Returns:
        List of values from all matching nodes
    """
    return [node.value for node in resolve_by_match_desc(root, path)]


def resolve_formatted_string(
    template: str,
    root: ConfigNode,
    initial_values: Optional[Dict[str, Any]] = None
) -> str:
    """Format a template string using values from the configuration tree.

    Searches the configuration tree to resolve {key} placeholders in the template
    string. Uses BFS to find values throughout the tree structure.

    Args:
        template: Template string with {key} placeholders to format
        root: Root of the configuration tree
        initial_values: Initial key-value pairs (user input, runtime values, etc.)

    Returns:
        Formatted string with placeholders replaced by configuration values

    Raises:
        ConfigResolverError: If initial_values is None

    Example:
        >>> root = create_config_root_from_dict({
        ...     "app": {"name": "MyApp"},
        ...     "message": "Welcome to {app_name}!"
        ... })
        >>> result = resolve_formatted_string(
        ...     "Welcome to {name}!",
        ...     root,
        ...     {"name": "MyApp"}
        ... )
        >>> print(result)  # "Welcome to MyApp!"
    """
    if initial_values is None:
        initial_values = {}

    # Build a complete context of all available values
    context = dict(initial_values)

    # Helper to collect all values from the config tree
    def collect_values(node: ConfigNode, path_parts: Optional[List[str]] = None) -> None:
        if path_parts is None:
            path_parts = []

        if node.key and node.key != "root":
            current_path = path_parts + [node.key]
            dotted_path = '.'.join(current_path)

            if isinstance(node.value, dict):
                # Process dictionary values
                if "value" in node.value:
                    context[dotted_path] = str(node.value["value"])
                # Process child nodes
                for child in node.next_nodes:
                    collect_values(child, current_path)
            elif isinstance(node.value, list):
                # Process list nodes - add children to context
                for child in node.next_nodes:
                    collect_values(child, current_path)
            elif isinstance(node.value, (str, int, float, bool)):
                context[dotted_path] = str(node.value)
        else:
            # Root node or nodes without keys
            for child in node.next_nodes:
                collect_values(child, path_parts)

    # Collect all values
    collect_values(root)

    # Use recursive formatting from formatters module
    from ..utils.formatters import recursive_format

    try:
        return recursive_format(template, context)
    except ValueError:
        # If max iterations exceeded, return the partially formatted result
        result = template
        for _ in range(5):
            formatted, _ = format_with_missing_keys(result, **context)
            if formatted == result:
                break
            result = formatted
        return result


def resolve_format_string(node: ConfigNode, initial_values: Optional[Dict[str, Any]] = None) -> str:
    """Format a string value from a specific node using configuration tree context.

    Extracts a string value from the node and formats it using values available
    in the configuration tree and initial values.

    Args:
        node: The ConfigNode containing the string to format
        initial_values: Initial key-value pairs for formatting

    Returns:
        Formatted string value

    Raises:
        ConfigResolverError: If initial_values is None
    """
    if initial_values is None:
        raise ConfigResolverError("initial_values cannot be None")

    # Extract string value from node
    if isinstance(node.value, str):
        template = node.value
    elif isinstance(node.value, dict) and "value" in node.value:
        value = node.value["value"]
        if isinstance(value, str):
            template = value
        else:
            return str(value)
    else:
        return str(node.value)

    key_values = dict(initial_values)
    formatted, missing_keys = format_with_missing_keys(template, **key_values)

    if not missing_keys:
        return formatted

    # Search for missing keys starting from this node
    queue = deque([node])
    visited = set()

    while queue and missing_keys:
        current = queue.popleft()
        if id(current) in visited:
            continue
        visited.add(id(current))

        for key in list(missing_keys):
            if key in key_values:
                continue
            if current.key == key:
                value = current.value
                if isinstance(value, dict) and "value" in value:
                    key_values[key] = value["value"]
                elif isinstance(value, (str, int)):
                    key_values[key] = value
                missing_keys.remove(key)

        # Search parent and child nodes
        if current.parent:
            queue.append(current.parent)
        queue.extend(current.next_nodes)

    formatted, _ = format_with_missing_keys(template, **key_values)
    return formatted


def _resolve_by_match_desc(root: ConfigNode, path: Tuple[str, ...]) -> List[ConfigNode]:
    """Internal function for resolving nodes by descending match priority.

    Implements a sophisticated matching algorithm that uses bit-shifting to
    create priority scores based on path position and match quality.

    Args:
        root: Root node to start search from
        path: Path tuple to match against

    Returns:
        List of nodes sorted by match priority (highest first)
    """
    if not path:
        return []

    # Fast path: direct traversal for exact matches
    # Disabled to ensure all matches are found
    # current = root
    # for i, component in enumerate(path):
    #     found = False
    #     for next_node in current.next_nodes:
    #         if component in next_node.matches:
    #             if i == len(path) - 1:
    #                 # Found exact match
    #                 return [next_node]
    #             current = next_node
    #             found = True
    #             break
    #     if not found:
    #         break  # Fall back to full search

    # Full search with priority scoring
    original_path = path
    results = []
    queue = [(path, 1, root)]
    visited = set()

    while queue:
        current_path, match_rank, node = queue.pop()
        if id(node) in visited:
            continue
        visited.add(id(node))

        for next_node in node.next_nodes:
            matched = False
            for i in range(len(current_path)):
                if current_path[i] in next_node.matches:
                    matched = True
                    # Calculate priority score using bit shifting
                    new_rank = match_rank + (1 << (len(original_path) - i))
                    remaining_path = current_path[i+1:]
                    queue.append((remaining_path, new_rank, next_node))
                    # Only add to results if this is the final path component
                    if not remaining_path:
                        results.append((new_rank, next_node))

            if not matched:
                queue.append((current_path, match_rank, next_node))

    # Sort by priority (highest first) and return nodes
    results.sort(key=lambda x: x[0], reverse=True)
    return [node for _, node in results]
