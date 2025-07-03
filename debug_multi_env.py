#!/usr/bin/env python3
"""Debug script for multi-environment test case."""

from src.aliasconf.core.manager import ConfigManager
from src.aliasconf.core.resolver import create_config_root_from_dict

base_config = {
    "features": {
        "aliases": ["feature_flags", "flags"],
        "new_ui": False,
        "beta_features": False,
        "analytics": True
    }
}

staging_config = {
    "features": {
        "new_ui": True,
        "beta_features": False
    }
}

# Merge configs
merged_dict = {}
merged_dict.update(base_config)
for key, value in staging_config.items():
    if key in merged_dict and isinstance(merged_dict[key], dict):
        merged_dict[key].update(value)
    else:
        merged_dict[key] = value

print("Merged config:")
print(merged_dict)
print()

# Create config
config = ConfigManager.from_dict(merged_dict)

# Test access patterns
print("Testing access patterns:")
print(f"features.new_ui: {config.get('features.new_ui', bool)}")

try:
    result = config.get('feature_flags.new_ui', bool)
    print(f"feature_flags.new_ui: {result}")
except Exception as e:
    print(f"feature_flags.new_ui: ERROR - {e}")

# Debug tree structure

root = create_config_root_from_dict(merged_dict)

def print_tree(node, level=0):
    indent = "  " * level
    print(f"{indent}{node.key}: {node.value} (matches: {node.matches})")
    for child in node.next_nodes:
        print_tree(child, level + 1)

print("\nTree structure:")
print_tree(root)

