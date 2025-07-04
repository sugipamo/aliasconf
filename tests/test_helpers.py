"""
Tests for aliasconf.utils.helpers module.

Following TDD principles with comprehensive test coverage.
"""

import pytest

from aliasconf.exceptions.errors import ConfigValidationError
from aliasconf.utils.helpers import (
    deep_merge_dicts,
    flatten_dict,
    is_template_string,
    normalize_path,
    safe_get_nested,
    unflatten_dict,
    validate_aliases,
    validate_config_structure,
)


class TestDeepMergeDicts:
    """Test cases for deep_merge_dicts function."""

    def test_merge_simple_dicts(self):
        """Test merging two simple dictionaries."""
        base = {"a": 1, "b": 2}
        overlay = {"b": 3, "c": 4}
        result = deep_merge_dicts(base, overlay)
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_merge_nested_dicts(self):
        """Test merging nested dictionaries."""
        base = {"a": {"x": 1, "y": 2}, "b": 3}
        overlay = {"a": {"y": 20, "z": 30}, "c": 4}
        result = deep_merge_dicts(base, overlay)
        assert result == {"a": {"x": 1, "y": 20, "z": 30}, "b": 3, "c": 4}

    def test_merge_empty_base(self):
        """Test merging with empty base dictionary."""
        base = {}
        overlay = {"a": 1, "b": 2}
        result = deep_merge_dicts(base, overlay)
        assert result == {"a": 1, "b": 2}

    def test_merge_empty_overlay(self):
        """Test merging with empty overlay dictionary."""
        base = {"a": 1, "b": 2}
        overlay = {}
        result = deep_merge_dicts(base, overlay)
        assert result == {"a": 1, "b": 2}

    def test_overlay_replaces_non_dict_values(self):
        """Test that overlay completely replaces non-dict values."""
        base = {"a": {"x": 1}, "b": {"y": 2}}
        overlay = {"a": "string", "b": 123}
        result = deep_merge_dicts(base, overlay)
        assert result == {"a": "string", "b": 123}

    def test_deep_nested_merge(self):
        """Test merging deeply nested structures."""
        base = {"a": {"b": {"c": {"d": 1}}}}
        overlay = {"a": {"b": {"c": {"e": 2}}}}
        result = deep_merge_dicts(base, overlay)
        assert result == {"a": {"b": {"c": {"d": 1, "e": 2}}}}

    def test_merge_with_none_values(self):
        """Test merging with None values."""
        base = {"a": 1, "b": None}
        overlay = {"b": 2, "c": None}
        result = deep_merge_dicts(base, overlay)
        assert result == {"a": 1, "b": 2, "c": None}

    def test_merge_with_lists(self):
        """Test that lists are replaced, not merged."""
        base = {"a": [1, 2, 3]}
        overlay = {"a": [4, 5]}
        result = deep_merge_dicts(base, overlay)
        assert result == {"a": [4, 5]}


class TestNormalizePath:
    """Test cases for normalize_path function."""

    def test_string_path_with_dots(self):
        """Test normalizing string path with dots."""
        assert normalize_path("python.timeout") == ["python", "timeout"]
        assert normalize_path("a.b.c.d") == ["a", "b", "c", "d"]

    def test_single_element_path(self):
        """Test normalizing single element path."""
        assert normalize_path("python") == ["python"]

    def test_list_path(self):
        """Test normalizing list path."""
        assert normalize_path(["python", "timeout"]) == ["python", "timeout"]

    def test_tuple_path(self):
        """Test normalizing tuple path."""
        assert normalize_path(("python", "timeout")) == ["python", "timeout"]

    def test_path_with_integers(self):
        """Test normalizing path with integers."""
        assert normalize_path(["items", 0, "name"]) == ["items", "0", "name"]

    def test_path_with_spaces(self):
        """Test normalizing path with spaces."""
        assert normalize_path("  python  .  timeout  ") == ["python", "timeout"]
        assert normalize_path(["  python  ", "  timeout  "]) == ["python", "timeout"]

    def test_empty_string_path_raises_error(self):
        """Test that empty string path raises error."""
        with pytest.raises(ConfigValidationError, match="Path cannot be empty string"):
            normalize_path("")

        with pytest.raises(ConfigValidationError, match="Path cannot be empty string"):
            normalize_path("   ")

    def test_empty_list_path_raises_error(self):
        """Test that empty list path raises error."""
        with pytest.raises(ConfigValidationError, match="Path cannot be empty"):
            normalize_path([])

        with pytest.raises(ConfigValidationError, match="Path cannot be empty"):
            normalize_path(())

    def test_path_starting_with_dot_raises_error(self):
        """Test that path starting with dot raises error."""
        with pytest.raises(ConfigValidationError, match="Path cannot start with a dot"):
            normalize_path(".python.timeout")

    def test_path_ending_with_dot_raises_error(self):
        """Test that path ending with dot raises error."""
        with pytest.raises(ConfigValidationError, match="Path cannot end with a dot"):
            normalize_path("python.timeout.")

    def test_path_with_double_dots_raises_error(self):
        """Test that path with double dots raises error."""
        with pytest.raises(
            ConfigValidationError, match="Path cannot contain empty components"
        ):
            normalize_path("python..timeout")

    def test_list_with_empty_string_raises_error(self):
        """Test that list with empty string raises error."""
        with pytest.raises(ConfigValidationError, match="Path parts cannot be empty"):
            normalize_path(["python", "", "timeout"])

        with pytest.raises(ConfigValidationError, match="Path parts cannot be empty"):
            normalize_path(["python", "   ", "timeout"])

    def test_invalid_path_type_raises_error(self):
        """Test that invalid path type raises error."""
        with pytest.raises(ConfigValidationError, match="Invalid path type"):
            normalize_path(123)

        with pytest.raises(ConfigValidationError, match="Invalid path type"):
            normalize_path({"key": "value"})

    def test_list_with_invalid_type_raises_error(self):
        """Test that list with invalid type raises error."""
        with pytest.raises(
            ConfigValidationError, match="Path parts must be strings or integers"
        ):
            normalize_path(["python", None, "timeout"])

        with pytest.raises(
            ConfigValidationError, match="Path parts must be strings or integers"
        ):
            normalize_path(["python", {"key": "value"}, "timeout"])


