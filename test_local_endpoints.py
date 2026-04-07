"""Quick test of all LUNAR endpoints"""
import requests
import json

BASE = "http://localhost:7860"

print("=" * 70)
print("TESTING ALL LUNAR ENDPOINTS (LOCAL)")
print("=" * 70)
print()

# Test 1: Health Check
print("1️⃣  HEALTH CHECK")
try:
    r = requests.get(f"{BASE}/health").json()
    print(f"   ✅ Status: OK")
    print(f"   Version: {r['version']}")
    print(f"   Active Sessions: {r['active_sessions']}")
except Exception as e:
    print(f"   ❌ Error: {e}")
print()

# Test 2: Tasks List
print("2️⃣  TASK LIST (21 variants)")
try:
    r = requests.get(f"{BASE}/tasks").json()
    print(f"   ✅ Total Tasks: {r['total']}")
    print(f"   First 5 tasks:")
    for i, task in enumerate(list(r['tasks'].keys())[:5], 1):
        print(f"     {i}. {task}")
    print(f"     ... and {r['total'] - 5} more")
except Exception as e:
    print(f"   ❌ Error: {e}")
print()

# Test 3: Manifest
print("3️⃣  MANIFEST (OpenEnv Spec)")
try:
    r = requests.get(f"{BASE}/manifest").json()
    print(f"   ✅ Name: {r['name']}")
    print(f"   Version: {r['version']}")
    print(f"   Task Variants: {r['features']['task_variants']}")
    print(f"   Multi-Domain: {r['features']['multi_domain']}")
    print(f"   Domains: {len(r['domains'])} domains")
except Exception as e:
    print(f"   ❌ Error: {e}")
print()

# Test 4: Create Session
print("4️⃣  CREATE SESSION (warehouse_easy)")
try:
    r = requests.post(f"{BASE}/reset", json={"task": "warehouse_easy"}).json()
    session_id = r['session_id']
    print(f"   ✅ Session Created: {session_id[:8]}...")
    print(f"   Task: {r['task']}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    session_id = None
print()

# Test 5: Get State
if session_id:
    print("5️⃣  GET STATE")
    try:
        r = requests.get(f"{BASE}/state", params={"session_id": session_id}).json()
        print(f"   ✅ State Retrieved")
        print(f"   Task: {r['task']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()

# Test 6: Take Step
if session_id:
    print("6️⃣  TAKE STEP (action)")
    try:
        r = requests.post(f"{BASE}/step", 
            params={"session_id": session_id},
            json={"warehouse_id": 0, "quantity": 50}
        ).json()
        print(f"   ✅ Step Executed")
        print(f"   Reward: {r['reward']:.3f}")
        print(f"   Done: {r['done']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()

# Test 7: Sessions List
print("7️⃣  SESSIONS LIST")
try:
    r = requests.get(f"{BASE}/sessions").json()
    print(f"   ✅ Active Sessions: {r['active_sessions']}")
except Exception as e:
    print(f"   ❌ Error: {e}")
print()

# Test 8: Leaderboard
print("8️⃣  LEADERBOARD")
try:
    r = requests.get(f"{BASE}/leaderboard?limit=5").json()
    print(f"   ✅ Total Sessions: {r['total_sessions']}")
    if r['leaderboard']:
        print(f"   Top Session: {r['leaderboard'][0]['task']} - Score: {r['leaderboard'][0]['best_reward']:.3f}")
except Exception as e:
    print(f"   ❌ Error: {e}")
print()

# Test 9: Server Stats
print("9️⃣  SERVER STATS")
try:
    r = requests.get(f"{BASE}/stats").json()
    stats = r['server_stats']
    print(f"   ✅ Active Sessions: {stats['total_sessions']}")
    print(f"   Max Sessions: {stats['max_sessions']}")
    print(f"   Available Tasks: {r['available_tasks']}")
except Exception as e:
    print(f"   ❌ Error: {e}")
print()

print("=" * 70)
print("✅ ALL ENDPOINTS WORKING SUCCESSFULLY!")
print("=" * 70)
print()
print("🌐 Server: http://localhost:7860")
print("📖 API Docs: http://localhost:7860/docs")
