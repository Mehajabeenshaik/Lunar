#!/usr/bin/env python
"""Test complete workflow on HF Space"""
import requests
import json
import sys

BASE_URL = "https://mehajabeen-lunar.hf.space"

print("=== TESTING HF SPACE WORKFLOW ===\n")

# Test 1: Health
print("1. Testing /health...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✓ PASS")
    else:
        print(f"   ✗ FAIL")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ FAIL: {e}")
    sys.exit(1)

# Test 2: Manifest
print("\n2. Testing /manifest...")
try:
    response = requests.get(f"{BASE_URL}/manifest", timeout=10)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Tasks: {data.get('tasks')}")
    print(f"   Tasks with graders: {data.get('features', {}).get('tasks_with_graders')}")
    print(f"   Graders: {data.get('graders')}")
    if data.get('features', {}).get('tasks_with_graders') >= 3:
        print(f"   ✓ PASS - 3+ tasks have graders")
    else:
        print(f"   ✗ FAIL - Not enough graders")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ FAIL: {e}")
    sys.exit(1)

# Test 3: Reset
print("\n3. Testing /reset...")
try:
    response = requests.post(
        f"{BASE_URL}/reset",
        json={"task": "warehouse_easy"},
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    reset_data = response.json()
    session_id = reset_data.get('session_id')
    print(f"   Session ID: {session_id}")
    if session_id:
        print(f"   ✓ PASS")
    else:
        print(f"   ✗ FAIL - No session_id")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ FAIL: {e}")
    sys.exit(1)

# Test 4: Step
print("\n4. Testing /step...")
try:
    response = requests.post(
        f"{BASE_URL}/step?session_id={session_id}",
        json={
            "reorder_quantities": [100],
            "transfers": []
        },
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    step_data = response.json()
    reward = step_data.get('reward')
    print(f"   Reward: {reward}")
    if reward is not None and 0 < reward < 1:
        print(f"   ✓ PASS - Partial credit reward")
    else:
        print(f"   ✗ FAIL - Invalid reward")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ FAIL: {e}")
    sys.exit(1)

print("\n=== ALL TESTS PASSED ===")
print(f"HF Space is fully functional with 3 tasks + graders")