class TestValidateAliases:
    """Test cases for validate_aliases function."""

    def test_valid_aliases_list(self):
        """Test validating valid aliases list."""
        assert validate_aliases(["py", "python3"]) == ["py", "python3"]
        assert validate_aliases(["alias1", "alias2", "alias3"]) == [
            "alias1",
            "alias2",
            "alias3",
        ]

    def test_aliases_with_spaces_stripped(self):
        """Test that aliases with spaces are stripped."""
        assert validate_aliases(["  py  ", "  python3  "]) == ["py", "python3"]

    def test_non_list_aliases_raises_error(self):
        """Test that non-list aliases raises error."""
        with pytest.raises(ConfigValidationError, match="Aliases must be a list"):
            validate_aliases("py")

        with pytest.raises(ConfigValidationError, match="Aliases must be a list"):
            validate_aliases({"alias": "py"})

        with pytest.raises(ConfigValidationError, match="Aliases must be a list"):
            validate_aliases(123)

    def test_empty_aliases_list_raises_error(self):
        """Test that empty aliases list raises error."""
        with pytest.raises(ConfigValidationError, match="Aliases list cannot be empty"):
            validate_aliases([])

    def test_non_string_alias_raises_error(self):
        """Test that non-string alias raises error."""
        with pytest.raises(ConfigValidationError, match="Each alias must be a string"):
            validate_aliases(["py", 123, "python3"])

        with pytest.raises(ConfigValidationError, match="Each alias must be a string"):
            validate_aliases(["py", None, "python3"])

    def test_empty_string_alias_raises_error(self):
        """Test that empty string alias raises error."""
        with pytest.raises(
            ConfigValidationError, match="Aliases cannot be empty strings"
        ):
            validate_aliases(["py", "", "python3"])

        with pytest.raises(
            ConfigValidationError, match="Aliases cannot be empty strings"
        ):
            validate_aliases(["py", "   ", "python3"])

    def test_duplicate_alias_raises_error(self):
        """Test that duplicate alias raises error."""
        with pytest.raises(ConfigValidationError, match="Duplicate alias found: py"):
            validate_aliases(["py", "python3", "py"])


class TestIsTemplateString:
    """Test cases for is_template_string function."""

    def test_string_with_template(self):
        """Test strings containing template placeholders."""
        assert is_template_string("Hello {name}") is True
        assert is_template_string("Path: {base_dir}/{file}") is True
        assert is_template_string("{start} middle {end}") is True

    def test_string_without_template(self):
        """Test strings without template placeholders."""
        assert is_template_string("Hello world") is False
        assert is_template_string("No templates here") is False
        assert is_template_string("") is False

    def test_string_with_invalid_template_syntax(self):
        """Test strings with invalid template syntax."""
        assert is_template_string("Hello {") is False
        assert is_template_string("Hello }") is False
        assert is_template_string("Hello {}") is False
        assert is_template_string("Hello {123}") is True  # Numbers are valid in \w+
        assert is_template_string("Hello {-name}") is False

    def test_string_with_multiple_templates(self):
        """Test strings with multiple template placeholders."""
        assert is_template_string("{greeting} {name}, welcome to {place}") is True


