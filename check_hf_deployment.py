#!/usr/bin/env python
"""Check if HF Spaces has the auto-expansion fix"""
import requests
import json

BASE = 'https://mehajabeen-lunar.hf.space'

print("Checking if HF Spaces has auto-expansion fix...\n")

# Test each task with single reorder value
results = {}
for task_id in ['warehouse_easy', 'warehouse_medium', 'warehouse_hard']:
    try:
        # Reset
        r = requests.post(f'{BASE}/reset', json={'task': task_id}, timeout=10)
        reset_data = r.json()
        session_id = reset_data['session_id']
        
        # Step with single value
        r = requests.post(
            f'{BASE}/step?session_id={session_id}',
            json={'reorder_quantities': [100], 'transfers': []},
            timeout=10
        )
        
        if r.status_code == 200:
            step_data = r.json()
            reward = step_data.get('reward', 0)
            error = step_data.get('info', {}).get('error', None)
            
            results[task_id] = {
                'reward': reward,
                'error': error,
                'has_fix': reward > 0.5
            }
        else:
            results[task_id] = {'status_code': r.status_code}
    except Exception as e:
        results[task_id] = {'exception': str(e)}

print("Results:")
print(json.dumps(results, indent=2))

# Summary
print("\nSummary:")
all_fixed = all(r.get('has_fix', False) for r in results.values() if 'has_fix' in r)
if all_fixed:
    print("✅ AUTO-EXPANSION FIX IS DEPLOYED")
else:
    print("❌ AUTO-EXPANSION FIX NOT WORKING ON HF SPACES")
    print("\nDetails:")
    for task, r in results.items():
        if 'error' in r and r['error']:
            print(f"  {task}: {r['error']}")
