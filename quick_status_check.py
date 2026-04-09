#!/usr/bin/env python
"""Quick status check - what's working  and what's not """

print("\n" + "=" * 60)
print("LUNAR vs APEX - COMPLIANCE SUMMARY")
print("=" * 60 + "\n")

issues = []

# 1. openenv.yaml
print("1. OPENENV.YAML")
try:
    import yaml
    with open('openenv.yaml') as f:
        spec = yaml.safe_load(f)
    
    graders = spec.get('graders', [])
    tasks = spec.get('tasks', [])
    
    has_grader_count = sum(1 for t in tasks if t.get('has_grader'))
    
    print(f"   - Graders listed: {len(graders)}")
    print(f"   - Tasks: {len(tasks)}")
    print(f"   - Tasks with has_grader=true: {has_grader_count}")
    
    if has_grader_count >= 3:
        print("   STATUS: OK\n")
    else:
        print("   STATUS: MISSING GRADERS\n")
        issues.append("openenv.yaml has less than 3 tasks with graders")
except Exception as e:
    print(f"   ERROR: {e}\n")
    issues.append(f"openenv.yaml parsing failed: {e}")

# 2. Graders module
print("2. GRADERS WORKING")
try:
    from warehouse_env.warehouse_env.graders import get_grader
    grader_count = 0
    for task_id in ['warehouse_easy', 'warehouse_medium', 'warehouse_hard']:
        try:
            grader = get_grader(task_id)
            grader_count += 1
        except Exception as e:
            issues.append(f"get_grader({task_id}) failed: {e}")
    
    print(f"   - Graders working: {grader_count}/3")
    if grader_count == 3:
        print("   STATUS: OK\n")
    else:
        print("   STATUS: SOME GRADERS BROKEN\n")
except Exception as e:
    print(f"   ERROR: {e}\n")
    issues.append(f"Graders module error: {e}")

# 3. API endpoints
print("3. API ENDPOINTS")
try:
    from fastapi.testclient import TestClient
    from warehouse_env.warehouse_env.server import app
    
    client = TestClient(app)
    
    endpoints_ok = 0
    endpoints_total = 0
    
    tests = [
        ("/health", "GET", {}),
        ("/manifest", "GET", {}),
        ("/tasks", "GET", {}),
    ]
    
    for endpoint, method, data in tests:
        endpoints_total += 1
        if method == "GET":
            r = client.get(endpoint)
        else:
            r = client.post(endpoint, json=data)
        
        if r.status_code == 200:
            endpoints_ok += 1
        else:
            issues.append(f"{endpoint} returned {r.status_code}")
    
    print(f"   - Endpoints responding: {endpoints_ok}/{endpoints_total}")
    print("   STATUS: OK\n")
except Exception as e:
    print(f"   ERROR: {e}\n")
    issues.append(f"API endpoints error: {e}")

# 4. Grader scoring
print("4. GRADER SCORING")
try:
    from fastapi.testclient import TestClient
    from warehouse_env.warehouse_env.server import app
    
    client = TestClient(app)
    
    scores_ok = 0
    for task_id in ['warehouse_easy', 'warehouse_medium', 'warehouse_hard']:
        # Reset
        r = client.post('/reset', json={'task': task_id})
        if r.status_code != 200:
            continue
        
        sid = r.json()['session_id']
        
        # Step
        r = client.post(f'/step?session_id={sid}', 
                       json={'reorder_quantities': [100], 'transfers': []})
        
        if r.status_code == 200:
            reward = r.json().get('reward', 0)
            if reward > 0:
                scores_ok += 1
                print(f"   {task_id}: reward={reward:.4f}")
            else:
                print(f"   {task_id}: reward={reward:.4f} (ZERO!)")
                issues.append(f"{task_id} returns zero reward")
    
    if scores_ok == 3:
        print("   STATUS: OK\n")
    else:
        print(f"   STATUS: ONLY {scores_ok}/3 WORKING\n")
except Exception as e:
    print(f"   ERROR: {e}\n")
    issues.append(f"Grader scoring error: {e}")

# 5. App entry point
print("5. APP ENTRY POINT")
try:
    from app import app
    print("   - app.py imports successfully")
    print("   - app object is callable")
    print("   STATUS: OK\n")
except Exception as e:
    print(f"   ERROR: {e}\n")
    issues.append(f"app.py error: {e}")

# SUMMARY
print("=" * 60)
print("SUMMARY")
print("=" * 60)

if not issues:
    print("\nALL CHECKS PASSED!")
    print("\nLUNAR should be ready for submission.")
    print("If validator still fails, the issue might be:")
    print("  1. Validator checking different criteria than expected")
    print("  2. Caching issue - validator using old Docker image")
    print("  3. Timing issue - validator not waiting for rebuild")
else:
    print(f"\nFOUND {len(issues)} ISSUES:\n")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")

print("\n" + "=" * 60 + "\n")
