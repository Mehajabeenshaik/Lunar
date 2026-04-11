#!/usr/bin/env python3
"""
Final comprehensive verification before submission
Checks all 30 tasks for:
1. Successful initialization
2. Safe reward values (0 < r < 1)
3. Consistent metadata
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from app import app
import json

client = TestClient(app)

print("="*80)
print("FINAL COMPREHENSIVE VERIFICATION BEFORE SUBMISSION")
print("="*80)

# 1. Verify manifest
print("\n1. MANIFEST VERIFICATION:")
response = client.get("/manifest")
if response.status_code != 200:
    print("   FAILED: /manifest not accessible")
    sys.exit(1)

manifest = response.json()
print(f"   OK Manifest accessible")
print(f"   OK Version: {manifest.get('version')}")
print(f"   OK Tasks: {manifest.get('tasks')}")
print(f"   OK Reward range: {manifest.get('reward_range')}")

if manifest.get('tasks') != 30:
    print("   ERROR: tasks should be 30")
    sys.exit(1)

if manifest.get('reward_range') != [0.001, 0.999]:
    print("   ERROR: reward_range should be [0.001, 0.999]")
    sys.exit(1)

# 2. Test all 30 tasks
print("\n2. TASK INITIALIZATION TEST:")
task_results = {}
all_safe = True

for task_id in range(1, 31):
    # Start session
    start_response = client.post("/session/start", json={"task_id": task_id})
    if start_response.status_code != 200:
        print(f"   FAILED Task {task_id:2d}: Cannot start session")
        task_results[task_id] = "FAILED"
        all_safe = False
        continue
    
    session_id = start_response.json().get("session_id")
    
    # Take multiple steps to test rewards
    step_rewards = []
    for step in range(3):
        step_response = client.post(
            f"/session/{session_id}/step",
            json={"session_id": session_id, "action": {"category": "safe"}}
        )
        if step_response.status_code != 200:
            print(f"   FAILED Task {task_id:2d}: Cannot execute step {step}")
            task_results[task_id] = "FAILED"
            all_safe = False
            break
        
        reward = step_response.json().get('reward')
        step_rewards.append(reward)
        
        # Check bounds
        if reward is None or reward <= 0.0 or reward >= 1.0:
            print(f"   FAILED Task {task_id:2d}: Boundary violation! reward={reward}")
            task_results[task_id] = f"BOUNDARY({reward})"
            all_safe = False
            break
    
    if all_safe or task_id not in task_results:
        avg_reward = sum(step_rewards) / len(step_rewards) if step_rewards else None
        status = f"OK (avg={avg_reward:.3f})" if avg_reward else "OK"
        task_results[task_id] = status
        print(f"   OK Task {task_id:2d}: {status}")

print("\n" + "="*80)
print("VERIFICATION SUMMARY")
print("="*80)

passed = sum(1 for v in task_results.values() if v.startswith("OK"))
failed = len(task_results) - passed

print(f"\nTasks passed: {passed}/30")
print(f"Tasks failed: {failed}/30")

if failed > 0:
    print("\nFailed tasks:")
    for task_id, status in task_results.items():
        if not status.startswith("OK"):
            print(f"  - Task {task_id}: {status}")

print("\n" + "="*80)

if all_safe and passed == 30:
    print("SUCCESS - ALL SYSTEMS GO FOR SUBMISSION!")
    print("="*80)
    sys.exit(0)
else:
    print("FAILED - Issues detected")
    print("="*80)
    sys.exit(1)
