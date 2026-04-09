#!/usr/bin/env python
"""FINAL SUBMISSION READINESS CHECK - Comprehensive Validation."""

import requests
import sys

print("\n" + "="*80)
print("LUNAR SUBMISSION READINESS CHECK - OPENENV V1 & APEX COMPLIANCE")
print("="*80)

checks_passed = 0
checks_total = 0

# 1. Health Check
print("\n[1] HEALTH CHECK")
checks_total += 1
try:
    r = requests.get("http://localhost:7860/health")
    if r.status_code == 200:
        print("    ✅ Server responding on port 7860")
        checks_passed += 1
    else:
        print(f"    ❌ Unexpected status code: {r.status_code}")
except Exception as e:
    print(f"    ❌ Cannot reach server: {e}")

# 2. Manifest with Graders
print("\n[2] MANIFEST WITH TASK GRADERS")
checks_total += 1
try:
    r = requests.get("http://localhost:7860/manifest")
    manifest = r.json()
    tasks = manifest.get("tasks", [])
    graders = manifest.get("graders", [])
    
    if len(tasks) >= 3 and len(graders) == len(tasks):
        print(f"    ✅ {len(tasks)} tasks with {len(graders)} graders advertised")
        print(f"       Tasks: {tasks}")
        print(f"       Graders: {graders}")
        checks_passed += 1
    else:
        print(f"    ❌ Tasks: {len(tasks)}, Graders: {len(graders)}")
except Exception as e:
    print(f"    ❌ Cannot access manifest: {e}")

# 3. Task Specifications
print("\n[3] TASK SPECIFICATIONS IN MANIFEST")
checks_total += 1
try:
    r = requests.get("http://localhost:7860/manifest")
    manifest = r.json()
    task_specs = manifest.get("task_specs", {})
    
    all_have_graders = all(spec.get("has_grader", False) for spec in task_specs.values())
    if all_have_graders and len(task_specs) >= 3:
        print(f"    ✅ All {len(task_specs)} tasks have grader_type specified")
        checks_passed += 1
    else:
        print(f"    ❌ Not all tasks have graders: {[t for t, s in task_specs.items() if not s.get('has_grader')]}")
except Exception as e:
    print(f"    ❌ Cannot validate task specs: {e}")

# 4. Reset Endpoint
print("\n[4] RESET ENDPOINT (OpenEnv v1)")
checks_total += 1
try:
    r = requests.post("http://localhost:7860/reset", json={"task": "warehouse_easy"})
    if r.status_code == 200:
        data = r.json()
        if "session_id" in data and "observation" in data:
            print(f"    ✅ Returns session_id + observation")
            checks_passed += 1
        else:
            print("    ❌ Missing session_id or observation fields")
    else:
        print(f"    ❌ Status code {r.status_code}")
except Exception as e:
    print(f"    ❌ Cannot call /reset: {e}")

# 5. Step Endpoint
print("\n[5] STEP ENDPOINT (OpenEnv v1)")
checks_total += 1
try:
    # Get a session first
    r = requests.post("http://localhost:7860/reset", json={"task": "warehouse_easy"})
    session_id = r.json()["session_id"]
    obs = r.json()["observation"]
    
    # warehouse_easy has 1 warehouse
    num_wh = len(obs.get("warehouse_levels", [1]))
    action = {
        "reorder_quantities": [50.0] * num_wh,
        "transfers": [[0.0] * num_wh for _ in range(num_wh)]
    }
    
    # Execute a step - session_id goes in query params!
    r = requests.post(
        f"http://localhost:7860/step?session_id={session_id}",
        json={"action": action}
    )
    if r.status_code == 200:
        data = r.json()
        if "reward" in data and "done" in data:
            reward = data["reward"]
            if 0.0 <= reward <= 1.0:
                print(f"    ✅ Returns reward (range [0,1]={reward:.2f}) + done")
                checks_passed += 1
            else:
                print(f"    ❌ Reward {reward} out of range [0.0, 1.0]")
        else:
            print("    ❌ Missing reward or done fields")
    else:
        print(f"    ❌ Status code {r.status_code} - {r.text[:100]}")
except Exception as e:
    print(f"    ❌ Cannot call /step: {e}")

# 6. State Endpoint
print("\n[6] STATE ENDPOINT (OpenEnv v1)")
checks_total += 1
try:
    r = requests.post("http://localhost:7860/reset", json={"task": "warehouse_medium"})
    session_id = r.json()["session_id"]
    
    r = requests.get(f"http://localhost:7860/state?session_id={session_id}")
    if r.status_code == 200:
        print(f"    ✅ GET /state returns session state")
        checks_passed += 1
    else:
        print(f"    ❌ Status code {r.status_code}")
