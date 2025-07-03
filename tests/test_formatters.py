"""
Tests for aliasconf.utils.formatters module.

Following TDD principles with comprehensive test coverage.
"""

import pytest

from aliasconf.utils.formatters import (
    format_with_missing_keys,
    recursive_format,
    validate_template_syntax,
)


class TestFormatWithMissingKeys:
    """Test cases for format_with_missing_keys function."""

    def test_format_simple_template(self):
        """Test formatting simple template with all keys present."""
        template = "Hello {name}, welcome!"
        result, missing = format_with_missing_keys(template, name="Alice")

        assert result == "Hello Alice, welcome!"
        assert missing == []

    def test_format_with_multiple_placeholders(self):
        """Test formatting with multiple placeholders."""
        template = "{greeting} {name}, you are {age} years old"
        result, missing = format_with_missing_keys(
            template,
            greeting="Hello",
            name="Bob",
            age=25,
        )

        assert result == "Hello Bob, you are 25 years old"
        assert missing == []

    def test_format_with_missing_keys(self):
        """Test formatting when some keys are missing."""
        template = "Hello {name}, your score is {score}"
        result, missing = format_with_missing_keys(template, name="Charlie")

        assert result == "Hello Charlie, your score is {score}"
        assert missing == ["score"]

    def test_format_with_all_keys_missing(self):
        """Test formatting when all keys are missing."""
        template = "{greeting} {name}!"
        result, missing = format_with_missing_keys(template)

        assert result == "{greeting} {name}!"
        assert set(missing) == {"greeting", "name"}

    def test_format_empty_template(self):
        """Test formatting empty template."""
        result, missing = format_with_missing_keys("", name="Test")

        assert result == ""
        assert missing == []

    def test_format_no_placeholders(self):
        """Test formatting template without placeholders."""
        template = "Hello world!"
        result, missing = format_with_missing_keys(template, name="Test")

        assert result == "Hello world!"
        assert missing == []

    def test_format_repeated_placeholders(self):
        """Test formatting with repeated placeholders."""
        template = "{name} meets {name} at {place}"
        result, missing = format_with_missing_keys(
            template,
            name="Alice",
            place="park",
        )

        assert result == "Alice meets Alice at park"
        assert missing == []

    def test_format_numeric_values(self):
        """Test formatting with numeric values."""
        template = "Count: {count}, Pi: {pi}"
        result, missing = format_with_missing_keys(
            template,
            count=42,
            pi=3.14159,
        )

        assert result == "Count: 42, Pi: 3.14159"
        assert missing == []

    def test_format_with_special_characters(self):
        """Test formatting with special characters in values."""
        template = "Path: {path}"
        result, missing = format_with_missing_keys(
            template,
            path="/usr/local/bin",
        )

        assert result == "Path: /usr/local/bin"
        assert missing == []

    def test_format_preserves_braces_without_keys(self):
        """Test that lone braces are preserved."""
        template = "Use {} for empty dict and {key} for value"
        result, missing = format_with_missing_keys(template, key="test")

        assert result == "Use {} for empty dict and test for value"
        assert missing == []


class TestValidateTemplateSyntax:
    """Test cases for validate_template_syntax function."""

    def test_validate_valid_template(self):
        """Test validating a valid template."""
        valid, error = validate_template_syntax("Hello {name}!")
        assert valid is True
        assert error == ""

    def test_validate_empty_template(self):
        """Test validating empty template."""
        valid, error = validate_template_syntax("")
        assert valid is True
        assert error == ""

    def test_validate_no_placeholders(self):
        """Test validating template without placeholders."""
        valid, error = validate_template_syntax("Hello world!")
        assert valid is True
        assert error == ""

    def test_validate_multiple_placeholders(self):
        """Test validating template with multiple placeholders."""
        valid, error = validate_template_syntax("{greeting} {name}, {message}")
        assert valid is True
        assert error == ""

    def test_validate_unmatched_opening_brace(self):
        """Test validating template with unmatched opening brace."""
        valid, error = validate_template_syntax("Hello {name")
        assert valid is False
        assert "Unmatched opening brace" in error
        assert "position 6" in error

    def test_validate_unmatched_closing_brace(self):
        """Test validating template with unmatched closing brace."""
        valid, error = validate_template_syntax("Hello name}")
        assert valid is False
        assert "Unmatched closing brace" in error
        assert "position 10" in error

    def test_validate_nested_braces(self):
        """Test validating template with nested braces."""
        valid, error = validate_template_syntax("Hello {{name}}")
        assert valid is False
        # Multiple unmatched braces
        assert "Unmatched" in error

    def test_validate_multiple_errors(self):
        """Test validating template with multiple brace errors."""
        valid, error = validate_template_syntax("{name}} is {{awesome")
        assert valid is False
        # Should report first error found
        assert "Unmatched" in error

    def test_validate_empty_placeholder(self):
        """Test validating template with empty placeholder."""
        # Empty placeholders are syntactically valid
        valid, error = validate_template_syntax("Hello {}")
        assert valid is True
        assert error == ""


class TestRecursiveFormat:
    """Test cases for recursive_format function."""

    def test_recursive_format_simple(self):
        """Test recursive formatting with simple template."""
        context = {"name": "Alice"}
        result = recursive_format("Hello {name}!", context)
        assert result == "Hello Alice!"

    def test_recursive_format_nested_templates(self):
        """Test recursive formatting with nested templates."""
        context = {
            "name": "Bob",
            "greeting": "Hello {name}",
            "message": "{greeting}, welcome!",
        }
        result = recursive_format("{message}", context)
        assert result == "Hello Bob, welcome!"

    def test_recursive_format_deep_nesting(self):
        """Test recursive formatting with deep nesting."""
        context = {"a": "final", "b": "{a}", "c": "{b}", "d": "{c}", "e": "{d}"}
        result = recursive_format("{e}", context)
        assert result == "final"

    def test_recursive_format_max_iterations(self):
        """Test that max iterations prevents infinite loops."""
        # Create circular reference
        context = {"a": "{b}", "b": "{a}"}

        with pytest.raises(ValueError, match="Maximum formatting iterations"):
            recursive_format("{a}", context, max_iterations=5)

    def test_recursive_format_partial_resolution(self):
        """Test recursive formatting with partial resolution."""
        context = {"greeting": "Hello {name}", "message": "{greeting}!"}
        result = recursive_format("{message}", context)
        # Should resolve what it can
        assert result == "Hello {name}!"

    def test_recursive_format_no_placeholders(self):
        """Test recursive formatting with no placeholders."""
        context = {"name": "Test"}
        result = recursive_format("Hello world!", context)
        assert result == "Hello world!"

    def test_recursive_format_empty_context(self):
        """Test recursive formatting with empty context."""
        result = recursive_format("{name} {age}", {})
        assert result == "{name} {age}"

    def test_recursive_format_mixed_types(self):
        """Test recursive formatting with mixed value types."""
        context = {
            "count": 42,
            "pi": 3.14,
            "flag": True,
            "message": "Count: {count}, Pi: {pi}, Flag: {flag}",
        }
        result = recursive_format("{message}", context)
        assert result == "Count: 42, Pi: 3.14, Flag: True"

    def test_recursive_format_custom_iterations(self):
        """Test recursive formatting with custom iteration limit."""
        context = {"a": "{b}", "b": "{c}", "c": "done"}
        # Should complete in 3 iterations
        result = recursive_format("{a}", context, max_iterations=3)
        assert result == "done"

        # Should fail with only 2 iterations
        with pytest.raises(ValueError):
            recursive_format("{a}", context, max_iterations=2)
