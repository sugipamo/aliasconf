"""
Pytest configuration and shared fixtures for AliasConf tests.

Provides common test fixtures, utilities, and test data generators.
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import pytest
import yaml

from aliasconf import ConfigManager


# Test data generators
def generate_nested_config(
    depth: int = 3, width: int = 3
) -> Dict[str, Any]:
    """
    Generate a nested configuration structure for testing.

    Args:
        depth: Maximum nesting depth
        width: Number of keys at each level

    Returns:
        Nested dictionary configuration
    """
    def _generate_level(current_depth: int) -> Dict[str, Any]:
        if current_depth <= 0:
            return {f"leaf_{i}": f"value_{i}" for i in range(width)}

        result = {}
        for i in range(width):
            if i == 0:  # Add aliases to first item
                result[f"node_{i}"] = {
                    "aliases": [f"n{i}", f"alias_{i}"],
                    **_generate_level(current_depth - 1),
                }
            else:
                result[f"node_{i}"] = _generate_level(current_depth - 1)

        return result

    return _generate_level(depth)


def generate_flat_config(num_keys: int = 100) -> Dict[str, Any]:
    """
    Generate a flat configuration with many top-level keys.

    Args:
        num_keys: Number of top-level keys

    Returns:
        Flat dictionary configuration
    """
    return {
        f"key_{i}": {
            "aliases": [f"k{i}", f"alias_{i}"] if i % 10 == 0 else [],
            "value": i,
            "name": f"Item {i}",
            "enabled": i % 2 == 0,
        }
        for i in range(num_keys)
    }


# Fixtures for common test configurations
@pytest.fixture
def simple_config():
    """Provide a simple test configuration."""
    return {
        "app": {
            "name": "TestApp",
            "version": "1.0.0",
            "debug": False
        },
        "database": {
            "aliases": ["db"],
            "host": "localhost",
            "port": 5432
        }
    }


@pytest.fixture
def nested_config():
    """Provide a deeply nested test configuration."""
    return {
        "services": {
            "backend": {
                "api": {
                    "v1": {
                        "aliases": ["api_v1"],
                        "endpoint": "/api/v1",
                        "auth": {
                            "aliases": ["auth_v1"],
                            "enabled": True,
                            "token_expiry": 3600
                        }
                    }
                }
            }
        }
    }


@pytest.fixture
def alias_heavy_config():
    """Provide a configuration with many aliases."""
    return {
        "python": {
            "aliases": ["py", "python3", "python-lang", "snake"],
            "version": "3.9",
            "path": "/usr/bin/python3"
        },
        "javascript": {
            "aliases": ["js", "node", "nodejs", "ecmascript"],
            "version": "14.0",
            "path": "/usr/bin/node"
        },
        "cpp": {
            "aliases": ["c++", "cplusplus", "cxx"],
            "version": "11",
            "compiler": "g++"
        }
    }


@pytest.fixture
def template_config():
    """Provide a configuration with template strings."""
    return {
        "base": {
            "url": "https://example.com",
            "api_version": "v1"
        },
        "endpoints": {
            "api": "{base.url}/api/{base.api_version}",
            "auth": "{endpoints.api}/auth",
            "users": "{endpoints.api}/users"
        }
    }


@pytest.fixture
def config_manager(simple_config):
    """Provide a ConfigManager instance with simple config."""
    return ConfigManager.from_dict(simple_config)


# Fixtures for file-based testing
@pytest.fixture
def temp_config_dir():
    """Provide a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def yaml_config_file(temp_config_dir, simple_config):
    """Create a temporary YAML config file."""
    file_path = temp_config_dir / "config.yaml"
    with open(file_path, "w") as f:
        yaml.dump(simple_config, f)
    return file_path


@pytest.fixture
def json_config_file(temp_config_dir, simple_config):
    """Create a temporary JSON config file."""
    file_path = temp_config_dir / "config.json"
    with open(file_path, "w") as f:
        json.dump(simple_config, f)
    return file_path


