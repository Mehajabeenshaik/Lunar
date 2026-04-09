#!/usr/bin/env python
"""Deep debug why validator is still failing"""
import requests
import json

BASE = 'https://mehajabeen-lunar.hf.space'

print('=== DEEP DEBUGGING VALIDATOR ISSUE ===\n')

# 1. Check manifest
print('1. Checking /manifest endpoint')
r = requests.get(f'{BASE}/manifest', timeout=10)
print(f'   Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    tasks = data.get('tasks')
    graders = data.get('graders')
    tasks_with = data.get('features', {}).get('tasks_with_graders')
    print(f'   Tasks: {tasks}')
    print(f'   Graders field: {graders}')
    print(f'   Tasks with graders count: {tasks_with}')
    
    # Check task_specs structure
    print('\n   Task specs details:')
    task_specs = data.get('task_specs', {})
    for task_id in tasks:
        spec = task_specs.get(task_id, {})
        has_grader = spec.get('has_grader')
        grader_type = spec.get('grader_type')
        print(f'      {task_id}: has_grader={has_grader}, grader_type={grader_type}')
else:
    print(f'   ERROR: {r.text}')
    exit(1)

# 2. Test running each task
print('\n2. Testing task execution (what validator does)')
for task_id in ['warehouse_easy', 'warehouse_medium', 'warehouse_hard']:
    print(f'\n   Testing {task_id}:')
    
    # Reset
    r = requests.post(f'{BASE}/reset', json={'task': task_id}, timeout=10)
    print(f'      /reset: {r.status_code}', end='')
    if r.status_code != 200:
        print(f' - FAIL: {r.text[:80]}')
        continue
    print(' OK')
    
    session = r.json().get('session_id')
    print(f'      session_id: {session}')
    
    # Step - test direct format (what validator likely sends)
    print(f'      /step: ', end='')
    step_payload = {
        'reorder_quantities': [100],
        'transfers': []
    }
    r = requests.post(
        f'{BASE}/step?session_id={session}',
        json=step_payload,
        timeout=10,
        headers={'Content-Type': 'application/json'}
    )
    print(f'{r.status_code}', end='')
    if r.status_code != 200:
        print(f' - FAIL')
        print(f'         Response: {r.text[:200]}')
        
        # Try alternate format
        print(f'      /step (alt format): ', end='')
        alt_payload = {'action': step_payload}
        r = requests.post(
            f'{BASE}/step?session_id={session}',
            json=alt_payload,
            timeout=10
        )
        print(f'{r.status_code}')
        if r.status_code != 200:
            print(f'         Both formats FAILED')
    else:
        reward = r.json().get('reward')
        print(f' OK (reward={reward:.4f})')

print('\n3. Checking if grader field structure is correct')
print('   Expected by validator:')
print('   - tasks list with 3+ items ✓')
print('   - graders list or tasks_with_graders >= 3 ✓')
print('   - Each task can be executed ✓')
print('   - /step returns reward in [0, 1] ✓')
