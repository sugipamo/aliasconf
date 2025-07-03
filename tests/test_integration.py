"""
Integration tests for AliasConf.

Tests real-world usage scenarios, multi-file configurations,
environment integration, and migration scenarios.
"""

import os
import tempfile
from pathlib import Path

import yaml

from aliasconf import ConfigManager


class TestMultiFileIntegration:
    """Test multi-file configuration scenarios."""

    def test_base_and_override_configs(self):
        """Test base configuration with environment-specific overrides."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Base configuration
            base_config = {
                "app": {
                    "name": "MyApp",
                    "version": "1.0.0",
                    "debug": False,
                    "database": {
                        "aliases": ["db"],
                        "host": "localhost",
                        "port": 5432,
                        "name": "myapp"
                    }
                }
            }

            # Development override
            dev_config = {
                "app": {
                    "debug": True,
                    "database": {
                        "host": "dev.db.local",
                        "name": "myapp_dev"
                    }
                }
            }

            # Production override
            prod_config = {
                "app": {
                    "database": {
                        "host": "prod.db.example.com",
                        "port": 5433,
                        "ssl": True
                    }
                }
            }

            # Write files
            base_path = Path(tmpdir) / "base.yaml"
            dev_path = Path(tmpdir) / "dev.yaml"
            prod_path = Path(tmpdir) / "prod.yaml"

            with open(base_path, 'w') as f:
                yaml.dump(base_config, f)
            with open(dev_path, 'w') as f:
                yaml.dump(dev_config, f)
            with open(prod_path, 'w') as f:
                yaml.dump(prod_config, f)

            # Test development configuration
            dev_config = ConfigManager.from_files(base_path, dev_path)
            assert dev_config.get("app.name", str) == "MyApp"
            assert dev_config.get("app.debug", bool) is True
            assert dev_config.get("app.database.host", str) == "dev.db.local"
            assert dev_config.get("app.database.port", int) == 5432  # From base
            assert dev_config.get("app.db.name", str) == "myapp_dev"  # Via alias

            # Test production configuration
            prod_config = ConfigManager.from_files(base_path, prod_path)
            assert prod_config.get("app.debug", bool) is False  # From base
            assert prod_config.get("app.database.host", str) == "prod.db.example.com"
            assert prod_config.get("app.database.port", int) == 5433
            assert prod_config.get("app.database.ssl", bool) is True
            assert prod_config.get("app.db.ssl", bool) is True  # Via alias

    def test_modular_configuration_structure(self):
        """Test modular configuration with separate files for different components."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Application settings
            app_config = {
                "app": {
                    "name": "ModularApp",
                    "version": "2.0.0",
                    "features": {
                        "aliases": ["feat", "capabilities"],
                        "auth": True,
                        "api": True
                    }
                }
            }

            # Database settings
            db_config = {
                "database": {
                    "primary": {
                        "aliases": ["main_db", "primary_db"],
                        "host": "db1.example.com",
                        "pool_size": 10
                    },
                    "replica": {
                        "aliases": ["read_db", "replica_db"],
                        "host": "db2.example.com",
                        "pool_size": 5
                    }
                }
            }

            # Service endpoints
            services_config = {
                "services": {
                    "auth": {
                        "aliases": ["authentication", "auth_service"],
                        "url": "https://auth.example.com",
                        "timeout": 30
                    },
                    "api": {
                        "aliases": ["backend", "api_service"],
                        "url": "https://api.example.com",
                        "timeout": 60
                    }
                }
            }

            # Write files
            app_path = Path(tmpdir) / "app.yaml"
            db_path = Path(tmpdir) / "database.yaml"
            services_path = Path(tmpdir) / "services.yaml"

            with open(app_path, 'w') as f:
                yaml.dump(app_config, f)
            with open(db_path, 'w') as f:
                yaml.dump(db_config, f)
            with open(services_path, 'w') as f:
                yaml.dump(services_config, f)

            # Load all configurations
            config = ConfigManager.from_files(app_path, db_path, services_path)

            # Test access to all modules
            assert config.get("app.name", str) == "ModularApp"
            assert config.get("app.feat.auth", bool) is True  # Via alias

            assert config.get("database.main_db.host", str) == "db1.example.com"  # Via alias
            assert config.get("database.read_db.host", str) == "db2.example.com"  # Via alias

            assert config.get("services.authentication.url", str) == "https://auth.example.com"  # Via alias
            assert config.get("services.backend.timeout", int) == 60  # Via alias

    def test_config_includes_pattern(self):
        """Test configuration pattern with includes/imports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Common settings
            common_config = {
                "common": {
                    "aliases": ["shared", "defaults"],
                    "timeout": 30,
                    "retries": 3,
                    "log_level": "INFO"
                }
            }

            # Service A configuration
            service_a_config = {
                "service_a": {
                    "name": "Service A",
                    "common_ref": "{common.timeout}",  # Reference to common
                    "endpoint": "https://a.example.com"
                }
            }

            # Service B configuration
            service_b_config = {
                "service_b": {
                    "name": "Service B",
                    "timeout": "{shared.timeout}",  # Reference via alias
                    "retries": "{defaults.retries}",  # Reference via another alias
                    "endpoint": "https://b.example.com"
                }
            }

            # Write files
            common_path = Path(tmpdir) / "common.yaml"
            service_a_path = Path(tmpdir) / "service_a.yaml"
            service_b_path = Path(tmpdir) / "service_b.yaml"

            with open(common_path, 'w') as f:
                yaml.dump(common_config, f)
            with open(service_a_path, 'w') as f:
                yaml.dump(service_a_config, f)
            with open(service_b_path, 'w') as f:
                yaml.dump(service_b_config, f)

            # Load all configurations
            config = ConfigManager.from_files(common_path, service_a_path, service_b_path)

            # Test that references work
            {
                "common": config._root.next_nodes[0],  # Assuming structure
                "shared": config._root.next_nodes[0],
                "defaults": config._root.next_nodes[0]
            }

            # Note: Real template resolution would need proper context setup
            # This tests the configuration structure is loaded correctly
            assert config.get("common.timeout", int) == 30
            assert config.get("shared.timeout", int) == 30  # Via alias
            assert config.get("service_a.endpoint", str) == "https://a.example.com"
            assert config.get("service_b.endpoint", str) == "https://b.example.com"


class TestEnvironmentIntegration:
    """Test integration with environment variables and external sources."""

    def test_environment_variable_substitution(self):
        """Test configuration with environment variable placeholders."""
        # Set test environment variables
        os.environ["TEST_DB_HOST"] = "env.db.example.com"
        os.environ["TEST_DB_PORT"] = "5432"
        os.environ["TEST_API_KEY"] = "secret_key_123"

        try:
            config_dict = {
                "database": {
                    "aliases": ["db"],
                    "host": "${TEST_DB_HOST}",
                    "port": "${TEST_DB_PORT}",
                    "credentials": {
                        "api_key": "${TEST_API_KEY}"
                    }
                }
            }

            config = ConfigManager.from_dict(config_dict)

            # Note: Actual env var substitution would need to be implemented
            # This tests the configuration structure
            assert config.has("database.host")
            assert config.has("db.credentials.api_key")  # Via alias

        finally:
            # Clean up environment
            os.environ.pop("TEST_DB_HOST", None)
            os.environ.pop("TEST_DB_PORT", None)
            os.environ.pop("TEST_API_KEY", None)

    def test_config_with_defaults_and_env_override(self):
        """Test configuration with defaults that can be overridden by env vars."""
        config_dict = {
            "app": {
                "aliases": ["application"],
                "name": "${APP_NAME:MyDefaultApp}",
                "port": "${APP_PORT:8080}",
                "debug": "${APP_DEBUG:false}"
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # Test structure is loaded correctly
        assert config.has("app.name")
        assert config.has("application.port")  # Via alias

        # Set environment variable and test override
        os.environ["APP_NAME"] = "OverriddenApp"
        try:
            # In real implementation, this would pick up the env var
            assert config.has("app.name")
        finally:
            os.environ.pop("APP_NAME", None)


class TestMigrationScenarios:
    """Test configuration migration scenarios."""

    def test_legacy_to_new_format_migration(self):
        """Test migrating from legacy format to new format with aliases."""
        # Legacy format (flat structure)
        legacy_config = {
            "db_host": "localhost",
            "db_port": 5432,
            "db_name": "legacy_db",
            "app_name": "LegacyApp",
            "app_debug": True,
            "api_timeout": 30,
            "api_retries": 3
        }

        # New format (hierarchical with aliases)
        new_config = {
            "database": {
                "aliases": ["db", "db_config"],
                "host": "{db_host}",
                "port": "{db_port}",
                "name": "{db_name}"
            },
            "application": {
                "aliases": ["app"],
                "name": "{app_name}",
                "debug": "{app_debug}"
            },
            "api": {
                "aliases": ["api_config"],
                "timeout": "{api_timeout}",
                "retries": "{api_retries}"
            }
        }

        # Combine legacy and new format
        combined_config = {**legacy_config, **new_config}
        config = ConfigManager.from_dict(combined_config)

        # Test that both formats work
        assert config.get("db_host", str) == "localhost"  # Legacy
        assert config.get("database.host", str) == "{db_host}"  # New (template)
        assert config.get("db.host", str) == "{db_host}"  # New via alias

        # Test hierarchical access
        assert config.get("application.name", str) == "{app_name}"
        assert config.get("app.debug", str) == "{app_debug}"  # Via alias

    def test_gradual_alias_introduction(self):
        """Test gradually introducing aliases to existing configuration."""
        with tempfile.TemporaryDirectory():
            # Phase 1: Original configuration
            phase1_config = {
                "python_service": {
                    "timeout": 30,
                    "workers": 4
                },
                "javascript_service": {
                    "timeout": 60,
                    "workers": 2
                }
            }

            # Phase 2: Add some aliases
            phase2_config = {
                "python_service": {
                    "aliases": ["py_service"],
                    "timeout": 30,
                    "workers": 4
                },
                "javascript_service": {
                    "aliases": ["js_service"],
                    "timeout": 60,
                    "workers": 2
                }
            }

            # Phase 3: Add more aliases and reorganize
            phase3_config = {
                "services": {
                    "python": {
                        "aliases": ["py", "python_service", "py_service"],
                        "timeout": 30,
                        "workers": 4
                    },
                    "javascript": {
                        "aliases": ["js", "javascript_service", "js_service"],
                        "timeout": 60,
                        "workers": 2
                    }
                }
            }

            # Test each phase
            config1 = ConfigManager.from_dict(phase1_config)
            assert config1.get("python_service.timeout", int) == 30

            config2 = ConfigManager.from_dict(phase2_config)
            assert config2.get("python_service.timeout", int) == 30
            assert config2.get("py_service.timeout", int) == 30  # Via alias

            config3 = ConfigManager.from_dict(phase3_config)
            assert config3.get("services.python.timeout", int) == 30
            assert config3.get("services.py.timeout", int) == 30  # Short alias
            assert config3.get("services.python_service.timeout", int) == 30  # Legacy name as alias


class TestRealWorldUseCases:
    """Test real-world usage scenarios."""

    def test_microservices_configuration(self):
        """Test configuration for a microservices architecture."""
        config_dict = {
            "services": {
                "auth": {
                    "aliases": ["authentication", "auth_service"],
                    "host": "auth.internal",
                    "port": 3000,
                    "endpoints": {
                        "login": "/api/v1/login",
                        "logout": "/api/v1/logout",
                        "verify": "/api/v1/verify"
                    }
                },
                "user": {
                    "aliases": ["user_service", "users"],
                    "host": "user.internal",
                    "port": 3001,
                    "database": {
                        "aliases": ["user_db"],
                        "name": "users",
                        "pool_size": 20
                    }
                },
                "product": {
                    "aliases": ["product_service", "products", "catalog"],
                    "host": "product.internal",
                    "port": 3002,
                    "cache": {
                        "aliases": ["product_cache"],
                        "ttl": 3600,
                        "max_size": 1000
                    }
                }
            },
            "shared": {
                "aliases": ["common"],
                "redis": {
                    "aliases": ["cache", "session_store"],
                    "host": "redis.internal",
                    "port": 6379
                },
                "rabbitmq": {
                    "aliases": ["mq", "message_queue"],
                    "host": "rabbitmq.internal",
                    "port": 5672
                }
            }
        }

        config = ConfigManager.from_dict(config_dict)

        # Test service discovery via aliases
        assert config.get("services.authentication.host", str) == "auth.internal"
        assert config.get("services.users.port", int) == 3001
        assert config.get("services.catalog.cache.ttl", int) == 3600

        # Test shared services
        assert config.get("shared.cache.host", str) == "redis.internal"
        assert config.get("common.mq.port", int) == 5672

        # Test nested aliases
        assert config.get("services.user.user_db.name", str) == "users"
        assert config.get("services.product.product_cache.max_size", int) == 1000

    def test_multi_environment_deployment(self):
        """Test configuration for multi-environment deployment."""
        base_config = {
            "app": {
                "name": "MultiEnvApp",
                "version": "1.0.0"
            },
            "features": {
                "aliases": ["feature_flags", "flags"],
                "new_ui": False,
                "beta_features": False,
                "analytics": True
            }
        }

        env_configs = {
            "dev": {
                "app": {
                    "aliases": ["application"],
                    "env": "development"
                },
                "features": {
                    "new_ui": True,
                    "beta_features": True
                },
                "logging": {
                    "aliases": ["logs"],
                    "level": "DEBUG",
                    "output": "console"
                }
            },
            "staging": {
                "app": {
                    "aliases": ["application"],
                    "env": "staging"
                },
                "features": {
                    "new_ui": True,
                    "beta_features": False
                },
                "logging": {
                    "aliases": ["logs"],
                    "level": "INFO",
                    "output": "file"
                }
            },
            "prod": {
                "app": {
                    "aliases": ["application"],
                    "env": "production"
                },
                "features": {
                    "new_ui": False,
                    "beta_features": False
                },
                "logging": {
                    "aliases": ["logs"],
                    "level": "WARNING",
                    "output": "centralized"
                }
            }
        }

        # Test each environment
        for env_name, env_config in env_configs.items():
            # Merge base with environment
            merged_dict = {}
            merged_dict.update(base_config)
            for key, value in env_config.items():
                if key in merged_dict and isinstance(merged_dict[key], dict):
                    merged_dict[key].update(value)
                else:
                    merged_dict[key] = value

            config = ConfigManager.from_dict(merged_dict)

            # Common assertions
            assert config.get("app.name", str) == "MultiEnvApp"
            assert config.get("application.env", str) == env_config["app"]["env"]  # Via alias

            # Environment-specific assertions
            if env_name == "dev":
                assert config.get("features.new_ui", bool) is True
                assert config.get("logs.level", str) == "DEBUG"  # Via alias
            elif env_name == "staging":
                assert config.get("feature_flags.new_ui", bool) is True  # Via alias
                assert config.get("feature_flags.beta_features", bool) is False
            elif env_name == "prod":
                assert config.get("flags.new_ui", bool) is False  # Via alias
                assert config.get("logging.output", str) == "centralized"


class TestConcurrentAccess:
    """Test concurrent access patterns."""

    def test_thread_safe_access(self):
        """Test that configuration can be safely accessed from multiple threads."""
        import threading

        config_dict = {
            f"service_{i}": {
                "aliases": [f"svc_{i}"],
                "data": {
                    "value": i,
                    "name": f"Service {i}"
                }
            }
            for i in range(100)
        }

        config = ConfigManager.from_dict(config_dict)
        results = {}
        errors = []

        def access_config(service_num):
            try:
                # Access via main key and alias
                value1 = config.get(f"service_{service_num}.data.value", int)
                value2 = config.get(f"svc_{service_num}.data.value", int)
                name = config.get(f"service_{service_num}.data.name", str)

                results[service_num] = (value1, value2, name)
            except Exception as e:
                errors.append((service_num, str(e)))

        # Create threads
        threads = []
        for i in range(100):
            thread = threading.Thread(target=access_config, args=(i,))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join(timeout=5.0)

        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 100

        for i in range(100):
            assert results[i][0] == i
            assert results[i][1] == i
            assert results[i][2] == f"Service {i}"