@pytest.fixture
def multi_config_files(temp_config_dir):
    """Create multiple config files for testing."""
    base_config = {
        "app": {
            "name": "BaseApp",
            "version": "1.0.0"
        }
    }

    override_config = {
        "app": {
            "version": "2.0.0",
            "debug": True
        },
        "features": {
            "aliases": ["feat"],
            "new_ui": True
        }
    }

    base_path = temp_config_dir / "base.yaml"
    override_path = temp_config_dir / "override.yaml"

    with open(base_path, "w") as f:
        yaml.dump(base_config, f)

    with open(override_path, "w") as f:
        yaml.dump(override_config, f)

    return base_path, override_path


# Test data fixtures
@pytest.fixture
def large_config_dict():
    """Provide a large configuration for performance testing."""
    return generate_flat_config(1000)


@pytest.fixture
def deep_config_dict():
    """Provide a deeply nested configuration."""
    return generate_nested_config(depth=10, width=3)


# Helper fixtures
@pytest.fixture
def capture_performance():
    """Fixture to capture performance metrics."""
    import time

    class PerformanceCapture:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.duration = None

        def start(self):
            self.start_time = time.time()

        def stop(self):
            self.end_time = time.time()
            self.duration = self.end_time - self.start_time
            return self.duration

        def __enter__(self):
            self.start()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.stop()

    return PerformanceCapture()


@pytest.fixture
def sample_configs():
    """Provide a collection of sample configurations for testing."""
    return {
        "minimal": {
            "key": "value"
        },
        "with_aliases": {
            "service": {
                "aliases": ["svc", "srv"],
                "port": 8080
            }
        },
        "nested": {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep"
                    }
                }
            }
        },
        "mixed_types": {
            "string": "text",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "null": None
        }
    }


# Markers for categorizing tests
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "edge_case: marks tests as edge case tests"
    )


# Parametrized test data
ALIAS_TEST_CASES = [
    # (config_dict, path, expected_value)
    ({"item": {"aliases": ["i"], "value": 1}}, "i.value", 1),
    ({"item": {"aliases": ["a", "b", "c"], "value": 2}}, "b.value", 2),
    ({"item": {"aliases": [], "value": 3}}, "item.value", 3),
]

TYPE_CONVERSION_TEST_CASES = [
    # (value, target_type, expected)
    ("123", int, 123),
    ("true", bool, True),
    ("3.14", float, 3.14),
    ("hello", str, "hello"),
    ([1, 2, 3], list, [1, 2, 3]),
    ({"key": "value"}, dict, {"key": "value"}),
]

PATH_FORMAT_TEST_CASES = [
    # (path_input, expected_normalized)
    ("a.b.c", ["a", "b", "c"]),
    (["a", "b", "c"], ["a", "b", "c"]),
    (("a", "b", "c"), ["a", "b", "c"]),
]


# Utility functions for tests
def assert_config_equal(
    config1: Dict[str, Any], config2: Dict[str, Any]
) -> None:
    """Assert two configurations are equal (ignoring aliases)."""
    def remove_aliases(d):
        if isinstance(d, dict):
            return {
                k: remove_aliases(v)
                for k, v in d.items()
                if k != "aliases"
            }
        elif isinstance(d, list):
            return [remove_aliases(item) for item in d]
        else:
            return d

    clean1 = remove_aliases(config1)
    clean2 = remove_aliases(config2)
    assert clean1 == clean2


def create_test_config_files(
    directory: Path, configs: Dict[str, Dict[str, Any]]
) -> List[Path]:
    """
    Create multiple test configuration files in a directory.

    Args:
        directory: Directory to create files in
        configs: Dictionary of filename -> config dict

    Returns:
        List of created file paths
    """
    paths = []
    for filename, config in configs.items():
        if filename.endswith(".json"):
            file_path = directory / filename
            with open(file_path, "w") as f:
                json.dump(config, f)
        else:  # Default to YAML
            file_path = directory / f"{filename}.yaml"
            with open(file_path, "w") as f:
                yaml.dump(config, f)
        paths.append(file_path)

    return paths
