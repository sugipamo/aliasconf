#!/usr/bin/env python3
"""Debug script to test add_alias functionality."""

from src.aliasconf import ConfigManager

# Create a simple config
config = ConfigManager()
config.set("database.host", "localhost")

# Before adding alias
print("=== Before adding alias ===")
print(f"database.host: {config.get('database.host', str)}")
try:
    print(f"db.host: {config.get('db.host', str)}")
except Exception as e:
    print(f"db.host: {e}")

# Print config structure
print("\nConfig structure:")
config_dict = config.to_dict(include_aliases=True)
print(config_dict)

# Add alias
print("\n=== Adding alias db.host -> database.host ===")
config.add_alias("db.host", "database.host")

# After adding alias
print("\n=== After adding alias ===")
print(f"database.host: {config.get('database.host', str)}")
try:
    print(f"db.host: {config.get('db.host', str)}")
except Exception as e:
    print(f"db.host: {e}")

# Print config structure
print("\nConfig structure:")
config_dict = config.to_dict(include_aliases=True)
print(config_dict)

# Test _collect_alias_mappings
print("\n=== Alias mappings ===")
alias_mappings = config._collect_alias_mappings()
print(f"Alias mappings: {alias_mappings}")