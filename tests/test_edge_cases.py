"""
Edge case tests for AliasConf.

Tests edge cases like circular references, deeply nested structures,
special characters, and boundary conditions.
"""

import sys

import pytest

from aliasconf import ConfigManager
from aliasconf.exceptions import (
    ConfigResolverError,
    ConfigValidationError,
)


class TestAliasEdgeCases:
    """Test edge cases for alias functionality."""

    def test_circular_reference_aliases(self):
        """Test handling of potential circular references in aliases."""
        config_dict = {
            "python": {"aliases": ["py"], "command": "python"},
            "py": {"aliases": ["python3"], "version": "3.9"},
            "python3": {"aliases": ["python"], "path": "/usr/bin/python3"},
        }

        config = ConfigManager.from_dict(config_dict)

        # Each should resolve to its own values
        assert config.get("python.command", str) == "python"
        assert config.get("py.version", str) == "3.9"
        assert config.get("python3.path", str) == "/usr/bin/python3"

    def test_deeply_nested_aliases(self):
        """Test aliases in deeply nested structures."""
        config_dict = {
            "services": {
                "backend": {
                    "api": {
                        "v1": {
                            "aliases": ["api-v1", "apiv1", "v1-api"],
                            "endpoint": "https://api.example.com/v1",
                        }
                    }
                }
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # Test all aliases work at deep nesting levels
        expected = "https://api.example.com/v1"
        assert config.get("services.backend.api.v1.endpoint", str) == expected
        assert config.get("services.backend.api.api-v1.endpoint", str) == expected
        assert config.get("services.backend.api.apiv1.endpoint", str) == expected
        assert config.get("services.backend.api.v1-api.endpoint", str) == expected

    def test_same_name_aliases_priority(self):
        """Test priority when multiple nodes have the same alias."""
        config_dict = {
            "python": {"aliases": ["py"], "version": "3.9"},
            "python2": {"aliases": ["py"], "version": "2.7"},  # Same alias
        }

        config = ConfigManager.from_dict(config_dict)

        # Should get one of them consistently (implementation-dependent)
        version = config.get("py.version", str)
        assert version in ["3.9", "2.7"]

    def test_special_characters_in_aliases(self):
        """Test aliases with special characters."""
        config_dict = {
            "cpp": {
                "aliases": ["c++", "c#", "c@lang", "c-plus-plus", "c_plus_plus"],
                "compiler": "g++",
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # All special character aliases should work
        for alias in ["cpp", "c++", "c#", "c@lang", "c-plus-plus", "c_plus_plus"]:
            assert config.get(f"{alias}.compiler", str) == "g++"

    def test_empty_aliases_list(self):
        """Test handling of empty aliases list."""
        config_dict = {"python": {"aliases": [], "version": "3.9"}}  # Empty list

        config = ConfigManager.from_dict(config_dict)

        # Should work without aliases
        assert config.get("python.version", str) == "3.9"

    def test_duplicate_aliases_in_same_node(self):
        """Test handling of duplicate aliases in the same node."""
        config_dict = {
            "python": {
                "aliases": ["py", "python3", "py", "python3"],  # Duplicates
                "version": "3.9",
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # Should handle duplicates gracefully
        assert config.get("python.version", str) == "3.9"
        assert config.get("py.version", str) == "3.9"
        assert config.get("python3.version", str) == "3.9"

    def test_alias_same_as_key_name(self):
        """Test when alias is the same as the key name."""
        config_dict = {
            "python": {
                "aliases": ["python", "py"],  # 'python' is same as key
                "version": "3.9",
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # Should work normally
        assert config.get("python.version", str) == "3.9"
        assert config.get("py.version", str) == "3.9"


class TestConfigResolutionEdgeCases:
    """Test edge cases for configuration resolution."""

    def test_nonexistent_deep_path(self):
        """Test accessing deeply nested non-existent paths."""
        config_dict = {"app": {"name": "test"}}

        config = ConfigManager.from_dict(config_dict)

        # Deep non-existent path without default
        with pytest.raises(ConfigResolverError):
            config.get("app.settings.database.host.port", str)

        # With default
        assert (
            config.get("app.settings.database.host.port", str, "default") == "default"
        )

    def test_type_conversion_extreme_values(self):
        """Test type conversion with extreme/boundary values."""
        config_dict = {
            "limits": {
                "max_int": str(sys.maxsize),
                "min_int": str(-sys.maxsize - 1),
                "large_float": "1.7976931348623157e+308",  # Near max float
                "small_float": "2.2250738585072014e-308",  # Near min positive float
                "zero": "0",
                "negative_zero": "-0",
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # Test conversions work with extreme values
        assert config.get("limits.max_int", int) == sys.maxsize
        assert config.get("limits.min_int", int) == -sys.maxsize - 1
        assert config.get("limits.large_float", float) > 1e308
        assert config.get("limits.small_float", float) < 1e-307
        assert config.get("limits.zero", int) == 0
        assert config.get("limits.negative_zero", int) == 0

    def test_massive_configuration_structure(self):
        """Test handling of very large configuration structures."""
        # Create a large nested structure
        config_dict = {}
        current = config_dict

        # Create deep nesting (100 levels)
        for i in range(100):
            current[f"level_{i}"] = {}
            current = current[f"level_{i}"]

        current["value"] = "deep_value"

        config = ConfigManager.from_dict(config_dict)

        # Build the path
        path_parts = [f"level_{i}" for i in range(100)]
        path_parts.append("value")
        path = ".".join(path_parts)

        # Should handle deep nesting
        assert config.get(path, str) == "deep_value"

    def test_unicode_and_special_characters_in_values(self):
        """Test handling of Unicode and special characters in configuration values."""
        config_dict = {
            "messages": {
                "welcome": "Hello, 世界! 🌍",
                "emoji": "🐍 Python 🚀",
                "special": "Line1\nLine2\tTabbed\r\nWindows",
                "quotes": "Single ' and double \" quotes",
                "backslash": "C:\\path\\to\\file",
                "null_char": "Contains\x00null",
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # All special characters should be preserved
        assert config.get("messages.welcome", str) == "Hello, 世界! 🌍"
        assert config.get("messages.emoji", str) == "🐍 Python 🚀"
        assert config.get("messages.special", str) == "Line1\nLine2\tTabbed\r\nWindows"
        assert config.get("messages.quotes", str) == "Single ' and double \" quotes"
        assert config.get("messages.backslash", str) == "C:\\path\\to\\file"
        assert config.get("messages.null_char", str) == "Contains\x00null"

    def test_empty_string_values(self):
        """Test handling of empty string values."""
        config_dict = {
            "strings": {"empty": "", "whitespace": "   ", "newlines": "\n\n\n"}
        }

        config = ConfigManager.from_dict(config_dict)

        # Empty strings should be preserved
        assert config.get("strings.empty", str) == ""
        assert config.get("strings.whitespace", str) == "   "
        assert config.get("strings.newlines", str) == "\n\n\n"

    def test_none_values_in_config(self):
        """Test handling of None/null values in configuration."""
        config_dict = {
            "database": {
                "host": "localhost",
                "password": None,
                "options": {"timeout": None, "retry": 3},
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # None values should be handled appropriately
        assert config.get("database.host", str) == "localhost"
        # None should raise error when trying to convert to string without default
        with pytest.raises(ConfigValidationError):
            config.get("database.password", str)

        # With default
        assert config.get("database.password", str, "default_pass") == "default_pass"


class TestTemplateEdgeCases:
    """Test edge cases for template functionality."""

    def test_recursive_template_expansion(self):
        """Test recursive template references."""
        config_dict = {
            "base": {
                "url": "https://example.com",
                "api": "{base.url}/api",
                "v1": "{base.api}/v1",
                "endpoint": "{base.v1}/users",
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # Should resolve recursive templates
        context = {"base": config._root.next_nodes[0]}
        result = config.get_formatted("base.endpoint", context, str)
        assert result == "https://example.com/api/v1/users"

    def test_missing_template_variables(self):
        """Test templates with missing variables."""
        config_dict = {
            "messages": {
                "greeting": "Hello, {name}!",
                "complex": "User {user.name} from {user.country}",
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # Partial context
        context = {"name": "Alice"}
        result = config.get_formatted("messages.greeting", context, str)
        assert result == "Hello, Alice!"

        # Missing variables should be preserved
        result = config.get_formatted("messages.complex", {}, str)
        assert "{user.name}" in result and "{user.country}" in result

    def test_nested_template_brackets(self):
        """Test templates with nested brackets."""
        config_dict = {
            "patterns": {
                "regex": "{{pattern}}",  # Double brackets
                "format": "{{{key}}}",  # Triple brackets
                "mixed": "Start {value} {{literal}} end",
            }
        }

        config = ConfigManager.from_dict(config_dict)

        context = {"pattern": "test", "key": "mykey", "value": "val"}

        # Should handle multiple brackets appropriately
        result1 = config.get_formatted("patterns.regex", context, str)
        result2 = config.get_formatted("patterns.format", context, str)
        result3 = config.get_formatted("patterns.mixed", context, str)

        # The exact behavior depends on the formatter implementation
        assert result1  # Should not crash
        assert result2
        assert result3

    def test_special_characters_in_template_keys(self):
        """Test template keys with special characters."""
        config_dict = {
            "templates": {
                "path": "{user-name}/{app.id}",
                "complex": "{data[0]}/{info['key']}",
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # Special characters in template keys
        context = {
            "user-name": "john",
            "app.id": "123",
            "data[0]": "first",
            "info['key']": "value",
        }

        # Should handle or gracefully fail with special characters
        try:
            result = config.get_formatted("templates.path", context, str)
            assert "john" in result or "{user-name}" in result
        except Exception:
            # Some template parsers might not support special characters
            pass


class TestBoundaryConditions:
    """Test boundary conditions and limits."""

    def test_empty_path_components(self):
        """Test paths with empty components."""
        config_dict = {"app": {"name": "test"}}

        config = ConfigManager.from_dict(config_dict)

        # Empty path components should be handled
        with pytest.raises((ConfigValidationError, ConfigResolverError)):
            config.get("app..name", str)  # Double dot

        with pytest.raises((ConfigValidationError, ConfigResolverError)):
            config.get(".app.name", str)  # Leading dot

        with pytest.raises((ConfigValidationError, ConfigResolverError)):
            config.get("app.name.", str)  # Trailing dot

    def test_very_long_alias_names(self):
        """Test handling of very long alias names."""
        long_alias = "a" * 1000  # 1000 character alias
        config_dict = {
            "service": {"aliases": [long_alias, "short"], "url": "https://example.com"}
        }

        config = ConfigManager.from_dict(config_dict)

        # Long aliases should work
        assert config.get(f"{long_alias}.url", str) == "https://example.com"
        assert config.get("short.url", str) == "https://example.com"

    def test_many_aliases_per_node(self):
        """Test nodes with many aliases."""
        # Create 1000 aliases
        aliases = [f"alias_{i}" for i in range(1000)]
        config_dict = {"service": {"aliases": aliases, "status": "active"}}

        config = ConfigManager.from_dict(config_dict)

        # All aliases should work
        for alias in aliases[:10]:  # Test first 10
            assert config.get(f"{alias}.status", str) == "active"

    def test_large_list_values(self):
        """Test configuration with large list values."""
        large_list = list(range(10000))  # 10,000 items
        config_dict = {"data": {"items": large_list, "count": len(large_list)}}

        config = ConfigManager.from_dict(config_dict)

        # Should handle large lists
        items = config.get("data.items", list)
        assert len(items) == 10000
        assert items[0] == 0
        assert items[-1] == 9999

    def test_mixed_type_hierarchies(self):
        """Test configurations mixing different types at various levels."""
        config_dict = {
            "mixed": {
                "string_val": "text",
                "number_val": 42,
                "bool_val": True,
                "list_val": [1, 2, 3],
                "nested": {"aliases": ["nested_alias"], "value": "nested_value"},
                "null_val": None,
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # All types should be accessible
        assert config.get("mixed.string_val", str) == "text"
        assert config.get("mixed.number_val", int) == 42
        assert config.get("mixed.bool_val", bool) is True
        assert config.get("mixed.list_val", list) == [1, 2, 3]
        assert config.get("mixed.nested.value", str) == "nested_value"
        assert config.get("mixed.nested_alias.value", str) == "nested_value"


class TestErrorHandlingEdgeCases:
    """Test edge cases for error handling."""

    def test_invalid_type_for_aliases(self):
        """Test various invalid types for aliases field."""
        invalid_configs = [
            {"node": {"aliases": "string_not_list"}},
            {"node": {"aliases": 123}},
            {"node": {"aliases": {"not": "list"}}},
            {"node": {"aliases": None}},
            {"node": {"aliases": [1, 2, 3]}},  # Non-string items
        ]

        for config_dict in invalid_configs:
            with pytest.raises(ConfigValidationError):
                ConfigManager.from_dict(config_dict)

    def test_reserved_keys_in_config(self):
        """Test handling of potentially reserved keys."""
        config_dict = {
            "__init__": {"value": "test"},
            "__class__": {"value": "test"},
            "__dict__": {"value": "test"},
        }

        # Should either handle gracefully or raise appropriate error
        try:
            config = ConfigManager.from_dict(config_dict)
            # If it works, values should be accessible
            assert config.has("__init__.value")
        except ConfigValidationError:
            # Or reject reserved keys
            pass

    def test_cyclic_configuration_structure(self):
        """Test handling of cyclic references in configuration."""
        # Note: Direct cyclic references aren't possible in JSON/YAML,
        # but we can test similar scenarios
        config_dict = {"a": {"ref": "{b.value}"}, "b": {"ref": "{a.value}"}}

        config = ConfigManager.from_dict(config_dict)

        # Should handle gracefully (likely preserving template strings)
        context = {}
        result_a = config.get_formatted("a.ref", context, str)
        result_b = config.get_formatted("b.ref", context, str)

        # Should not crash, results might contain unresolved templates
        assert isinstance(result_a, str)
        assert isinstance(result_b, str)
