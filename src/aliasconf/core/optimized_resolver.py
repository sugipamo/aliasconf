"""
Optimized configuration resolver for AliasConf.

This module provides optimized resolution functions that use caching and
indexing for improved performance with large configurations.
"""

from typing import List, Optional, Tuple

from .cache import ConfigCache
from .node import ConfigNode

# Global cache instance
_global_cache = ConfigCache()


def _resolve_by_match_desc_optimized(
    root: ConfigNode,
    path: Tuple[str, ...],
    cache: Optional[ConfigCache] = None,
) -> List[ConfigNode]:
    """Optimized internal function for resolving nodes.

    Uses caching and direct path lookup for improved performance.

    Args:
        root: Root node to start search from
        path: Path tuple to match against
        cache: Optional cache instance (uses global if not provided)

    Returns:
        List of nodes sorted by match priority (highest first)
    """
    if not path:
        return []

    if cache is None:
        cache = _global_cache

    # Initialize cache if needed
    if not cache.is_initialized:
        cache.initialize(root)

    # Try direct path lookup first
    direct_node = cache.path_index.get_node(path)
    if direct_node:
        return [direct_node]

    # Try progressively shorter paths for partial matches
    results = []
    for i in range(len(path), 0, -1):
        partial_path = path[:i]
        node = cache.path_index.get_node(partial_path)
        if node:
            # Check if this node can resolve the remaining path
            remaining = path[i:]
            if not remaining:
                results.append((1 << len(path), node))
            else:
                # Try to resolve remaining path from this node
                child_results = _resolve_children_fast(
                    node, remaining, len(path) - i
                )
                results.extend(child_results)

    # Check aliases for the first component
    if path and not results:
        first_component = path[0]
        alias_paths = cache.path_index.get_nodes_by_alias(first_component)
        for alias_path in alias_paths:
            node = cache.path_index.get_node(alias_path)
            if node:
                if len(path) == 1:
                    # Direct alias match
                    results.append((1 << len(path), node))
                else:
                    # Try to resolve remaining path from this aliased node
                    remaining = path[1:]
                    child_results = _resolve_children_fast(node, remaining, 0)
                    results.extend(child_results)

    # Sort by priority (highest first) and return nodes
    results.sort(key=lambda x: x[0], reverse=True)
    return [node for _, node in results]


def _resolve_children_fast(
    parent: ConfigNode,
    remaining_path: Tuple[str, ...],
    base_priority: int,
) -> List[Tuple[int, ConfigNode]]:
    """Fast resolution of remaining path from a parent node.

    Args:
        parent: Parent node to start from
        remaining_path: Remaining path components to resolve
        base_priority: Base priority for scoring

    Returns:
        List of (priority, node) tuples
    """
    if not remaining_path:
        return []

    results = []
    current_nodes = [(parent, remaining_path, base_priority)]

    while current_nodes:
        node, path, priority = current_nodes.pop(0)

        if not path:
            continue

        component = path[0]
        remaining = path[1:]

        for child in node.next_nodes:
            if component in child.matches:
                new_priority = priority + (1 << len(remaining))
                if not remaining:
                    results.append((new_priority, child))
                else:
                    current_nodes.append((child, remaining, new_priority))

    return results


def resolve_best_optimized(
    root: ConfigNode,
    path: List[str],
    cache: Optional[ConfigCache] = None,
) -> Optional[ConfigNode]:
    """Optimized version of resolve_best using caching.

    Args:
        root: Root config node to start resolution from
        path: Path to resolve as list of strings
        cache: Optional cache instance

    Returns:
        Best matching config node, or None if no match found
    """
    if cache is None:
        cache = _global_cache

    # Check LRU cache first
    path_tuple = tuple(path)
    cached_result = cache.lru_cache.get(path_tuple)
    if cached_result is not None:
        return cached_result

    # Resolve using optimized algorithm
    results = _resolve_by_match_desc_optimized(root, path_tuple, cache)
    result = results[0] if results else None

    # Cache the result
    cache.lru_cache.put(path_tuple, result)

    return result


def clear_global_cache() -> None:
    """Clear the global cache.

    Should be called when configuration changes.
    """
    _global_cache.clear()
