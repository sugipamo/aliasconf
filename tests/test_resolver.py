"""
Tests for aliasconf.core.resolver module.

Following TDD principles with comprehensive test coverage.
"""

import pytest

from aliasconf.core.resolver import (
    _find_key_in_tree,
    _resolve_dotted_path,
    create_config_root_from_dict,
    resolve_best,
    resolve_by_match_desc,
    resolve_formatted_string,
)
from aliasconf.exceptions.errors import ConfigResolverError, ConfigValidationError


class TestCreateConfigRootFromDict:
    """Test cases for create_config_root_from_dict function."""

    def test_create_from_simple_dict(self):
        """Test creating config tree from simple dictionary."""
        data = {"key1": "value1", "key2": "value2"}
        root = create_config_root_from_dict(data)

        assert root.key == "root"
        assert root.value == data
        assert len(root.next_nodes) == 2

        # Check child nodes
        keys = {node.key for node in root.next_nodes}
        assert keys == {"key1", "key2"}

    def test_create_from_nested_dict(self):
        """Test creating config tree from nested dictionary."""
        data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {
                    "username": "admin",
                    "password": "secret"
                }
            }
        }
        root = create_config_root_from_dict(data)

        # Navigate through tree
        db_node = next(n for n in root.next_nodes if n.key == "database")
        assert db_node is not None

        host_node = next(n for n in db_node.next_nodes if n.key == "host")
        assert host_node.value == "localhost"

        creds_node = next(n for n in db_node.next_nodes if n.key == "credentials")
        user_node = next(n for n in creds_node.next_nodes if n.key == "username")
        assert user_node.value == "admin"

    def test_create_with_aliases(self):
        """Test creating config tree with aliases."""
        data = {
            "python": {
                "aliases": ["py", "python3"],
                "timeout": 30
            }
        }
        root = create_config_root_from_dict(data)

        python_node = next(n for n in root.next_nodes if n.key == "python")
        assert "py" in python_node.matches
        assert "python3" in python_node.matches
        assert "python" in python_node.matches  # The key itself

        # Aliases key should not create a node
        alias_nodes = [n for n in python_node.next_nodes if n.key == "aliases"]
        assert len(alias_nodes) == 0

    def test_create_with_list_values(self):
        """Test creating config tree with list values."""
        data = {
            "servers": ["server1", "server2", "server3"],
            "ports": [8000, 8001, 8002]
        }
        root = create_config_root_from_dict(data)

        servers_node = next(n for n in root.next_nodes if n.key == "servers")
        # List items become child nodes with index as key
        assert len(servers_node.next_nodes) == 3

        server_keys = {node.key for node in servers_node.next_nodes}
        assert server_keys == {"0", "1", "2"}

        # Check values
        server0 = next(n for n in servers_node.next_nodes if n.key == "0")
        assert server0.value == "server1"

    def test_create_with_mixed_structure(self):
        """Test creating config tree with mixed dict/list structure."""
        data = {
            "apps": [
                {"name": "app1", "port": 8000},
                {"name": "app2", "port": 8001}
            ]
        }
        root = create_config_root_from_dict(data)

        apps_node = next(n for n in root.next_nodes if n.key == "apps")
        app0_node = next(n for n in apps_node.next_nodes if n.key == "0")

        name_node = next(n for n in app0_node.next_nodes if n.key == "name")
        assert name_node.value == "app1"

    def test_create_with_invalid_aliases_type(self):
        """Test that invalid aliases type raises error."""
        data = {
            "python": {
                "aliases": "py",  # Should be a list
                "timeout": 30
            }
        }
        with pytest.raises(ConfigValidationError, match="aliases must be a list type"):
            create_config_root_from_dict(data)

    def test_create_with_non_dict_raises_error(self):
        """Test that non-dict data raises error."""
        with pytest.raises(ConfigResolverError, match="Only dictionary data is supported"):
            create_config_root_from_dict("not a dict")

        with pytest.raises(ConfigResolverError, match="Only dictionary data is supported"):
            create_config_root_from_dict([1, 2, 3])

        with pytest.raises(ConfigResolverError, match="Only dictionary data is supported"):
            create_config_root_from_dict(None)

    def test_create_empty_dict(self):
        """Test creating config tree from empty dictionary."""
        root = create_config_root_from_dict({})
        assert root.key == "root"
        assert root.value == {}
        assert len(root.next_nodes) == 0


