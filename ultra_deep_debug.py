#!/usr/bin/env python
"""ULTRA DEEP DEBUG - Check everything about graders"""
import sys
sys.path.insert(0, '.')

print('=' * 80)
print('ULTRA DEEP GRADER DEBUG')
print('=' * 80)

# 1. Test imports
print('\n1. TESTING IMPORTS')
try:
    from warehouse_env.warehouse_env.graders import (
        get_grader, 
        EasyTaskGrader, 
        MediumTaskGrader, 
        HardTaskGrader,
        TaskGrader
    )
    print('   [OK] All grader imports successful')
except Exception as e:
    print(f'   [FAIL] Import failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. Test get_grader function
print('\n2. TESTING get_grader() FUNCTION')
for task_id in ['warehouse_easy', 'warehouse_medium', 'warehouse_hard']:
    try:
        grader = get_grader(task_id)
        print(f'   [OK] {task_id}: {grader.__class__.__name__}')
        print(f'      - Type: {type(grader)}')
        print(f'      - Has grade method: {hasattr(grader, "grade")}')
        print(f'      - Method callable: {callable(getattr(grader, "grade", None))}')
    except Exception as e:
        print(f'   [FAIL] {task_id}: {e}')
        import traceback
        traceback.print_exc()

# 3. Test grader instantiation directly
print('\n3. TESTING DIRECT INSTANTIATION')
try:
    g1 = EasyTaskGrader()
    g2 = MediumTaskGrader()
    g3 = HardTaskGrader()
    print(f'   [OK] EasyTaskGrader: {g1}')
    print(f'   [OK] MediumTaskGrader: {g2}')
    print(f'   [OK] HardTaskGrader: {g3}')
except Exception as e:
    print(f'   [FAIL] Failed: {e}')
    import traceback
    traceback.print_exc()

# 4. Test grade method
print('\n4. TESTING GRADE METHOD')
from warehouse_env.warehouse_env.models import State

try:
    grader = EasyTaskGrader()
    state = State(
        warehouse_levels=[100.0],
        demand_forecast=[50.0],
        supplier_status=[1.0],
        day=10,
        holding_costs=100.0,
        shortage_penalty=0.0
    )
    result = grader.grade(state, [0.9, 0.8, 0.85])
    print(f'   [OK] grade() executed successfully')
    print(f'   Result: {result}')
    print(f'   Score: {result.get("score")}')
    
    if result.get('score') is not None:
        score = result.get('score')
        if 0 <= score <= 1:
            print(f'   [OK] Score in valid range [0, 1]')
        else:
            print(f'   [FAIL] Score out of range: {score}')
except Exception as e:
    print(f'   [FAIL] grade() failed: {e}')
    import traceback
    traceback.print_exc()

# 5. Test from API perspective
print('\n5. TESTING FROM API PERSPECTIVE')
try:
    from warehouse_env.warehouse_env.task_config import get_task_variants, is_valid_task
    tasks = get_task_variants()
    print(f'   [OK] Tasks from config: {list(tasks.keys())}')
    print(f'   Count: {len(tasks)}')
    
    for task_id in tasks:
        valid = is_valid_task(task_id)
        print(f'      is_valid_task({task_id}): {valid}')
except Exception as e:
    print(f'   [FAIL] Failed: {e}')
    import traceback
    traceback.print_exc()

# 6. Test manifest building
print('\n6. TESTING MANIFEST BUILDING')
try:
    from warehouse_env.warehouse_env.server import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    r = client.get('/manifest')
    
    print(f'   Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        
        # Count graders
        graders_list = data.get('graders', [])
        tasks_with_graders = data.get('features', {}).get('tasks_with_graders', 0)
        task_specs = data.get('task_specs', {})
        
        print(f'   [OK] graders field: {graders_list}')
        print(f'      Count: {len(graders_list)}')
        print(f'   [OK] tasks_with_graders: {tasks_with_graders}')
        
        print(f'   Task specs with graders:')
        grader_count = 0
        for task_id, spec in task_specs.items():
            has_grader = spec.get('has_grader')
            grader_type = spec.get('grader_type')
            print(f'      {task_id}: has_grader={has_grader}, type={grader_type}')
            if has_grader:
                grader_count += 1
        
        print(f'   [OK] Tasks with has_grader=true: {grader_count}')
    else:
        print(f'   [FAIL] Manifest error: {r.text}')
except Exception as e:
    print(f'   [FAIL] Failed: {e}')
    import traceback
    traceback.print_exc()

# 7. Test tasks endpoint
print('\n7. TESTING /tasks ENDPOINT')
try:
    from warehouse_env.warehouse_env.server import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    r = client.get('/tasks')
    
    print(f'   Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        total = data.get('total')
        tasks = data.get('tasks', {})
        
        print(f'   [OK] Total tasks: {total}')
        
        grader_count = 0
        for task_id, spec in tasks.items():
            has_grader = spec.get('has_grader')
            grader_type = spec.get('grader_type')
            print(f'      {task_id}: has_grader={has_grader}, type={grader_type}')
            if has_grader:
                grader_count += 1
        
        print(f'   [OK] Tasks with has_grader=true: {grader_count}')
    else:
        print(f'   [FAIL] Tasks endpoint error: {r.text}')
except Exception as e:
    print(f'   [FAIL] Failed: {e}')
    import traceback
    traceback.print_exc()

# 8. Check openenv.yaml
print('\n8. CHECKING openenv.yaml')
try:
    import yaml
    with open('openenv.yaml', 'r') as f:
        spec = yaml.safe_load(f)
    
    graders = spec.get('graders', [])
    tasks = spec.get('tasks', [])
    
    print(f'   [OK] openenv.yaml graders field: {graders}')
    print(f'   [OK] Count: {len(graders)}')
    
    print(f'   Tasks in openenv.yaml:')
    for task in tasks:
        task_id = task.get('id')
        has_grader = task.get('has_grader')
        grader_type = task.get('grader_type')
        print(f'      {task_id}: has_grader={has_grader}, type={grader_type}')
except Exception as e:
    print(f'   [FAIL] Failed: {e}')
    import traceback
    traceback.print_exc()

print('\n' + '=' * 80)
print('SUMMARY: All grader subsystems checked')
print('=' * 80)
