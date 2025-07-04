#!/usr/bin/env python3
"""
Basic usage examples for AliasConf.

This script demonstrates the core features of AliasConf including
alias resolution, type conversion, and template formatting.
"""

from aliasconf import ConfigManager


def main():
    print("🔧 AliasConf Basic Usage Examples\n")

    # Example 1: Basic configuration with aliases
    print("📝 Example 1: Basic Configuration with Aliases")
    print("-" * 50)

    config_dict = {
        "python": {
            "aliases": ["py", "python3"],
            "timeout": 30,
            "command": "python {script}",
            "version": "3.11",
        },
        "cpp": {
            "aliases": ["c++", "cxx"],
            "timeout": 60,
            "command": "g++ {source} -o {output}",
            "std": "c++17",
        },
        "database": {"host": "localhost", "port": 5432, "name": "myapp"},
    }

    config = ConfigManager.from_dict(config_dict)

    # Access same value through different aliases
    print("Accessing Python timeout through different aliases:")
    print(f"  python.timeout:  {config.get('python.timeout', int)}")
    print(f"  py.timeout:      {config.get('py.timeout', int)}")
    print(f"  python3.timeout: {config.get('python3.timeout', int)}")
    print()

    # Type conversion examples
    print("Type conversion examples:")
    print(f"  Database port (int):    {config.get('database.port', int)}")
    print(f"  Database host (str):    {config.get('database.host', str)}")
    print(f"  Python version (str):   {config.get('python.version', str)}")
    print()

    # Example 2: Template formatting
    print("📝 Example 2: Template Formatting")
    print("-" * 50)

    # Format Python command
    python_cmd = config.get_formatted("python.command", {"script": "hello.py"})
    print(f"Python command: {python_cmd}")

    # Format C++ command
    cpp_cmd = config.get_formatted(
        "cpp.command", {"source": "main.cpp", "output": "main"}
    )
    print(f"C++ command: {cpp_cmd}")
    print()

    # Example 3: Default values
    print("📝 Example 3: Default Values")
    print("-" * 50)

    # Existing values
    existing_port = config.get("database.port", int)
    print(f"Existing database port: {existing_port}")

    # Non-existing values with defaults
    debug_mode = config.get("app.debug", bool, False)
    max_connections = config.get("database.max_connections", int, 100)
    app_name = config.get("app.name", str, "MyApp")

    print(f"Debug mode (default): {debug_mode}")
    print(f"Max connections (default): {max_connections}")
    print(f"App name (default): {app_name}")
    print()

    # Example 4: Checking existence
    print("📝 Example 4: Checking Path Existence")
    print("-" * 50)

    paths_to_check = [
        "python.timeout",
        "py.timeout",
        "database.host",
        "nonexistent.path",
        "app.name",
    ]

    for path in paths_to_check:
        exists = config.has(path)
        print(f"  {path:<20} {'✅ exists' if exists else '❌ not found'}")
    print()

    # Example 5: Complex nested configuration
    print("📝 Example 5: Complex Nested Configuration")
    print("-" * 50)

    complex_config = {
        "services": {
            "web": {
                "aliases": ["frontend", "ui"],
                "host": "0.0.0.0",
                "port": 8080,
                "ssl": {
                    "enabled": True,
                    "cert_path": "/etc/ssl/cert.pem",
                    "key_path": "/etc/ssl/key.pem",
                },
            },
            "api": {
                "aliases": ["backend", "server"],
                "host": "127.0.0.1",
                "port": 3000,
                "rate_limit": {"enabled": True, "requests_per_minute": 100},
            },
        }
    }

    complex = ConfigManager.from_dict(complex_config)

    # Access nested values through aliases
    web_port = complex.get("web.port", int)
    frontend_port = complex.get("frontend.port", int)
    ssl_enabled = complex.get("web.ssl.enabled", bool)

    print(f"Web service port (via 'web'): {web_port}")
    print(f"Web service port (via 'frontend'): {frontend_port}")
    print(f"SSL enabled: {ssl_enabled}")

    api_rate_limit = complex.get("backend.rate_limit.requests_per_minute", int)
    print(f"API rate limit (via 'backend' alias): {api_rate_limit}")
    print()

    # Example 6: Configuration merging
    print("📝 Example 6: Configuration Merging")
    print("-" * 50)

    base_config = ConfigManager.from_dict(
        {
            "app": {"name": "MyApp", "version": "1.0.0", "debug": False},
            "database": {"host": "localhost", "port": 5432},
        }
    )

    dev_config = ConfigManager.from_dict(
        {
            "app": {"debug": True, "log_level": "DEBUG"},
            "database": {"host": "dev-db-server", "ssl": True},
        }
    )

    merged = base_config.merge(dev_config)

    print("Merged configuration:")
    print(f"  App name: {merged.get('app.name', str)}")
    print(f"  App debug: {merged.get('app.debug', bool)}")
    print(f"  App log level: {merged.get('app.log_level', str)}")
    print(f"  Database host: {merged.get('database.host', str)}")
    print(f"  Database port: {merged.get('database.port', int)}")
    print(f"  Database SSL: {merged.get('database.ssl', bool)}")
    print()

    print("✅ All examples completed successfully!")


if __name__ == "__main__":
    main()
