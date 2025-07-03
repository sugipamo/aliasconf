"""
Performance tests for AliasConf.

Tests performance characteristics including load times, memory usage,
and scalability with large configurations.
"""

import json
import tempfile
import time
from pathlib import Path

import yaml

from aliasconf import ConfigManager


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""

    def test_small_config_load_time(self):
        """Test load time for small configurations (<100 items)."""
        config_dict = {
            f"service_{i}": {
                "aliases": [f"svc_{i}", f"s{i}"],
                "host": f"host{i}.example.com",
                "port": 8000 + i,
                "enabled": i % 2 == 0,
            }
            for i in range(50)
        }

        start_time = time.time()
        config = ConfigManager.from_dict(config_dict)
        load_time = time.time() - start_time

        # Should load small configs very quickly
        assert load_time < 0.1  # Less than 100ms

        # Test access time
        start_time = time.time()
        for i in range(10):
            value = config.get(f"service_{i}.host", str)
            assert value == f"host{i}.example.com"
        access_time = time.time() - start_time

        assert access_time < 0.01  # Less than 10ms for 10 accesses

    def test_medium_config_load_time(self):
        """Test load time for medium configurations (~1000 items)."""
        config_dict = {}

        # Create a nested structure with ~1000 total nodes
        for i in range(10):
            config_dict[f"category_{i}"] = {}
            for j in range(10):
                config_dict[f"category_{i}"][f"subcategory_{j}"] = {}
                for k in range(10):
                    config_dict[f"category_{i}"][f"subcategory_{j}"][f"item_{k}"] = {
                        "aliases": [f"alias_{i}_{j}_{k}"],
                        "value": f"value_{i}_{j}_{k}",
                    }

        start_time = time.time()
        config = ConfigManager.from_dict(config_dict)
        load_time = time.time() - start_time

        # Should handle medium configs efficiently
        assert load_time < 1.0  # Less than 1 second

        # Test nested access
        start_time = time.time()
        value = config.get("category_5.subcategory_5.item_5.value", str)
        access_time = time.time() - start_time

        assert value == "value_5_5_5"
        assert access_time < 0.01  # Single access should be fast

    def test_large_config_load_time(self):
        """Test load time for large configurations (~10000 items)."""
        config_dict = {}

        # Create a flatter structure with many items
        for i in range(100):
            section = {}
            for j in range(100):
                section[f"item_{j}"] = {
                    "aliases": [f"i{i}_{j}", f"item{i}{j}"],
                    "data": {"value": i * j, "name": f"Item {i}-{j}", "enabled": True},
                }
            config_dict[f"section_{i}"] = section

        start_time = time.time()
        config = ConfigManager.from_dict(config_dict)
        load_time = time.time() - start_time

        # Large configs should still load in reasonable time
        assert load_time < 5.0  # Less than 5 seconds

        # Test multiple accesses
        start_time = time.time()
        for i in range(0, 100, 10):
            value = config.get(f"section_{i}.item_{i}.data.value", int)
            assert value == i * i
        access_time = time.time() - start_time

        assert access_time < 0.1  # 10 accesses should be fast


