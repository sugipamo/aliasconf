"""
ConfigNode implementation for AliasConf.

This module provides the ConfigNode class which represents individual nodes
in the configuration tree. Each node can have multiple aliases and supports
hierarchical relationships with parent and child nodes.
"""

from collections import deque
from typing import TYPE_CHECKING, Any, List, Optional, Set

from ..exceptions.errors import ConfigNodeError, ConfigValidationError

if TYPE_CHECKING:
    pass


class ConfigNode:
    """A node in the configuration tree with alias support.

    Each ConfigNode represents a configuration item with:
    - A primary key
    - A value (which can be any type)
    - A set of aliases (alternative names)
    - Parent-child relationships

    The node supports hierarchical access patterns and efficient searching
    through the configuration tree using BFS algorithms.

    Attributes:
        key (str): The primary key for this configuration node
        value (Any): The configuration value stored in this node
        parent (Optional[ConfigNode]): Parent node in the hierarchy
        next_nodes (List[ConfigNode]): Child nodes
        matches (Set[str]): Set of keys that match this node (includes aliases)

    Example:
        >>> node = ConfigNode("python", {"timeout": 30})
        >>> node.matches.add("py")  # Add alias
        >>> node.matches.add("python3")  # Add another alias
        >>> print(node.matches)  # {"python", "py", "python3", "*"}
    """

    def __init__(self, key: str, value: Optional[Any]):
        """Initialize a new ConfigNode.

        Args:
            key: The primary key for this node
            value: The configuration value to store

        Note:
            The key and "*" are automatically added to the matches set.
        """
        self.key = key
        self.value = value
        self.parent: Optional[ConfigNode] = None
        self.next_nodes: List[ConfigNode] = []
        self.matches: Set[str] = {key, "*"}
        self.aliases: List[str] = []  # Store original aliases

    def __repr__(self) -> str:
        """Return a detailed string representation of the node."""
        return (
            f"ConfigNode("
            f"key={self.key!r}, "
            f"value={self.value!r}, "
            f"matches={self.matches!r}, "
            f"next_nodes={[x.key for x in self.next_nodes]}"
            f")"
        )

    def add_edge(self, to_node: "ConfigNode") -> None:
        """Add a child node to this node.

        Args:
            to_node: The child node to add

        Raises:
            ConfigNodeError: If the edge already exists
        """
        add_edge(self, to_node)

    def next_nodes_with_key(self, key: str) -> List["ConfigNode"]:
        """Get child nodes that match the given key.

        Args:
            key: The key to search for in child nodes

        Returns:
            List of child nodes whose matches set contains the key
        """
        return next_nodes_with_key(self, key)

    def path(self) -> List[str]:
        """Get the path from root to this node.

        Returns:
            List of keys representing the path from root to this node
        """
        return path(self)

    def find_nearest_key_node(self, key: str) -> Optional["ConfigNode"]:
        """Find the nearest node that matches the given key using BFS.

        Args:
            key: The key to search for

        Returns:
            The nearest node that matches the key, or None if not found
        """
        return find_nearest_key_node(self, key)


def init_matches(node: ConfigNode, value: Any) -> None:
    """Initialize the matches set for a node based on its value.

    If the value is a dictionary containing an "aliases" key with a list
    of strings, those aliases are added to the node's matches set.
    The "aliases" key is then removed from the value.

    Args:
        node: The ConfigNode to initialize
        value: The configuration value (potentially containing aliases)

    Raises:
        ConfigNodeError: If aliases is not a list type
    """
    if isinstance(value, dict) and "aliases" in value:
        aliases = value["aliases"]
        if not isinstance(aliases, list):
            raise ConfigValidationError(f"aliases must be a list type: {aliases}")
        for alias in aliases:
            if not isinstance(alias, str):
                raise ConfigValidationError(f"alias must be a string: {alias}")
            node.matches.add(alias)
        # Store the aliases in the node
        node.aliases = aliases[:]
        # Remove aliases from the value since it's processed
        if "aliases" in value:
            del value["aliases"]
    node.value = value


def add_edge(parent: ConfigNode, to_node: ConfigNode) -> None:
    """Add an edge from parent to child node.

    This establishes a parent-child relationship between two nodes.
    Prevents duplicate edges from being created.

    Args:
        parent: The parent node
        to_node: The child node

    Raises:
        ConfigNodeError: If the edge already exists
    """
    if to_node in parent.next_nodes:
        raise ConfigNodeError(f"Edge to '{to_node.key}' already exists")
    parent.next_nodes.append(to_node)
    to_node.parent = parent


def path(node: ConfigNode) -> List[str]:
    """Get the path from root to the given node.

    Traverses up the tree through parent relationships to build
    the complete path from root to the specified node.

    Args:
        node: The node to get the path for

    Returns:
        List of keys representing the path from root to node
    """
    path_list = []
    current = node
    while current:
        path_list.append(current.key)
        if not current.parent:
            break
        current = current.parent
    return path_list[::-1]


def next_nodes_with_key(node: ConfigNode, key: str) -> List[ConfigNode]:
    """Get child nodes that match the given key.

    Args:
        node: The parent node to search from
        key: The key to match against

    Returns:
        List of child nodes whose matches set contains the key
    """
    return [n for n in node.next_nodes if key in n.matches]


def find_nearest_key_node(node: ConfigNode, key: str) -> Optional[ConfigNode]:
    """Find the nearest node that matches the given key using BFS.

    Performs a breadth-first search to find the nearest node
    that has the given key in its matches set.

    Args:
        node: The starting node for the search
        key: The key to search for

    Returns:
        The nearest node that matches the key, or None if not found
    """
    queue = deque([(0, node)])
    visited = set()

    while queue:
        depth, current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)

        if key in current.matches:
            return current

        # Check parent if exists
        if current.parent and current.parent not in visited:
            queue.append((depth + 1, current.parent))

        # Check children
        for next_node in current.next_nodes:
            if next_node not in visited:
                queue.append((depth + 1, next_node))

    return None
