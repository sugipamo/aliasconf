#!/usr/bin/env python3
"""Debug script to test alias with environment variables."""

import os
from unittest import mock
from src.aliasconf import ConfigManager

# Create config and add alias
config = ConfigManager()
config.set("database.host", "localhost")
config.add_alias("db.host", "database.host")

print("=== Initial state ===")
print(f"database.host: {config.get('database.host', str)}")
print(f"db.host: {config.get('db.host', str)}")

print("\n=== Alias mappings ===")
alias_mappings = config._collect_alias_mappings()
print(f"Alias mappings: {alias_mappings}")

print("\n=== Loading from env with aliases ===")
with mock.patch.dict(os.environ, {
    "ALIASCONF_DB_HOST": "prod.db.com"  # Using alias path
}):
    config.load_from_env(prefix="ALIASCONF_", use_aliases=True)
    
    print(f"database.host after env load: {config.get('database.host', str)}")
    print(f"db.host after env load: {config.get('db.host', str)}")
    
    # Check what was loaded
    print("\n=== Config structure after env load ===")
    print(config.to_dict(include_aliases=True))