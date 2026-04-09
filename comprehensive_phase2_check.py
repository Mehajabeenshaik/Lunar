#!/usr/bin/env python
"""Comprehensive check of all potential Phase 2 blockers"""
from fastapi.testclient import TestClient
from warehouse_env.warehouse_env.server import app
import json

client = TestClient(app)

print("=" * 80)
print("COMPREHENSIVE PHASE 2 BLOCKER CHECK")
print("=" * 80)

issues = []

# 1. Check /manifest schema
print("\n1. MANIFEST ENDPOINT")
r = client.get('/manifest')
if r.status_code != 200:
    issues.append(f"❌ /manifest returns {r.status_code} (should be 200)")
else:
    m = r.json()
    
    # Check required fields
    required_manifest_fields = ['version', 'name', 'description', 'tasks', 'task_specs', 'graders']
    for field in required_manifest_fields:
        if field not in m:
            issues.append(f"❌ /manifest missing field: {field}")
    
    # Check graders advertised
    graders = m.get('graders', [])
    if len(graders) != 3:
        issues.append(f"❌ /manifest advertises {len(graders)} graders (need 3)")
    
    # Check task_specs includes grader info
    task_specs = m.get('task_specs', {})
    for task_id in ['warehouse_easy', 'warehouse_medium', 'warehouse_hard']:
        if task_id not in task_specs:
            issues.append(f"❌ /manifest missing task_spec for {task_id}")
        else:
            spec = task_specs[task_id]
            if not spec.get('has_grader'):
                issues.append(f"❌ /manifest {task_id} has_grader=false")
            if 'grader_type' not in spec:
                issues.append(f"❌ /manifest {task_id} missing grader_type")

if not issues:
    print("   ✓ /manifest structure correct")

# 2. Check /tasks endpoint
print("\n2. TASKS ENDPOINT")
r = client.get('/tasks')
if r.status_code != 200:
    issues.append(f"❌ /tasks returns {r.status_code} (should be 200)")
else:
    t = r.json()
    tasks = t.get('tasks', {})
    
    for task_id in ['warehouse_easy', 'warehouse_medium', 'warehouse_hard']:
        if task_id not in tasks:
            issues.append(f"❌ /tasks missing {task_id}")
        else:
            spec = tasks[task_id]
            if not spec.get('has_grader'):
                issues.append(f"❌ /tasks {task_id} has_grader=false")

if not issues:
    print("   ✓ /tasks structure correct")

# 3. Check /reset endpoint returns correct format
print("\n3. RESET ENDPOINT")
r = client.post('/reset', json={'task': 'warehouse_easy'})
if r.status_code != 200:
    issues.append(f"❌ /reset returns {r.status_code}")
else:
    data = r.json()
    if 'session_id' not in data:
        issues.append("❌ /reset missing session_id")
    if 'observation' not in data:
        issues.append("❌ /reset missing observation")
    else:
        obs = data['observation']
        required_obs_fields = ['warehouse_levels', 'demand_forecast', 'supplier_status', 'day']
        for field in required_obs_fields:
            if field not in obs:
                issues.append(f"❌ reset observation missing {field}")

if not issues:
    print("   ✓ /reset returns correct format")

# 4. Check /step endpoint 
print("\n4. STEP ENDPOINT")
r = client.post('/reset', json={'task': 'warehouse_easy'})
session_id = r.json()['session_id']

r = client.post(
    f'/step?session_id={session_id}',
    json={'reorder_quantities': [100], 'transfers': []}
)

if r.status_code != 200:
    issues.append(f"❌ /step returns {r.status_code}")
else:
    data = r.json()
    if 'reward' not in data:
        issues.append("❌ /step missing reward")
    if 'done' not in data:
        issues.append("❌ /step missing done")
    if 'observation' not in data:
        issues.append("❌ /step missing observation")
    if 'info' not in data:
        issues.append("❌ /step missing info")
    
    reward = data.get('reward', 0)
    if reward <= 0:
        issues.append(f"❌ /step returned reward={reward} (should be > 0)")

if not issues:
    print("   ✓ /step returns correct format with positive rewards")

# 5. Check /health endpoint
print("\n5. HEALTH ENDPOINT")
try:
    r = client.get('/health')
    if r.status_code != 200:
        issues.append(f"❌ /health returns {r.status_code}")
    else:
        print("   ✓ /health returns 200")
except:
    issues.append("❌ /health endpoint missing or broken")

# 6. Check openenv.yaml
print("\n6. OPENENV.YAML")
try:
    import yaml
    with open('openenv.yaml', 'r') as f:
        spec = yaml.safe_load(f)
    
    if 'graders' not in spec:
        issues.append("❌ openenv.yaml missing graders field")
    elif len(spec.get('graders', [])) != 3:
        issues.append(f"❌ openenv.yaml has {len(spec.get('graders', []))} graders (need 3)")
    
    tasks = spec.get('tasks', [])
    for task in tasks:
        if not task.get('has_grader'):
            issues.append(f"❌ openenv.yaml {task.get('id')} has_grader=false")
    
    if not issues:
        print("   ✓ openenv.yaml correctly configured")
except Exception as e:
    issues.append(f"❌ Error reading openenv.yaml: {e}")

# 7. Check inference.py  
print("\n7. INFERENCE.PY")
try:
    with open('inference.py', 'r') as f:
        content = f.read()
    
    required_functions = ['main()', 'reset_environment()', 'step_environment()', 'generate_action()']
    for func in required_functions:
        if func not in content:
            issues.append(f"❌ inference.py missing {func}")
    
    if 'print(' not in content or '[START]' not in content or '[END]' not in content:
        issues.append("❌ inference.py missing required logging statements")
    
    if not issues:
        print("   ✓ inference.py has all required functions")
except Exception as e:
    issues.append(f"❌ Error reading inference.py: {e}")

# 8. Check Dockerfile
print("\n8. DOCKERFILE")
try:
    with open('Dockerfile', 'r') as f:
        content = f.read()
    
    required_commands = ['FROM', 'WORKDIR', 'COPY', 'RUN pip', 'EXPOSE', 'CMD']
    for cmd in required_commands:
        if cmd not in content:
            issues.append(f"❌ Dockerfile missing {cmd}")
    
    if '7860' not in content:
        issues.append("❌ Dockerfile doesn't expose port 7860")
    
    if not issues:
        print("   ✓ Dockerfile structure correct")
except Exception as e:
    issues.append(f"❌ Error reading Dockerfile: {e}")

print("\n" + "=" * 80)
if issues:
    print(f"FOUND {len(issues)} POTENTIAL ISSUES:")
    for issue in issues:
        print(f"  {issue}")
else:
    print("✅ NO ISSUES FOUND - ALL PHASE 2 REQUIREMENTS MET")
print("=" * 80)