class TestFlattenDict:
    """Test cases for flatten_dict function."""

    def test_flatten_simple_dict(self):
        """Test flattening a simple dictionary."""
        data = {"a": 1, "b": 2, "c": 3}
        result = flatten_dict(data)
        assert result == {"a": 1, "b": 2, "c": 3}

    def test_flatten_nested_dict(self):
        """Test flattening a nested dictionary."""
        data = {"a": {"b": {"c": 1}, "d": 2}, "e": 3}
        result = flatten_dict(data)
        assert result == {"a.b.c": 1, "a.d": 2, "e": 3}

    def test_flatten_empty_dict(self):
        """Test flattening an empty dictionary."""
        assert flatten_dict({}) == {}

    def test_flatten_with_custom_separator(self):
        """Test flattening with custom separator."""
        data = {"a": {"b": 1}, "c": {"d": 2}}
        result = flatten_dict(data, separator="/")
        assert result == {"a/b": 1, "c/d": 2}

    def test_flatten_with_parent_key(self):
        """Test flattening with parent key prefix."""
        data = {"a": 1, "b": {"c": 2}}
        result = flatten_dict(data, parent_key="root")
        assert result == {"root.a": 1, "root.b.c": 2}

    def test_flatten_with_mixed_types(self):
        """Test flattening with mixed value types."""
        data = {
            "str": "value",
            "int": 123,
            "list": [1, 2, 3],
            "nested": {"bool": True, "none": None},
        }
        result = flatten_dict(data)
        assert result == {
            "str": "value",
            "int": 123,
            "list": [1, 2, 3],
            "nested.bool": True,
            "nested.none": None,
        }

    def test_flatten_deeply_nested(self):
        """Test flattening deeply nested structure."""
        data = {"a": {"b": {"c": {"d": {"e": 1}}}}}
        result = flatten_dict(data)
        assert result == {"a.b.c.d.e": 1}


class TestUnflattenDict:
    """Test cases for unflatten_dict function."""

    def test_unflatten_simple_dict(self):
        """Test unflattening a simple dictionary."""
        data = {"a": 1, "b": 2, "c": 3}
        result = unflatten_dict(data)
        assert result == {"a": 1, "b": 2, "c": 3}

    def test_unflatten_compound_keys(self):
        """Test unflattening dictionary with compound keys."""
        data = {"a.b.c": 1, "a.d": 2, "e": 3}
        result = unflatten_dict(data)
        assert result == {"a": {"b": {"c": 1}, "d": 2}, "e": 3}

    def test_unflatten_empty_dict(self):
        """Test unflattening an empty dictionary."""
        assert unflatten_dict({}) == {}

    def test_unflatten_with_custom_separator(self):
        """Test unflattening with custom separator."""
        data = {"a/b": 1, "c/d": 2}
        result = unflatten_dict(data, separator="/")
        assert result == {"a": {"b": 1}, "c": {"d": 2}}

    def test_unflatten_with_mixed_types(self):
        """Test unflattening with mixed value types."""
        data = {
            "str": "value",
            "int": 123,
            "list": [1, 2, 3],
            "nested.bool": True,
            "nested.none": None,
        }
        result = unflatten_dict(data)
        assert result == {
            "str": "value",
            "int": 123,
            "list": [1, 2, 3],
            "nested": {"bool": True, "none": None},
        }

    def test_unflatten_deeply_nested(self):
        """Test unflattening to deeply nested structure."""
        data = {"a.b.c.d.e": 1}
        result = unflatten_dict(data)
        assert result == {"a": {"b": {"c": {"d": {"e": 1}}}}}

    def test_unflatten_overlapping_paths(self):
        """Test unflattening with overlapping paths."""
        # This test exposes a limitation in unflatten_dict:
        # It cannot handle paths where a value is both a leaf and a branch
        data = {"a.b": 1, "a.b.c": 2}
        with pytest.raises(TypeError):
            # This will fail because a.b is set to 1 first,
            # then we try to add a.b.c which requires a.b to be a dict
            unflatten_dict(data)


