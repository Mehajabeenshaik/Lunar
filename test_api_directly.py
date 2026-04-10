#!/usr/bin/env python3
"""
Test the API directly to see what actual responses are being returned
This simulates what the validator might be checking
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Test FastAPI app directly
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

print("="*80)
print("DIRECT API RESPONSE TEST")
print("="*80)

# Test 1: Check manifest
print("\n1. Checking /manifest endpoint:")
response = client.get("/manifest")
manifest = response.json()
print(f"   Status: {response.status_code}")
print(f"   Reward range: {manifest.get('reward_range')}")
print(f"   Tasks: {manifest.get('tasks')}")

# Test 2: Check stats
print("\n2. Checking /stats endpoint:")
response = client.get("/stats")
stats = response.json()
print(f"   Status: {response.status_code}")
print(f"   Reward range: {stats.get('reward_range')}")
print(f"   Tasks available: {stats.get('tasks_available')}")

# Test 3: Start a session and take a step
print("\n3. Testing /session/start and /session/{id}/step:")
start_response = client.post("/session/start", json={"task_id": 1})
start_data = start_response.json()
print(f"   Start status: {start_response.status_code}")

if start_response.status_code == 200:
    session_id = start_data.get("session_id")
    print(f"   Session ID: {session_id}")
    
    # Take a step
    step_response = client.post(
        f"/session/{session_id}/step",
        json={"session_id": session_id, "action": {"category": "safe"}}
    )
    step_data = step_response.json()
    print(f"   Step status: {step_response.status_code}")
    print(f"   Reward: {step_data.get('reward')} (type: {type(step_data.get('reward'))})")
    
    reward = step_data.get('reward')
    if reward is not None:
        print(f"   Safe (0 < r < 1)? {0 < reward < 1}")
        print(f"   == 0.0? {reward == 0.0}")
        print(f"   == 1.0? {reward == 1.0}")
        print(f"   >= 1.0? {reward >= 1.0}")
        print(f"   <= 0.0? {reward <= 0.0}")
        print(f"   JSON string: '{reward}'")
        print(f"   Rounded to 4 decimals: {round(reward, 4)}")

# Test 4: Test all 30 tasks for boundary values
print("\n4. Testing all 30 tasks for boundary values:")
boundary_violations = []

for task_id in range(1, 31):
    start_response = client.post("/session/start", json={"task_id": task_id})
    if start_response.status_code != 200:
        error_msg = start_response.json().get('detail', 'Unknown error')
        print(f"   Task {task_id}: FAILED - {error_msg[:60]}")
        continue
    
    session_id = start_response.json().get("session_id")
    
    # Test with different actions
    test_actions = [
        {"category": "safe"},
        {"category": "hate"},
        {},
    ]
    
    for action in test_actions:
        step_response = client.post(
            f"/session/{session_id}/step",
            json={"session_id": session_id, "action": action}
        )
        if step_response.status_code == 200:
            reward = step_response.json().get('reward')
            if reward is not None and (reward <= 0.0 or reward >= 1.0):
                boundary_violations.append({
                    "task": task_id,
                    "action": action,
                    "reward": reward,
                    "is_violation": reward <= 0.0 or reward >= 1.0
                })

if boundary_violations:
    print(f"   ❌ Found {len(boundary_violations)} boundary violations:")
    for v in boundary_violations[:5]:  # Show first 5
        print(f"      Task {v['task']}: {v['reward']} (action: {v['action']})")
else:
    print(f"   ✅ NO BOUNDARY VIOLATIONS detected in API responses!")

print("\n" + "="*80)