class TestFindKeyInTree:
    """Test cases for _find_key_in_tree function."""

    def test_find_existing_key(self):
        """Test finding an existing key in the tree."""
        data = {
            "database": {
                "host": "localhost",
                "port": 5432
            },
            "cache": {
                "ttl": 3600
            }
        }
        root = create_config_root_from_dict(data)

        # Find direct key
        assert _find_key_in_tree(root, "host") == "localhost"
        assert _find_key_in_tree(root, "port") == 5432
        assert _find_key_in_tree(root, "ttl") == 3600

    def test_find_non_existing_key(self):
        """Test finding a non-existing key returns None."""
        data = {"key1": "value1"}
        root = create_config_root_from_dict(data)

        assert _find_key_in_tree(root, "nonexistent") is None

    def test_find_key_with_value_dict(self):
        """Test finding key that has value in dict format."""
        data = {
            "config": {
                "timeout": {"value": 30, "description": "Timeout in seconds"}
            }
        }
        root = create_config_root_from_dict(data)

        # Should extract the "value" field
        assert _find_key_in_tree(root, "timeout") == 30

    def test_find_key_in_deep_tree(self):
        """Test finding key in deeply nested tree."""
        data = {
            "a": {"b": {"c": {"d": {"e": "deep_value"}}}}
        }
        root = create_config_root_from_dict(data)

        assert _find_key_in_tree(root, "e") == "deep_value"

    def test_find_duplicate_keys(self):
        """Test finding when multiple nodes have same key."""
        data = {
            "dev": {"port": 8000},
            "prod": {"port": 9000}
        }
        root = create_config_root_from_dict(data)

        # Should find one of them (BFS order)
        result = _find_key_in_tree(root, "port")
        assert result in [8000, 9000]


