"""
Cache implementation for AliasConf performance optimization.

This module provides caching mechanisms to improve performance for large
configurations and frequent access patterns.
"""

from collections import OrderedDict
from typing import Dict, Optional, Set, Tuple

from .node import ConfigNode


class PathIndex:
    """Index for fast path lookups.

    Maintains an index of all paths in the configuration tree for O(1) lookup
    instead of O(n) tree traversal.
    """

    def __init__(self) -> None:
        """Initialize path index."""
        self._index: Dict[Tuple[str, ...], ConfigNode] = {}
        self._alias_index: Dict[str, Set[Tuple[str, ...]]] = {}

    def build_index(self, root: ConfigNode, path: Tuple[str, ...] = ()) -> None:
        """Build index from configuration tree.

        Args:
            root: Root node to index
            path: Current path in tree (for recursion)
        """
        if root.key and root.key != "root":
            current_path = path + (root.key,)
            self._index[current_path] = root

            # Index aliases
            for alias in root.matches:
                if alias != root.key and alias != "*":
                    if alias not in self._alias_index:
                        self._alias_index[alias] = set()
                    self._alias_index[alias].add(current_path)

        # Recursively index children
        for child in root.next_nodes:
            child_path = path + (root.key,) if root.key and root.key != "root" else path
            self.build_index(child, child_path)

    def get_node(self, path: Tuple[str, ...]) -> Optional[ConfigNode]:
        """Get node by exact path.

        Args:
            path: Path to lookup

        Returns:
            ConfigNode if found, None otherwise
        """
        return self._index.get(path)

    def get_nodes_by_alias(self, alias: str) -> Set[Tuple[str, ...]]:
        """Get all paths that have the given alias.

        Args:
            alias: Alias to lookup

        Returns:
            Set of paths that have this alias
        """
        return self._alias_index.get(alias, set())

    def clear(self) -> None:
        """Clear the index."""
        self._index.clear()
        self._alias_index.clear()


class LRUCache:
    """LRU cache for resolved paths.

    Caches resolved paths to avoid repeated BFS traversals.
    """

    def __init__(self, max_size: int = 1000):
        """Initialize LRU cache.

        Args:
            max_size: Maximum number of entries to cache
        """
        self._cache: OrderedDict[Tuple[str, ...], Optional[ConfigNode]] = OrderedDict()
        self._max_size = max_size

    def get(self, path: Tuple[str, ...]) -> Optional[ConfigNode]:
        """Get cached node for path.

        Args:
            path: Path to lookup

        Returns:
            Cached node or None if not in cache
        """
        if path in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(path)
            return self._cache[path]
        return None

    def put(self, path: Tuple[str, ...], node: Optional[ConfigNode]) -> None:
        """Cache a resolved path.

        Args:
            path: Path that was resolved
            node: Node that was found (or None)
        """
        if path in self._cache:
            self._cache.move_to_end(path)
        else:
            self._cache[path] = node
            if len(self._cache) > self._max_size:
                # Remove least recently used
                self._cache.popitem(last=False)

    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()


class ConfigCache:
    """Combined caching system for AliasConf.

    Combines path indexing and LRU caching for optimal performance.
    """

    def __init__(self, lru_size: int = 1000):
        """Initialize config cache.

        Args:
            lru_size: Size of LRU cache
        """
        self.path_index = PathIndex()
        self.lru_cache = LRUCache(lru_size)
        self._initialized = False

    def initialize(self, root: ConfigNode) -> None:
        """Initialize cache from configuration tree.

        Args:
            root: Root node of configuration tree
        """
        self.path_index.build_index(root)
        self._initialized = True

    def clear(self) -> None:
        """Clear all caches."""
        self.path_index.clear()
        self.lru_cache.clear()
        self._initialized = False

    @property
    def is_initialized(self) -> bool:
        """Check if cache is initialized."""
        return self._initialized
