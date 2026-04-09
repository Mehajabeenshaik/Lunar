#!/usr/bin/env python
"""Debug HF Space /step error"""
import requests

BASE_URL = "https://mehajabeen-lunar.hf.space"

# Reset
response = requests.post(
    f"{BASE_URL}/reset",
    json={"task": "warehouse_easy"},
    timeout=10
)
session_id = response.json()['session_id']
print(f"Session: {session_id}\n")

# Try step
response = requests.post(
    f"{BASE_URL}/step?session_id={session_id}",
    json={
        "reorder_quantities": [100],
        "transfers": []
    },
    timeout=10
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
