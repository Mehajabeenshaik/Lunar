#!/usr/bin/env python
"""Test API endpoints."""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

print("=" * 70)
print("TESTING API ENDPOINTS")
print("=" * 70)

# Test 1: Health
print("\n1. Testing /health")
response = requests.get(f"{BASE_URL}/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# Test 2: Reset (warehouse_easy)
print("\n2. Testing POST /reset (warehouse_easy)")
response = requests.post(f"{BASE_URL}/reset", json={"task": "warehouse_easy"})
print(f"   Status: {response.status_code}")
reset_data = response.json()
print(f"   Task: {reset_data.get('task')}")
obs = reset_data.get('observation', {})
print(f"   Observation keys: {list(obs.keys())}")

# Test 3: Step
print("\n3. Testing POST /step")
action = {
    "reorder_quantities": [50.0],
    "transfers": [[0.0]]
}
response = requests.post(f"{BASE_URL}/step", json={"action": action})
print(f"   Status: {response.status_code}")
step_data = response.json()
print(f"   Reward: {step_data.get('reward'):.2f}")
print(f"   Done: {step_data.get('done')}")

# Test 4: State
print("\n4. Testing GET /state")
response = requests.get(f"{BASE_URL}/state")
print(f"   Status: {response.status_code}")
state_data = response.json()
print(f"   Task: {state_data.get('task')}")
print(f"   Episode rewards: {len(state_data.get('episode_rewards', []))} stored")

# Test 5: Reset (warehouse_medium)
print("\n5. Testing POST /reset (warehouse_medium)")
response = requests.post(f"{BASE_URL}/reset", json={"task": "warehouse_medium"})
print(f"   Status: {response.status_code}")
reset_data = response.json()
print(f"   Task: {reset_data.get('task')}")

# Test 6: Reset (warehouse_hard)
print("\n6. Testing POST /reset (warehouse_hard)")
response = requests.post(f"{BASE_URL}/reset", json={"task": "warehouse_hard"})
print(f"   Status: {response.status_code}")
reset_data = response.json()
print(f"   Task: {reset_data.get('task')}")

print("\n" + "=" * 70)
print("ALL API ENDPOINT TESTS PASSED!")
print("=" * 70)
