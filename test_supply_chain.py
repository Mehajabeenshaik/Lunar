#!/usr/bin/env python3
"""Test supply_chain_basic task."""

import requests
import json

print("Testing supply_chain_basic task initialization...")
r = requests.post("http://localhost:7860/reset?task=supply_chain_basic")
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")

if r.status_code != 200:
    print("\nFull response:")
    print(r.text)
