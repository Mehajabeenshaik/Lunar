#!/usr/bin/env python3
"""Comprehensive API workflow test (tests how submissions would actually call the API)."""

import requests
import json
import time

print("\n" + "="*80)
print("COMPREHENSIVE API WORKFLOW TEST (Submission-style)")
print("="*80)

# Test 1: Health
print("\n[1] Health Check Endpoint")
try:
    r = requests.get("http://localhost:7860/health", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"    ✅ Status: {r.status_code}")
        print(f"    ✅ Health: {data['status']}")
        print(f"    ✅ Version: {data['version']}")
    else:
        print(f"    ❌ Status: {r.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"    ❌ FAILED: {e}")
    exit(1)

# Test 2: Manifest (submission tests this)
print("\n[2] Manifest Endpoint (OpenEnv spec)")
try:
    r = requests.get("http://localhost:7860/manifest", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"    ✅ Status: {r.status_code}")
        print(f"    ✅ Name: {data['name']}")
        print(f"    ✅ Domains: {len(data['domains'])}")
        print(f"    ✅ Tasks: {len(data['tasks'])}")
        print(f"    ✅ Multi-agent: {data['features']['multi_agent']}")
    else:
        print(f"    ❌ Status: {r.status_code}")
        exit(1)
except Exception as e:
    print(f"    ❌ FAILED: {e}")
    exit(1)

# Test 3: Tasks endpoint
print("\n[3] Tasks Endpoint")
try:
    r = requests.get("http://localhost:7860/tasks", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"    ✅ Status: {r.status_code}")
        print(f"    ✅ Total tasks: {data['total']}")
        task_list = list(data['tasks'].keys())
        print(f"    ✅ First 3: {task_list[:3]}")
    else:
        print(f"    ❌ Status: {r.status_code}")
        exit(1)
except Exception as e:
    print(f"    ❌ FAILED: {e}")
    exit(1)

# Test 4: Reset with query params (submission format 1)
print("\n[4] Reset with Query Parameters")
try:
    r = requests.post("http://localhost:7860/reset?task=warehouse_easy", timeout=5)
    if r.status_code == 200:
        data = r.json()
        session_id_1 = data['session_id']
        print(f"    ✅ Status: {r.status_code}")
        print(f"    ✅ Session: {session_id_1[:8]}...")
        print(f"    ✅ Task: {data['task']}")
        print(f"    ✅ Observation keys: {list(data['observation'].keys())[:3]}...")
    else:
        print(f"    ❌ Status: {r.status_code}")
        print(f"    ❌ Response: {r.text}")
        exit(1)
except Exception as e:
    print(f"    ❌ FAILED: {e}")
    exit(1)

# Test 5: Reset with body JSON (submission format 2)
print("\n[5] Reset with Request Body")
try:
    r = requests.post(
        "http://localhost:7860/reset",
        json={"task": "warehouse_medium"},
        timeout=5
    )
    if r.status_code == 200:
        data = r.json()
        session_id_2 = data['session_id']
        print(f"    ✅ Status: {r.status_code}")
        print(f"    ✅ Session: {session_id_2[:8]}...")
        print(f"    ✅ Task: {data['task']}")
    else:
        print(f"    ❌ Status: {r.status_code}")
        print(f"    ❌ Response: {r.text}")
        exit(1)
except Exception as e:
    print(f"    ❌ FAILED: {e}")
    exit(1)

# Test 6: Step endpoint with proper action
print("\n[6] Step Endpoint (First action)")
try:
    action = {
        "reorder_quantities": [50.0, 50.0, 50.0],
        "transfers": [[0.0]*3 for _ in range(3)]
    }
    r = requests.post(
        f"http://localhost:7860/step?session_id={session_id_1}",
        json={"action": action},
        timeout=5
    )
    if r.status_code == 200:
        data = r.json()
        print(f"    ✅ Status: {r.status_code}")
        print(f"    ✅ Reward: {data['reward']:.3f}")
        print(f"    ✅ Range [0,1]: {0 <= data['reward'] <= 1}")
        print(f"    ✅ Done: {data['done']}")
    else:
        print(f"    ❌ Status: {r.status_code}")
        print(f"    ❌ Response: {r.text}")
        exit(1)
except Exception as e:
    print(f"    ❌ FAILED: {e}")
    exit(1)

# Test 7: Multiple steps
print("\n[7] Multiple Steps (Workflow)")
try:
    for i in range(2, 5):
        action = {
            "reorder_quantities": [50.0, 50.0, 50.0],
            "transfers": [[0.0]*3 for _ in range(3)]
        }
        r = requests.post(
            f"http://localhost:7860/step?session_id={session_id_1}",
            json={"action": action},
            timeout=5
        )
        if r.status_code == 200:
            data = r.json()
            print(f"    ✅ Step {i}: reward={data['reward']:.3f}")
        else:
            print(f"    ❌ Step {i} failed: {r.status_code}")
            exit(1)
except Exception as e:
    print(f"    ❌ FAILED: {e}")
    exit(1)

# Test 8: State endpoint
print("\n[8] State Endpoint")
try:
    r = requests.get(
        f"http://localhost:7860/state?session_id={session_id_1}",
        timeout=5
    )
    if r.status_code == 200:
        data = r.json()
        print(f"    ✅ Status: {r.status_code}")
        print(f"    ✅ Task: {data['task']}")
        print(f"    ✅ Episode rewards: {len(data['episode_rewards'])} steps")
    else:
        print(f"    ❌ Status: {r.status_code}")
        exit(1)
except Exception as e:
    print(f"    ❌ FAILED: {e}")
    exit(1)

# Test 9: Leaderboard
print("\n[9] Leaderboard Endpoint")
try:
    r = requests.get("http://localhost:7860/leaderboard?limit=5", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"    ✅ Status: {r.status_code}")
        print(f"    ✅ Total sessions: {data['total_sessions']}")
        if data['leaderboard']:
            entry = data['leaderboard'][0]
            best_reward = entry['best_reward']
            print(f"    ✅ Top reward: {best_reward:.3f}")
    else:
        print(f"    ❌ Status: {r.status_code}")
        exit(1)
except Exception as e:
    print(f"    ❌ FAILED: {e}")
    exit(1)

# Test 10: Sessions list
print("\n[10] Sessions Endpoint")
try:
    r = requests.get("http://localhost:7860/sessions", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"    ✅ Status: {r.status_code}")
        print(f"    ✅ Active sessions: {data['active_sessions']}")
    else:
        print(f"    ❌ Status: {r.status_code}")
        exit(1)
except Exception as e:
    print(f"    ❌ FAILED: {e}")
    exit(1)

# Test 11: Test all warehouse task variants (only 3 are implemented)
print("\n[11] Test All Warehouse Tasks")
warehouse_tasks = [
    "warehouse_easy",
    "warehouse_medium",
    "warehouse_hard"
]
try:
    for task in warehouse_tasks:
        r = requests.post(f"http://localhost:7860/reset?task={task}", timeout=5)
        if r.status_code == 200:
            print(f"    ✅ {task}: OK")
        else:
            print(f"    ❌ {task}: {r.status_code}")
            exit(1)
except Exception as e:
    print(f"    ❌ FAILED: {e}")
    exit(1)

print("\n" + "="*80)
print("✅ ALL API WORKFLOWS PASSED - Ready for submission!")
print("="*80 + "\n")