class TestSafeGetNested:
    """Test cases for safe_get_nested function."""

    def test_get_existing_value(self):
        """Test getting existing value from nested dict."""
        data = {"a": {"b": {"c": 42}}}
        assert safe_get_nested(data, "a.b.c") == 42
        assert safe_get_nested(data, ["a", "b", "c"]) == 42

    def test_get_non_existing_value_returns_default(self):
        """Test getting non-existing value returns default."""
        data = {"a": {"b": {"c": 42}}}
        assert safe_get_nested(data, "a.b.x") is None
        assert safe_get_nested(data, "a.b.x", "default") == "default"
        assert safe_get_nested(data, "x.y.z", 123) == 123

    def test_get_from_empty_dict(self):
        """Test getting from empty dict returns default."""
        assert safe_get_nested({}, "a.b.c") is None
        assert safe_get_nested({}, "a", "default") == "default"

    def test_get_with_non_dict_intermediate(self):
        """Test getting when intermediate value is not a dict."""
        data = {"a": "not a dict"}
        assert safe_get_nested(data, "a.b.c") is None
        assert safe_get_nested(data, "a.b.c", "default") == "default"

    def test_get_with_none_intermediate(self):
        """Test getting when intermediate value is None."""
        data = {"a": {"b": None}}
        assert safe_get_nested(data, "a.b.c") is None
        assert safe_get_nested(data, "a.b.c", "default") == "default"

    def test_get_with_invalid_path(self):
        """Test getting with invalid path returns default."""
        data = {"a": {"b": {"c": 42}}}
        # Invalid path types are handled gracefully
        assert safe_get_nested(data, "") is None
        assert safe_get_nested(data, None, "default") == "default"

    def test_get_direct_value(self):
        """Test getting direct value without nesting."""
        data = {"key": "value"}
        assert safe_get_nested(data, "key") == "value"
        assert safe_get_nested(data, ["key"]) == "value"

    def test_type_error_returns_default(self):
        """Test that TypeError returns default value."""
        # Pass non-dict as data
        assert safe_get_nested("not a dict", "a.b.c", "default") == "default"
        assert safe_get_nested(None, "a.b.c", "default") == "default"


class TestValidateConfigStructure:
    """Test cases for validate_config_structure function."""

    def test_valid_config_dict(self):
        """Test validating valid configuration dictionary."""
        # Should not raise any exception
        validate_config_structure({"key": "value"})
        validate_config_structure({"a": 1, "b": {"c": 2}})

    def test_empty_dict_with_allow_empty(self):
        """Test validating empty dict when allowed."""
        # Should not raise any exception
        validate_config_structure({}, allow_empty=True)

    def test_none_config_raises_error(self):
        """Test that None config raises error."""
        with pytest.raises(
            ConfigValidationError, match="Configuration data cannot be None"
        ):
            validate_config_structure(None)

    def test_non_dict_config_raises_error(self):
        """Test that non-dict config raises error."""
        with pytest.raises(
            ConfigValidationError, match="Configuration must be a dictionary"
        ):
            validate_config_structure("not a dict")

        with pytest.raises(
            ConfigValidationError, match="Configuration must be a dictionary"
        ):
            validate_config_structure([1, 2, 3])

        with pytest.raises(
            ConfigValidationError, match="Configuration must be a dictionary"
        ):
            validate_config_structure(123)

    def test_empty_dict_without_allow_empty_raises_error(self):
        """Test that empty dict raises error when not allowed."""
        with pytest.raises(
            ConfigValidationError, match="Configuration cannot be empty"
        ):
            validate_config_structure({})

    def test_reserved_keys_raise_error(self):
        """Test that reserved keys raise error."""
        with pytest.raises(
            ConfigValidationError, match="Configuration key '.*' is reserved"
        ):
            validate_config_structure({"__aliasconf_internal__": "value"})

        with pytest.raises(
            ConfigValidationError, match="Configuration key '.*' is reserved"
        ):
            validate_config_structure({"__meta__": "value"})

    def test_non_string_keys_raise_error(self):
        """Test that non-string keys raise error."""
        with pytest.raises(
            ConfigValidationError, match="Configuration keys must be strings"
        ):
            validate_config_structure({123: "value"})

        with pytest.raises(
            ConfigValidationError, match="Configuration keys must be strings"
        ):
            validate_config_structure({None: "value"})

    def test_empty_string_keys_raise_error(self):
        """Test that empty string keys raise error."""
        with pytest.raises(
            ConfigValidationError, match="Configuration keys cannot be empty strings"
        ):
            validate_config_structure({"": "value"})

        with pytest.raises(
            ConfigValidationError, match="Configuration keys cannot be empty strings"
        ):
            validate_config_structure({"   ": "value"})

    def test_nested_structure_validation(self):
        """Test validating nested configuration structure."""
        # Valid nested structure should pass
        config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {"username": "test_user", "password": "test_pass"},
            },
            "cache": {"enabled": True, "ttl": 3600},
        }
        validate_config_structure(config)  # Should not raise
