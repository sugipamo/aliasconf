"""
Basic tests for AliasConf functionality.

Tests core features like alias resolution, type conversion, and basic configuration access.
"""

import pytest

from aliasconf import ConfigManager
from aliasconf.exceptions import ConfigResolverError, ConfigValidationError


class TestBasicFunctionality:
    """Test basic AliasConf functionality."""

    def test_simple_config_creation(self):
        """Test creating a simple configuration."""
        config_dict = {"app": {"name": "TestApp", "version": "1.0.0"}}

        config = ConfigManager.from_dict(config_dict)

        assert config.get("app.name", str) == "TestApp"
        assert config.get("app.version", str) == "1.0.0"

    def test_alias_resolution(self):
        """Test that aliases work correctly."""
        config_dict = {
            "python": {
                "aliases": ["py", "python3"],
                "timeout": 30,
                "command": "python script.py",
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # All these should return the same value
        assert config.get("python.timeout", int) == 30
        assert config.get("py.timeout", int) == 30
        assert config.get("python3.timeout", int) == 30

        # Same for command
        expected_command = "python script.py"
        assert config.get("python.command", str) == expected_command
        assert config.get("py.command", str) == expected_command
        assert config.get("python3.command", str) == expected_command

    def test_type_conversion(self):
        """Test automatic type conversion."""
        config_dict = {
            "settings": {
                "timeout": "30",  # String that should convert to int
                "debug": "true",  # String that should convert to bool
                "ratio": "1.5",  # String that should convert to float
                "enabled": True,  # Already a bool
                "count": 42,  # Already an int
            }
        }

        config = ConfigManager.from_dict(config_dict)

        assert config.get("settings.timeout", int) == 30
        assert config.get("settings.debug", bool) is True
        assert config.get("settings.ratio", float) == 1.5
        assert config.get("settings.enabled", bool) is True
        assert config.get("settings.count", int) == 42

    def test_type_conversion_errors(self):
        """Test that invalid type conversions raise appropriate errors."""
        config_dict = {
            "settings": {"invalid_int": "not_a_number", "invalid_bool": "maybe"}
        }

        config = ConfigManager.from_dict(config_dict)

        with pytest.raises(ConfigValidationError):
            config.get("settings.invalid_int", int)

        with pytest.raises(ConfigValidationError):
            config.get("settings.invalid_bool", bool)

    def test_default_values(self):
        """Test default value handling."""
        config_dict = {"app": {"name": "TestApp"}}

        config = ConfigManager.from_dict(config_dict)

        # Existing value
        assert config.get("app.name", str) == "TestApp"

        # Non-existing value with default
        assert config.get("app.version", str, "0.1.0") == "0.1.0"
        assert config.get("app.debug", bool, False) is False
        assert config.get("app.timeout", int, 30) == 30

    def test_nested_configuration(self):
        """Test deeply nested configuration access."""
        config_dict = {
            "database": {
                "primary": {
                    "host": "localhost",
                    "port": 5432,
                    "credentials": {"username": "admin", "password": "secret"},
                }
            }
        }

        config = ConfigManager.from_dict(config_dict)

        assert config.get("database.primary.host", str) == "localhost"
        assert config.get("database.primary.port", int) == 5432
        assert config.get("database.primary.credentials.username", str) == "admin"
        assert config.get("database.primary.credentials.password", str) == "secret"

    def test_has_method(self):
        """Test the has() method for checking path existence."""
        config_dict = {"app": {"name": "TestApp", "settings": {"debug": True}}}

        config = ConfigManager.from_dict(config_dict)

        assert config.has("app.name") is True
        assert config.has("app.settings.debug") is True
        assert config.has("app.nonexistent") is False
        assert config.has("nonexistent.path") is False

    def test_multiple_aliases(self):
        """Test configuration with multiple aliases."""
        config_dict = {
            "cpp": {
                "aliases": ["c++", "cxx", "cplusplus"],
                "compiler": "g++",
                "flags": ["-std=c++17", "-Wall"],
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # Test all aliases work
        for alias in ["cpp", "c++", "cxx", "cplusplus"]:
            assert config.get(f"{alias}.compiler", str) == "g++"
            assert config.get(f"{alias}.flags", list) == ["-std=c++17", "-Wall"]

    def test_empty_configuration(self):
        """Test handling of empty configuration."""
        config = ConfigManager.from_dict({})

        assert config.has("any.path") is False
        assert config.get("any.path", str, "default") == "default"

        with pytest.raises(ConfigResolverError):
            config.get("any.path", str)  # No default provided

    def test_invalid_configuration_structure(self):
        """Test validation of configuration structure."""
        # Test non-dict data
        with pytest.raises(ConfigValidationError):
            ConfigManager.from_dict("not a dict")

        with pytest.raises(ConfigValidationError):
            ConfigManager.from_dict(None)

        with pytest.raises(ConfigValidationError):
            ConfigManager.from_dict([1, 2, 3])

    def test_invalid_aliases(self):
        """Test handling of invalid alias structures."""
        # Aliases must be a list
        config_dict = {
            "python": {
                "aliases": "not_a_list",  # Invalid: should be list
                "timeout": 30,
            }
        }

        with pytest.raises(ConfigValidationError):
            ConfigManager.from_dict(config_dict)

    def test_path_normalization(self):
        """Test different path input formats."""
        config_dict = {"app": {"name": "TestApp"}}

        config = ConfigManager.from_dict(config_dict)

        # Different path formats should all work
        assert config.get("app.name", str) == "TestApp"  # String path
        assert config.get(["app", "name"], str) == "TestApp"  # List path
        assert config.get(("app", "name"), str) == "TestApp"  # Tuple path


class TestConfigManagerMethods:
    """Test ConfigManager specific methods."""

    def test_to_dict(self):
        """Test converting configuration back to dictionary."""
        config_dict = {
            "app": {
                "aliases": ["application"],
                "name": "TestApp",
                "settings": {"debug": True},
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # Test with aliases included
        result_with_aliases = config.to_dict(include_aliases=True)
        assert "aliases" in result_with_aliases["app"]

        # Test with aliases excluded (default)
        result_without_aliases = config.to_dict()
        assert "aliases" not in result_without_aliases["app"]
        assert result_without_aliases["app"]["name"] == "TestApp"

    def test_cache_functionality(self):
        """Test that caching works correctly."""
        config_dict = {"app": {"name": "TestApp"}}

        config = ConfigManager.from_dict(config_dict)

        # First access
        result1 = config.get("app.name", str)

        # Second access (should use cache)
        result2 = config.get("app.name", str)

        assert result1 == result2 == "TestApp"

        # Clear cache and verify it still works
        config.clear_cache()
        result3 = config.get("app.name", str)
        assert result3 == "TestApp"
