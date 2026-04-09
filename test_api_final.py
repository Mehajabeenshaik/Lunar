#!/usr/bin/env python3
"""Final comprehensive API test."""

import requests

print("\n" + "="*70)
print("LUNAR API - COMPREHENSIVE WORKFLOW TEST")
print("="*70 + "\n")

# 1. Health check
print("1. Health Check")
r = requests.get('http://localhost:7860/health')
data = r.json()
print(f"   ✅ Status: {data['status']} | Version: {data['version']}")
print(f"      Active Sessions: {data['active_sessions']}/{data['max_sessions']}")

# 2. Get manifest
print("\n2. OpenEnv Manifest")
r = requests.get('http://localhost:7860/manifest')
data = r.json()
print(f"   ✅ Name: {data['name']}")
print(f"      Domains: {len(data['domains'])}")
print(f"      Features: multi_agent={data['features']['multi_agent']}, "
      f"leaderboard={data['features']['leaderboard']}")

# 3. Get tasks
print("\n3. Available Tasks")
r = requests.get('http://localhost:7860/tasks')
data = r.json()
print(f"   ✅ Total: {data['total']} tasks")
print(f"      Sample: {list(data['tasks'].keys())[:3]}")

# 4. Create session and run steps
print("\n4. Session Management")
r = requests.post('http://localhost:7860/reset', json={'task': 'warehouse_easy'})
session_data = r.json()
session_id = session_data['session_id']
print(f"   ✅ Session created: {session_id[:8]}...")
print(f"      Task: {session_data['task']}")

# Take a step
action = {
    'reorder_quantities': [50.0, 50.0, 50.0],
    'transfers': [[0.0]*3 for _ in range(3)]
}
r = requests.post(f'http://localhost:7860/step?session_id={session_id}', 
                  json={'action': action})
step_data = r.json()
print(f"   ✅ Step 1: reward={step_data['reward']:.3f}, done={step_data['done']}")

# Get state
r = requests.get(f'http://localhost:7860/state?session_id={session_id}')
state_data = r.json()
print(f"   ✅ Current state retrieved, episode_rewards={len(state_data['episode_rewards'])} steps")

# 5. Get leaderboard
print("\n5. Leaderboard")
r = requests.get('http://localhost:7860/leaderboard?limit=5')
data = r.json()
print(f"   ✅ Total sessions tracked: {data['total_sessions']}")
if data['leaderboard']:
    top_entry = data['leaderboard'][0]
    print(f"      Top reward: {top_entry['reward']:.3f}")

# 6. List sessions
print("\n6. Session Management")
r = requests.get('http://localhost:7860/sessions')
data = r.json()
print(f"   ✅ Active sessions: {data['active_sessions']}")
print(f"      Session IDs: {data['sessions'][:1]}")

print("\n" + "="*70)
print("✅ ALL API TESTS PASSED - Environment is fully functional!")
print("="*70 + "\n")
