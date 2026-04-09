#!/usr/bin/env python
"""Final comprehensive diagnostic - logs everything about grader configuration"""
import sys
import json

print("\n" + "=" * 80)
print("COMPREHENSIVE GRADER CONFIGURATION DIAGNOSTIC")
print("=" * 80)

# 1. Check Python environment
print("\n1. PYTHON ENVIRONMENT")
print(f"  Python: {sys.version}")
print(f"  Executable: {sys.executable}")

# 2. Check imports
print("\n2. MODULE IMPORTS")
try:
    import numpy
    print(f"  ✓ numpy: {numpy.__version__}")
except ImportError as e:
    print(f"  ✗ numpy: {e}")

try:
    import pydantic
    print(f"  ✓ pydantic: {pydantic.__version__}")
except ImportError as e:
    print(f"  ✗ pydantic: {e}")

try:
    import fastapi
    print(f"  ✓ fastapi: {fastapi.__version__}")
except ImportError as e:
    print(f"  ✗ fastapi: {e}")

try:
    import yaml
    print(f"  ✓ pyyaml: installed")
except ImportError as e:
    print(f"  ✗ pyyaml: {e}")

# 3. Check openenv.yaml
print("\n3. OPENENV.YAML")
try:
    import yaml
    with open('openenv.yaml') as f:
        spec = yaml.safe_load(f)
    
    graders = spec.get('graders', [])
    tasks = spec.get('tasks', [])
    
    print(f"  ✓ File found and parseable")
    print(f"  graders field: {len(graders)} items")
    print(f"    Items: {graders}")
    print(f"  tasks section: {len(tasks)} tasks")
    
    grader_count = 0
    for task in tasks:
        has_grader = task.get('has_grader')
        if has_grader:
            grader_count += 1
            print(f"    ✓ {task['id']}: has_grader=True")
        else:
            print(f"    ✗ {task['id']}: has_grader=False or missing")
    
    if grader_count >= 3:
        print(f"\n  ✓ OPENENV.YAML VALID: {grader_count}/3 tasks have graders")
    else:
        print(f"\n  ✗ OPENENV.YAML INVALID: Only {grader_count}/3 tasks have graders")
        
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# 4. Check task_config.py
print("\n4. TASK CONFIG")
try:
    from warehouse_env.warehouse_env.task_config import get_task_variants, is_valid_task
    
    tasks = get_task_variants()
    print(f"  ✓ Imported successfully")
    print(f"  Task count: {len(tasks)}")
    
    for task_id in tasks:
        valid = is_valid_task(task_id)
        if valid:
            print(f"    ✓ {task_id}: valid")
        else:
            print(f"    ✗ {task_id}: invalid")
            
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# 5. Check graders module
print("\n5. GRADERS MODULE")
try:
    from warehouse_env.warehouse_env.graders import get_grader, EasyTaskGrader, MediumTaskGrader, HardTaskGrader
    
    print(f"  ✓ Module imported successfully")
    
    for task_id in ['warehouse_easy', 'warehouse_medium', 'warehouse_hard']:
        try:
            grader = get_grader(task_id)
            grader_class = grader.__class__.__name__
            print(f"    ✓ {task_id}: {grader_class}")
        except Exception as e:
            print(f"    ✗ {task_id}: {e}")
            
except Exception as e:
    print(f"  ✗ Error importing graders: {e}")
    import traceback
    traceback.print_exc()

# 6. Check /manifest endpoint
print("\n6. /MANIFEST ENDPOINT")
try:
    from fastapi.testclient import TestClient
    from warehouse_env.warehouse_env.server import app
    
    client = TestClient(app)
    r = client.get('/manifest')
    
    if r.status_code == 200:
        m = r.json()
        graders = m.get('graders', [])
        features = m.get('features', {})
        tasks_with_graders_count = features.get('tasks_with_graders', 0)
        task_specs = m.get('task_specs', {})
        
        print(f"  ✓ Status 200")
        print(f"  graders field: {len(graders)} items: {graders}")
        print(f"  features.tasks_with_graders: {tasks_with_graders_count}")
        print(f"  task_specs:")
        
        spec_grader_count = 0
        for task_id, spec in task_specs.items():
            has_grader = spec.get('has_grader')
            grader_type = spec.get('grader_type', 'N/A')
            if has_grader:
                spec_grader_count += 1
                print(f"    ✓ {task_id}: has_grader=True, type={grader_type}")
            else:
                print(f"    ✗ {task_id}: has_grader=False")
        
        if spec_grader_count >= 3:
            print(f"\n  ✓ MANIFEST VALID: {spec_grader_count}/3 tasks with graders")
        else:
            print(f"\n  ✗ MANIFEST INVALID: Only {spec_grader_count}/3 tasks with graders")
    else:
        print(f"  ✗ Status: {r.status_code}")
        print(f"  Response: {r.text[:500]}")
        
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# 7. Check /tasks endpoint
print("\n7. /TASKS ENDPOINT")
try:
    from fastapi.testclient import TestClient
    from warehouse_env.warehouse_env.server import app
    
    client = TestClient(app)
    r = client.get('/tasks')
    
    if r.status_code == 200:
        t = r.json()
        tasks = t.get('tasks', {})
        total = t.get('total', 0)
        
        print(f"  ✓ Status 200")
        print(f"  Total tasks: {total}")
        
        grader_count = 0
        for task_id, spec in tasks.items():
            has_grader = spec.get('has_grader')
            grader_type = spec.get('grader_type', 'N/A')
            if has_grader:
                grader_count += 1
                print(f"    ✓ {task_id}: has_grader=True, type={grader_type}")
            else:
                print(f"    ✗ {task_id}: has_grader=False")
        
        if grader_count >= 3:
            print(f"\n  ✓ /TASKS VALID: {grader_count}/3 tasks with graders")
        else:
            print(f"\n  ✗ /TASKS INVALID: Only {grader_count}/3 tasks with graders")
    else:
        print(f"  ✗ Status: {r.status_code}")
        
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# 8. Final summary
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print("""
If all checks above show ✓ (at least 3 graders detected), then:
  - openenv.yaml is correctly configured with 3 graders
  - task_config.py is defining 3 tasks correctly
  - graders module can instantiate all 3 graders
  - /manifest endpoint returns 3 graders
  - /tasks endpoint returns 3 graders with graders
  
This submission should PASS the "not enough tasks with graders" check.

If any check shows ✗, that's likely the validator failure reason.
""")
print("=" * 80 + "\n")
