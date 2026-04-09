#!/usr/bin/env python
"""Verify auto-expansion fix on HF Spaces"""
import requests
import time

BASE = 'https://mehajabeen-lunar.hf.space'

print("Verifying fix on HF Spaces deployment:\n")

for task_id in ['warehouse_easy', 'warehouse_medium', 'warehouse_hard']:
    print(f"=== {task_id} ===")
    
    try:
        # Reset
        r = requests.post(f'{BASE}/reset', json={'task': task_id}, timeout=10)
        if r.status_code != 200:
            print(f"  Reset failed: {r.status_code}")
            continue
        
        reset_data = r.json()
        session_id = reset_data['session_id']
        
        # Step with single reorder value (should now auto-expand)
        r = requests.post(
            f'{BASE}/step?session_id={session_id}',
            json={'reorder_quantities': [100], 'transfers': []},
            timeout=10
        )
        
        if r.status_code == 200:
            step_data = r.json()
            reward = step_data['reward']
            info = step_data['info']
            
            if reward > 0:
                print(f"  [FIXED] reward = {reward:.4f}")
            else:
                print(f"  [STILL BROKEN] reward = {reward:.4f}")
                if 'error' in info:
                    print(f"    error: {info['error']}")
        else:
            print(f"  [ERROR] Status {r.status_code}")
    except Exception as e:
        print(f"  [EXCEPTION] {e}")
    
    print()
