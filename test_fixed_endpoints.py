#!/usr/bin/env python3
"""Test fixed endpoint handling."""

import requests

print("Testing /reset endpoint with different formats...\n")

# Test 1: Query parameters only
print("1. Using query parameters: /reset?task=warehouse_easy")
r = requests.post("http://localhost:7860/reset?task=warehouse_easy")
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    sid = data["session_id"][:8]
    print(f"   Session: {sid}...")
    session_id = data["session_id"]
else:
    print(f"   Error: {r.text}")

# Test 2: Request body only
print("\n2. Using request body: POST with JSON body")
r = requests.post("http://localhost:7860/reset", json={"task": "warehouse_medium"})
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    sid = data["session_id"][:8]
    print(f"   Session: {sid}...")
    session_id = data["session_id"]
else:
    print(f"   Error: {r.text}")

# Test 3: Test step with proper format
print("\n3. Testing /step endpoint")
r = requests.post("http://localhost:7860/reset", json={"task": "warehouse_easy"})
session_id = r.json()["session_id"]

action = {
    "reorder_quantities": [50.0, 50.0, 50.0],
    "transfers": [[0.0]*3 for _ in range(3)]
}
r = requests.post(f"http://localhost:7860/step?session_id={session_id}", json={"action": action})
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   Reward: {data['reward']:.3f}")
else:
    print(f"   Error: {r.text}")

print("\n✅ All tests completed")