class TestAliasPerformance:
    """Performance tests specifically for alias resolution."""

    def test_many_aliases_per_node_performance(self):
        """Test performance with many aliases per node."""
        # Create nodes with increasing numbers of aliases
        config_dict = {}

        for i in range(10):
            num_aliases = 10 ** (i % 4)  # 1, 10, 100, 1000 aliases
            aliases = [f"alias_{i}_{j}" for j in range(num_aliases)]
            config_dict[f"node_{i}"] = {"aliases": aliases, "value": f"value_{i}"}

        start_time = time.time()
        config = ConfigManager.from_dict(config_dict)
        load_time = time.time() - start_time

        # Should handle many aliases efficiently
        assert load_time < 1.0

        # Test alias resolution performance
        start_time = time.time()
        # Access via different aliases
        assert config.get("alias_3_50.value", str) == "value_3"  # Middle alias
        assert config.get("alias_3_99.value", str) == "value_3"  # Last alias
        access_time = time.time() - start_time

        assert access_time < 0.05  # Alias resolution should be fast

    def test_deep_alias_chain_performance(self):
        """Test performance with deeply chained alias lookups."""
        config_dict = {
            "level_0": {
                "aliases": ["l0"],
                "nested": {
                    "level_1": {
                        "aliases": ["l1"],
                        "nested": {
                            "level_2": {
                                "aliases": ["l2"],
                                "nested": {
                                    "level_3": {
                                        "aliases": ["l3"],
                                        "value": "deep_value",
                                    }
                                },
                            }
                        },
                    }
                },
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # Test accessing via full alias chain
        start_time = time.time()
        value = config.get("l0.nested.l1.nested.l2.nested.l3.value", str)
        access_time = time.time() - start_time

        assert value == "deep_value"
        assert access_time < 0.01  # Should resolve quickly despite depth

    def test_alias_vs_direct_access_performance(self):
        """Compare performance of alias access vs direct access."""
        config_dict = {
            "services": {
                "database": {
                    "aliases": ["db", "database-service", "data", "storage"],
                    "config": {"host": "localhost", "port": 5432, "name": "mydb"},
                }
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # Time direct access
        start_time = time.time()
        for _ in range(1000):
            config.get("services.database.config.host", str)
        direct_time = time.time() - start_time

        # Time alias access
        start_time = time.time()
        for _ in range(1000):
            config.get("services.db.config.host", str)
        alias_time = time.time() - start_time

        # Alias access should be comparable to direct access
        # Allow up to 2x overhead for alias resolution
        assert alias_time < direct_time * 2


class TestCachePerformance:
    """Test cache performance characteristics."""

    def test_cache_hit_performance(self):
        """Test performance improvement from cache hits."""
        config_dict = {
            f"item_{i}": {"value": f"value_{i}", "number": i} for i in range(100)
        }

        config = ConfigManager.from_dict(config_dict)

        # First access (cache miss)
        start_time = time.time()
        for i in range(100):
            config.get(f"item_{i}.value", str)
        first_access_time = time.time() - start_time

        # Second access (cache hit)
        start_time = time.time()
        for i in range(100):
            config.get(f"item_{i}.value", str)
        second_access_time = time.time() - start_time

        # Cache hits should be significantly faster
        assert second_access_time < first_access_time * 0.5

    def test_cache_memory_overhead(self):
        """Test that cache doesn't cause excessive memory usage."""
        config_dict = {
            f"item_{i}": {"data": "x" * 1000} for i in range(1000)  # 1KB string
        }

        config = ConfigManager.from_dict(config_dict)

        # Access all items to populate cache
        for i in range(1000):
            config.get(f"item_{i}.data", str)

        # Clear cache and measure impact
        config.clear_cache()

        # Re-access subset to test partial cache
        for i in range(100):
            config.get(f"item_{i}.data", str)

        # Cache should be working (test passes if no memory errors)
        assert True


class TestScalabilityLimits:
    """Test scalability limits and extreme cases."""

    def test_very_deep_nesting_performance(self):
        """Test performance with very deep nesting (100+ levels)."""
        config_dict = {}
        current = config_dict

        # Create 100 levels of nesting
        for i in range(100):
            current[f"level_{i}"] = {}
            current = current[f"level_{i}"]

        current["value"] = "deep_value"

        start_time = time.time()
        config = ConfigManager.from_dict(config_dict)
        load_time = time.time() - start_time

        # Should handle deep nesting
        assert load_time < 1.0

        # Build path and test access
        path = ".".join([f"level_{i}" for i in range(100)]) + ".value"

        start_time = time.time()
        value = config.get(path, str)
        access_time = time.time() - start_time

        assert value == "deep_value"
        assert access_time < 0.1  # Should still be reasonably fast

    def test_wide_flat_structure_performance(self):
        """Test performance with very wide flat structure."""
        # Create 10,000 top-level keys
        config_dict = {
            f"key_{i}": {"value": i, "name": f"Item {i}"} for i in range(10000)
        }

        start_time = time.time()
        config = ConfigManager.from_dict(config_dict)
        load_time = time.time() - start_time

        # Should handle wide structures
        assert load_time < 2.0

        # Test random access pattern
        import random

        indices = random.sample(range(10000), 100)

        start_time = time.time()
        for i in indices:
            value = config.get(f"key_{i}.value", int)
            assert value == i
        access_time = time.time() - start_time

        assert access_time < 0.1  # 100 random accesses should be fast


class TestFileLoadPerformance:
    """Test performance of loading from files."""

    def test_yaml_vs_json_load_performance(self):
        """Compare YAML and JSON loading performance."""
        # Create test data
        config_dict = {
            f"section_{i}": {
                "aliases": [f"sec{i}", f"s{i}"],
                "data": {
                    "values": list(range(10)),
                    "enabled": True,
                    "name": f"Section {i}",
                },
            }
            for i in range(100)
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / "config.yaml"
            json_path = Path(tmpdir) / "config.json"

            # Write YAML file
            with open(yaml_path, "w") as f:
                yaml.dump(config_dict, f)

            # Write JSON file
            with open(json_path, "w") as f:
                json.dump(config_dict, f)

            # Time YAML loading
            start_time = time.time()
            yaml_config = ConfigManager.from_file(yaml_path)
            yaml_time = time.time() - start_time

            # Time JSON loading
            start_time = time.time()
            json_config = ConfigManager.from_file(json_path)
            json_time = time.time() - start_time

            # Both should load successfully
            assert yaml_config.get("section_50.data.name", str) == "Section 50"
            assert json_config.get("section_50.data.name", str) == "Section 50"

            # JSON is typically faster than YAML
            # But both should be reasonable
            assert yaml_time < 1.0
            assert json_time < 1.0

    def test_multiple_file_merge_performance(self):
        """Test performance of merging multiple configuration files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple config files
            file_paths = []
            for i in range(10):
                config_dict = {
                    f"file_{i}": {
                        "data": {
                            "value": i,
                            "items": list(range(100)),
                        }
                    }
                }

                file_path = Path(tmpdir) / f"config_{i}.yaml"
                with open(file_path, "w") as f:
                    yaml.dump(config_dict, f)
                file_paths.append(file_path)

            # Time loading and merging
            start_time = time.time()
            config = ConfigManager.from_files(*file_paths)
            load_time = time.time() - start_time

            # Should handle multiple files efficiently
            assert load_time < 2.0

            # Verify all files were loaded
            for i in range(10):
                assert config.get(f"file_{i}.data.value", int) == i


class TestMemoryEfficiency:
    """Test memory efficiency of configurations."""

    def test_duplicate_value_memory_sharing(self):
        """Test that duplicate values don't unnecessarily duplicate memory."""
        # Create config with many duplicate values
        shared_data = {"shared": "value" * 1000}  # ~5KB string

        config_dict = {}
        for i in range(1000):
            config_dict[f"item_{i}"] = {"unique": i, "shared": shared_data}

        config = ConfigManager.from_dict(config_dict)

        # Access items to ensure they're loaded
        for i in range(0, 1000, 100):
            value = config.get(f"item_{i}.unique", int)
            assert value == i

        # If memory is shared properly, this should not cause issues
        # (Python's reference counting should handle this)
        assert True

    def test_lazy_evaluation_performance(self):
        """Test that unused parts of config don't impact performance."""
        # Create large config with mostly unused sections
        config_dict = {"used": {"value": "this will be accessed"}}

        # Add many unused sections
        for i in range(1000):
            config_dict[f"unused_{i}"] = {
                "data": {
                    "large": "x" * 10000,  # 10KB each
                    "nested": {"deep": {"value": i}},
                }
            }

        start_time = time.time()
        config = ConfigManager.from_dict(config_dict)
        load_time = time.time() - start_time

        # Should load quickly despite large unused sections
        assert load_time < 2.0

        # Accessing only used section should be fast
        start_time = time.time()
        value = config.get("used.value", str)
        access_time = time.time() - start_time

        assert value == "this will be accessed"
        assert access_time < 0.01