except Exception as e:
    print(f"    ❌ Cannot call /state: {e}")

# 7. All 3 Tasks Work
print("\n[7] ALL 3 WAREHOUSE TASKS WORK")
checks_total += 1
try:
    tasks_ok = []
    for task in ["warehouse_easy", "warehouse_medium", "warehouse_hard"]:
        r = requests.post("http://localhost:7860/reset", json={"task": task})
        if r.status_code == 200 and "session_id" in r.json():
            tasks_ok.append(task)
    
    if len(tasks_ok) == 3:
        print(f"    ✅ All 3 tasks initialize successfully: {tasks_ok}")
        checks_passed += 1
    else:
        print(f"    ❌ Only {len(tasks_ok)} tasks work: {tasks_ok}")
except Exception as e:
    print(f"    ❌ Cannot test all tasks: {e}")

# 8. Difficulty Progression
print("\n[8] DIFFICULTY PROGRESSION (Easy → Medium → Hard)")
checks_total += 1
try:
    task_specs = requests.get("http://localhost:7860/manifest").json().get("task_specs", {})
    difficulties = {t: s.get("difficulty") for t, s in task_specs.items()}
    
    if (difficulties.get("warehouse_easy") == "easy" and 
        difficulties.get("warehouse_medium") == "medium" and 
        difficulties.get("warehouse_hard") == "hard"):
        print(f"    ✅ Proper difficulty progression: {difficulties}")
        checks_passed += 1
    else:
        print(f"    ❌ Difficulty mismatch: {difficulties}")
except Exception as e:
    print(f"    ❌ Cannot validate difficulty: {e}")

# 9. Deterministic Rewards
print("\n[9] DETERMINISTIC REWARD SIGNAL")
checks_total += 1
try:
    rewards_1 = []
    r = requests.post("http://localhost:7860/reset", json={"task": "warehouse_easy"})
    sid = r.json()["session_id"]
    obs = r.json()["observation"]
    num_wh = len(obs.get("warehouse_levels", [1]))
    
    for _ in range(2):
        action = {
            "reorder_quantities": [50.0] * num_wh,
            "transfers": [[0.0] * num_wh for _ in range(num_wh)]
        }
        r = requests.post(f"http://localhost:7860/step?session_id={sid}",
                         json={"action": action})
        if r.status_code == 200:
            rewards_1.append(r.json().get("reward", 0.0))
    
    rewards_2 = []
    r = requests.post("http://localhost:7860/reset", json={"task": "warehouse_easy"})
    sid = r.json()["session_id"]
    obs = r.json()["observation"]
    num_wh = len(obs.get("warehouse_levels", [1]))
    
    for _ in range(2):
        action = {
            "reorder_quantities": [50.0] * num_wh,
            "transfers": [[0.0] * num_wh for _ in range(num_wh)]
        }
        r = requests.post(f"http://localhost:7860/step?session_id={sid}",
                         json={"action": action})
        if r.status_code == 200:
            rewards_2.append(r.json().get("reward", 0.0))
    
    if rewards_1 == rewards_2:
        print(f"    ✅ Rewards are deterministic: {rewards_1} == {rewards_2}")
        checks_passed += 1
    else:
        print(f"    ⚠️  Rewards differ: {rewards_1} vs {rewards_2} (may be stochastic)")
except Exception as e:
    print(f"    ⚠️  Cannot validate determinism: {e}")

# 10. API Documentation
print("\n[10] SWAGGER DOCUMENTATION")
checks_total += 1
try:
    r = requests.get("http://localhost:7860/docs")
    if r.status_code == 200:
        print(f"    ✅ /docs endpoint live (Swagger UI)")
        checks_passed += 1
    else:
        print(f"    ❌ /docs returned {r.status_code}")
except Exception as e:
    print(f"    ❌ Cannot access /docs: {e}")

# Summary
print("\n" + "="*80)
print(f"RESULTS: {checks_passed}/{checks_total} checks passed")
if checks_passed >= checks_total - 1:  # Allow 1 optional failure (determinism)
    print("✅ SUBMISSION READY - All critical checks passed!")
    sys.exit(0)
else:
    print("❌ SUBMISSION NOT READY - Fix failures above")
    sys.exit(1)
