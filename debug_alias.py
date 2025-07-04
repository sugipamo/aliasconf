#!/usr/bin/env python3
"""Debug script to test alias resolution."""

from src.aliasconf.core.resolver import create_config_root_from_dict, resolve_best

config_dict = {
    "python": {
        "aliases": ["py", "python3"],
        "timeout": 30,
        "command": "python script.py",
    }
}

# Create config tree
root = create_config_root_from_dict(config_dict)


# Debug: Print tree structure
def print_tree(node, level=0):
    indent = "  " * level
    print(f"{indent}{node.key}: {node.value} (matches: {node.matches})")
    for child in node.next_nodes:
        print_tree(child, level + 1)


print("Tree structure:")
print_tree(root)
print()

# Test alias resolution
print("Testing alias resolution:")
paths_to_test = [
    ["python", "timeout"],
    ["py", "timeout"],
    ["python3", "timeout"],
]

for path in paths_to_test:
    result = resolve_best(root, path)
    print(f"Path {path}: {result}")
    if result:
        print(f"  Value: {result.value}")