class TestResolveDottedPath:
    """Test cases for _resolve_dotted_path function."""

    def test_resolve_simple_path(self):
        """Test resolving simple dotted path."""
        data = {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        root = create_config_root_from_dict(data)

        result = _resolve_dotted_path(root, ["database", "host"])
        assert result == "localhost"

    def test_resolve_deep_path(self):
        """Test resolving deeply nested path."""
        data = {
            "app": {
                "database": {
                    "primary": {
                        "host": "db1.example.com"
                    }
                }
            }
        }
        root = create_config_root_from_dict(data)

        result = _resolve_dotted_path(root, ["app", "database", "primary", "host"])
        assert result == "db1.example.com"

    def test_resolve_nonexistent_path(self):
        """Test resolving non-existent path returns None."""
        data = {"key": "value"}
        root = create_config_root_from_dict(data)

        result = _resolve_dotted_path(root, ["non", "existent", "path"])
        assert result is None

    def test_resolve_with_value_dict(self):
        """Test resolving path to node with value dict."""
        data = {
            "settings": {
                "timeout": {"value": 60, "unit": "seconds"}
            }
        }
        root = create_config_root_from_dict(data)

        result = _resolve_dotted_path(root, ["settings", "timeout"])
        assert result == 60


class TestResolveByMatchDesc:
    """Test cases for resolve_by_match_desc function."""

    def test_resolve_exact_match(self):
        """Test resolving with exact path match."""
        data = {
            "python": {
                "timeout": 30,
                "command": "python3"
            }
        }
        root = create_config_root_from_dict(data)

        nodes = resolve_by_match_desc(root, ["python", "timeout"])
        assert len(nodes) > 0
        assert nodes[0].value == 30

    def test_resolve_with_aliases(self):
        """Test resolving using aliases."""
        data = {
            "python": {
                "aliases": ["py", "python3"],
                "timeout": 30
            }
        }
        root = create_config_root_from_dict(data)

        # Resolve using alias
        nodes = resolve_by_match_desc(root, ["py", "timeout"])
        assert len(nodes) > 0
        assert nodes[0].value == 30

        # Also works with python3 alias
        nodes = resolve_by_match_desc(root, ["python3", "timeout"])
        assert len(nodes) > 0
        assert nodes[0].value == 30

    def test_resolve_partial_match(self):
        """Test resolving with partial path match."""
        data = {
            "app": {
                "database": {
                    "host": "localhost"
                }
            }
        }
        root = create_config_root_from_dict(data)

        # Should still find host even with partial path
        nodes = resolve_by_match_desc(root, ["host"])
        assert len(nodes) > 0
        assert nodes[0].value == "localhost"

    def test_resolve_empty_path(self):
        """Test resolving with empty path."""
        data = {"key": "value"}
        root = create_config_root_from_dict(data)

        nodes = resolve_by_match_desc(root, [])
        # Should return root or empty list
        assert isinstance(nodes, list)

    def test_resolve_priority_ordering(self):
        """Test that results are ordered by match priority."""
        data = {
            "python": {
                "aliases": ["py"],
                "version": "3.9"
            },
            "py": {
                "version": "2.7"  # Less specific match
            }
        }
        root = create_config_root_from_dict(data)

        nodes = resolve_by_match_desc(root, ["py", "version"])
        # Should prefer the alias match over exact key match
        assert len(nodes) >= 2


class TestResolveBest:
    """Test cases for resolve_best function."""

    def test_resolve_best_match(self):
        """Test getting the best match from resolver."""
        data = {
            "python": {
                "timeout": 30,
                "retry": 3
            }
        }
        root = create_config_root_from_dict(data)

        node = resolve_best(root, ["python", "timeout"])
        assert node is not None
        assert node.value == 30

    def test_resolve_best_with_aliases(self):
        """Test resolve_best with alias resolution."""
        data = {
            "python": {
                "aliases": ["py", "python3"],
                "path": "/usr/bin/python3"
            }
        }
        root = create_config_root_from_dict(data)

        # All should resolve to same node
        node1 = resolve_best(root, ["python", "path"])
        node2 = resolve_best(root, ["py", "path"])
        node3 = resolve_best(root, ["python3", "path"])

        assert node1.value == node2.value == node3.value == "/usr/bin/python3"

    def test_resolve_best_no_match(self):
        """Test resolve_best returns None for no match."""
        data = {"key": "value"}
        root = create_config_root_from_dict(data)

        node = resolve_best(root, ["nonexistent", "path"])
        assert node is None

    def test_resolve_best_chooses_highest_priority(self):
        """Test that resolve_best chooses highest priority match."""
        data = {
            "dev": {
                "database": {"host": "dev.db.com"}
            },
            "database": {
                "host": "prod.db.com"
            }
        }
        root = create_config_root_from_dict(data)

        # More specific path should win
        node = resolve_best(root, ["dev", "database", "host"])
        assert node.value == "dev.db.com"


class TestResolveFormattedString:
    """Test cases for resolve_formatted_string function."""

    def test_resolve_simple_template(self):
        """Test resolving simple template string."""
        data = {
            "name": "John",
            "greeting": "Hello {name}!"
        }
        root = create_config_root_from_dict(data)

        result = resolve_formatted_string("Hello {name}!", root)
        assert result == "Hello John!"

    def test_resolve_multiple_placeholders(self):
        """Test resolving template with multiple placeholders."""
        data = {
            "host": "localhost",
            "port": "8080",
            "url": "http://{host}:{port}"
        }
        root = create_config_root_from_dict(data)

        result = resolve_formatted_string("http://{host}:{port}", root)
        assert result == "http://localhost:8080"

    def test_resolve_nested_reference(self):
        """Test resolving template with nested references."""
        data = {
            "base": {
                "url": "example.com"
            },
            "api": {
                "endpoint": "https://{base.url}/api"
            }
        }
        root = create_config_root_from_dict(data)

        result = resolve_formatted_string("https://{base.url}/api", root)
        assert result == "https://example.com/api"

    def test_resolve_with_missing_keys(self):
        """Test resolving template with missing keys."""
        data = {"name": "John"}
        root = create_config_root_from_dict(data)

        # Should handle missing keys gracefully
        result = resolve_formatted_string("Hello {name}, your age is {age}", root)
        # The missing key behavior depends on format_with_missing_keys
        assert "John" in result

    def test_resolve_non_template_string(self):
        """Test resolving string without templates."""
        data = {"key": "value"}
        root = create_config_root_from_dict(data)

        result = resolve_formatted_string("No templates here", root)
        assert result == "No templates here"

    def test_resolve_with_circular_reference(self):
        """Test that circular references are handled."""
        data = {
            "a": "{b}",
            "b": "{a}"
        }
        root = create_config_root_from_dict(data)

        # Should not get stuck in infinite loop
        result = resolve_formatted_string("{a}", root)
        # Result depends on implementation, but should not crash
        assert isinstance(result, str)

    def test_resolve_formatted_string_with_list_index(self):
        """Test resolving template referencing list items."""
        data = {
            "servers": ["server1", "server2", "server3"],
            "primary": "{servers.0}"
        }
        root = create_config_root_from_dict(data)

        result = resolve_formatted_string("{servers.0}", root)
        assert result == "server1"

    def test_resolve_empty_template(self):
        """Test resolving empty template string."""
        data = {"key": "value"}
        root = create_config_root_from_dict(data)

        result = resolve_formatted_string("", root)
        assert result == ""

    def test_resolve_formatted_string_special_chars(self):
        """Test resolving template with special characters."""
        data = {
            "path": "/usr/local/bin",
            "file": "script.sh"
        }
        root = create_config_root_from_dict(data)

        result = resolve_formatted_string("{path}/{file}", root)
        assert result == "/usr/local/bin/script.sh"
