#!/usr/bin/env python3

import os
from unittest import mock
from aliasconf import ConfigManager

def custom_converter(key: str, value: str):
    print(f"Converting key: {key}, value: {value}")
    if key.endswith("_list") or key.endswith(".list"):
        result = value.split(",")
        print(f"  -> Converted to list: {result}")
        return result
    return value

with mock.patch.dict(os.environ, {
    "ALIASCONF_ALLOWED_IPS_LIST": "192.168.1.1,192.168.1.2,192.168.1.3"
}):
    config = ConfigManager()
    config.load_from_env(prefix="ALIASCONF_", converter=custom_converter)
    
    print("\nConfig tree:")
    config_dict = config.to_dict(include_aliases=False)
    print(config_dict)
    
    print("\nTrying to get allowed.ips.list:")
    try:
        result = config.get("allowed.ips.list", list)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
        # Try getting as Any type
        try:
            result = config.get("allowed.ips.list", str)
            print(f"As string: {result}")
        except:
            pass