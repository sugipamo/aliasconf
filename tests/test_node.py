"""
Tests for aliasconf.core.node module.

Following TDD principles with comprehensive test coverage.
"""

import pytest

from aliasconf.core.node import (
    ConfigNode,
    add_edge,
    find_nearest_key_node,
    init_matches,
    next_nodes_with_key,
    path,
)
from aliasconf.exceptions.errors import ConfigNodeError, ConfigValidationError


class TestConfigNode:
    """Test cases for ConfigNode class."""

    def test_node_initialization(self):
        """Test basic node initialization."""
        node = ConfigNode("test_key", "test_value")

        assert node.key == "test_key"
        assert node.value == "test_value"
        assert node.parent is None
        assert node.next_nodes == []
        assert node.matches == {"test_key", "*"}
        assert node.aliases == []

    def test_node_with_dict_value(self):
        """Test node with dictionary value."""
        value = {"timeout": 30, "retry": 3}
        node = ConfigNode("config", value)

        assert node.key == "config"
        assert node.value == value
        assert node.value["timeout"] == 30

    def test_node_with_none_value(self):
        """Test node with None value."""
        node = ConfigNode("empty", None)

        assert node.key == "empty"
        assert node.value is None

    def test_node_repr(self):
        """Test node string representation."""
        node = ConfigNode("test", "value")
        child = ConfigNode("child", "child_value")
        node.next_nodes.append(child)

        repr_str = repr(node)
        assert "ConfigNode(" in repr_str
        assert "key='test'" in repr_str
        assert "value='value'" in repr_str
        assert "['child']" in repr_str

    def test_node_add_edge_method(self):
        """Test add_edge method on node."""
        parent = ConfigNode("parent", "parent_value")
        child = ConfigNode("child", "child_value")

        parent.add_edge(child)

        assert child in parent.next_nodes
        assert child.parent == parent

    def test_node_next_nodes_with_key_method(self):
        """Test next_nodes_with_key method."""
        parent = ConfigNode("parent", {})
        child1 = ConfigNode("config", "value1")
        child2 = ConfigNode("settings", "value2")

        parent.next_nodes.append(child1)
        parent.next_nodes.append(child2)
        child1.parent = parent
        child2.parent = parent

        # Add alias to child1
        child1.matches.add("conf")

        # Search by primary key
        nodes = parent.next_nodes_with_key("config")
        assert len(nodes) == 1
        assert nodes[0] == child1

        # Search by alias
        nodes = parent.next_nodes_with_key("conf")
        assert len(nodes) == 1
        assert nodes[0] == child1

        # Search for non-existent key
        nodes = parent.next_nodes_with_key("nonexistent")
        assert len(nodes) == 0

    def test_node_path_method(self):
        """Test path method returns correct path from root."""
        root = ConfigNode("root", {})
        level1 = ConfigNode("app", {})
        level2 = ConfigNode("database", {})
        level3 = ConfigNode("host", "localhost")

        add_edge(root, level1)
        add_edge(level1, level2)
        add_edge(level2, level3)

        path_list = level3.path()
        assert path_list == ["root", "app", "database", "host"]


class TestAddEdge:
    """Test cases for add_edge function."""

    def test_add_edge_basic(self):
        """Test adding edge between two nodes."""
        parent = ConfigNode("parent", {})
        child = ConfigNode("child", "value")

        add_edge(parent, child)

        assert child in parent.next_nodes
        assert child.parent == parent

    def test_add_edge_duplicate_raises_error(self):
        """Test adding duplicate edge raises error."""
        parent = ConfigNode("parent", {})
        child = ConfigNode("child", "value")

        add_edge(parent, child)

        with pytest.raises(ConfigNodeError, match="already exists"):
            add_edge(parent, child)

    def test_add_edge_maintains_references(self):
        """Test that edge maintains proper parent-child references."""
        parent = ConfigNode("parent", {})
        child1 = ConfigNode("child1", "value1")
        child2 = ConfigNode("child2", "value2")

        add_edge(parent, child1)
        add_edge(parent, child2)

        assert len(parent.next_nodes) == 2
        assert child1.parent == parent
        assert child2.parent == parent
        assert child1 in parent.next_nodes
        assert child2 in parent.next_nodes


class TestInitMatches:
    """Test cases for init_matches function."""

    def test_init_matches_with_aliases_list(self):
        """Test initializing matches with aliases list."""
        node = ConfigNode("python", {})
        value = {"aliases": ["py", "python3"], "timeout": 30}

        init_matches(node, value)

        assert "py" in node.matches
        assert "python3" in node.matches
        assert "python" in node.matches  # Original key
        assert "*" in node.matches  # Wildcard
        assert node.aliases == ["py", "python3"]

    def test_init_matches_without_aliases(self):
        """Test initializing matches without aliases."""
        node = ConfigNode("config", {})
        value = {"timeout": 30, "retry": 3}

        init_matches(node, value)

        # Should only have the original key and wildcard
        assert node.matches == {"config", "*"}
        assert node.aliases == []

    def test_init_matches_with_invalid_aliases_type(self):
        """Test that non-list aliases raises error."""
        node = ConfigNode("python", {})
        value = {"aliases": "py"}  # Should be a list

        with pytest.raises(ConfigValidationError, match="aliases must be a list type"):
            init_matches(node, value)

    def test_init_matches_with_empty_aliases_list(self):
        """Test initializing with empty aliases list."""
        node = ConfigNode("python", {})
        value = {"aliases": [], "timeout": 30}

        init_matches(node, value)

        assert node.matches == {"python", "*"}
        assert node.aliases == []

    def test_init_matches_with_non_dict_value(self):
        """Test initializing matches with non-dict value."""
        node = ConfigNode("key", {})

        # String value
        init_matches(node, "string_value")
        assert node.matches == {"key", "*"}

        # List value
        init_matches(node, [1, 2, 3])
        assert node.matches == {"key", "*"}

        # None value
        init_matches(node, None)
        assert node.matches == {"key", "*"}


