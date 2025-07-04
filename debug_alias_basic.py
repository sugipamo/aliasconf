#!/usr/bin/env python3
"""Debug script to understand how aliases work."""

from src.aliasconf import ConfigManager

# Test with aliases defined in config
config_dict = {
    "database": {
        "aliases": ["db"],  # database has alias 'db'
        "host": "localhost",
        "port": 5432
    }
}

config = ConfigManager.from_dict(config_dict)

print("=== Testing aliases defined in config ===")
print(f"database.host: {config.get('database.host', str)}")
print(f"db.host: {config.get('db.host', str)}")  # Should work

print("\n=== Config structure ===")
print(config.to_dict(include_aliases=True))

print("\n=== Alias mappings ===")
alias_mappings = config._collect_alias_mappings()
print(f"Alias mappings: {alias_mappings}")

# Print tree structure
print("\n=== Tree structure ===")
def print_tree(node, level=0):
    indent = "  " * level
    print(f"{indent}{node.key}: value={node.value}, matches={node.matches}, aliases={node.aliases}")
    for child in node.next_nodes:
        print_tree(child, level + 1)

if config._root:
    print_tree(config._root)