class TestNextNodesWithKey:
    """Test cases for next_nodes_with_key function."""

    def test_next_nodes_with_exact_key_match(self):
        """Test finding nodes with exact key match."""
        parent = ConfigNode("parent", {})
        child1 = ConfigNode("config", "value1")
        child2 = ConfigNode("settings", "value2")
        child3 = ConfigNode("config", "value3")  # Duplicate key

        parent.next_nodes = [child1, child2, child3]

        nodes = next_nodes_with_key(parent, "config")
        assert len(nodes) == 2
        assert child1 in nodes
        assert child3 in nodes
        assert child2 not in nodes

    def test_next_nodes_with_alias_match(self):
        """Test finding nodes with alias match."""
        parent = ConfigNode("parent", {})
        child = ConfigNode("python", {"timeout": 30})
        child.matches.add("py")
        child.matches.add("python3")

        parent.next_nodes = [child]

        # All aliases should find the same node
        assert next_nodes_with_key(parent, "python") == [child]
        assert next_nodes_with_key(parent, "py") == [child]
        assert next_nodes_with_key(parent, "python3") == [child]

    def test_next_nodes_with_wildcard(self):
        """Test that wildcard matches all nodes."""
        parent = ConfigNode("parent", {})
        child1 = ConfigNode("config", "value1")
        child2 = ConfigNode("settings", "value2")

        parent.next_nodes = [child1, child2]

        nodes = next_nodes_with_key(parent, "*")
        assert len(nodes) == 2
        assert child1 in nodes
        assert child2 in nodes

    def test_next_nodes_with_no_matches(self):
        """Test finding nodes with no matches returns empty list."""
        parent = ConfigNode("parent", {})
        child = ConfigNode("config", "value")
        parent.next_nodes = [child]

        nodes = next_nodes_with_key(parent, "nonexistent")
        assert nodes == []


class TestPath:
    """Test cases for path function."""

    def test_path_single_node(self):
        """Test path for single node without parent."""
        node = ConfigNode("root", {})
        assert path(node) == ["root"]

    def test_path_two_levels(self):
        """Test path for two-level hierarchy."""
        parent = ConfigNode("parent", {})
        child = ConfigNode("child", "value")
        add_edge(parent, child)

        assert path(child) == ["parent", "child"]

    def test_path_deep_hierarchy(self):
        """Test path for deep hierarchy."""
        root = ConfigNode("root", {})
        level1 = ConfigNode("level1", {})
        level2 = ConfigNode("level2", {})
        level3 = ConfigNode("level3", {})
        level4 = ConfigNode("level4", "value")

        add_edge(root, level1)
        add_edge(level1, level2)
        add_edge(level2, level3)
        add_edge(level3, level4)

        assert path(level4) == ["root", "level1", "level2", "level3", "level4"]

    def test_path_with_special_keys(self):
        """Test path with special characters in keys."""
        parent = ConfigNode("app.config", {})
        child = ConfigNode("database-settings", {})
        grandchild = ConfigNode("connection_pool", "value")

        add_edge(parent, child)
        add_edge(child, grandchild)

        assert path(grandchild) == ["app.config", "database-settings", "connection_pool"]


class TestFindNearestKeyNode:
    """Test cases for find_nearest_key_node function."""

    def test_find_nearest_key_node_in_current(self):
        """Test finding key in current node."""
        node = ConfigNode("target", "value")

        result = find_nearest_key_node(node, "target")
        assert result == node

    def test_find_nearest_key_node_in_parent(self):
        """Test finding key in parent node."""
        parent = ConfigNode("parent", {})
        child = ConfigNode("child", "value")
        add_edge(parent, child)

        result = find_nearest_key_node(child, "parent")
        assert result == parent

    def test_find_nearest_key_node_in_sibling(self):
        """Test finding key in sibling node."""
        parent = ConfigNode("parent", {})
        child1 = ConfigNode("child1", "value1")
        child2 = ConfigNode("child2", "value2")
        add_edge(parent, child1)
        add_edge(parent, child2)

        result = find_nearest_key_node(child1, "child2")
        assert result == child2

    def test_find_nearest_key_node_not_found(self):
        """Test when key is not found returns None."""
        node = ConfigNode("test", "value")

        result = find_nearest_key_node(node, "nonexistent")
        assert result is None

    def test_find_nearest_key_node_with_alias(self):
        """Test finding node by alias."""
        parent = ConfigNode("parent", {})
        child = ConfigNode("python", "value")
        child.matches.add("py")
        add_edge(parent, child)

        result = find_nearest_key_node(parent, "py")
        assert result == child


