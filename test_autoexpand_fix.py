#!/usr/bin/env python
"""Test if auto-expansion fix works locally"""
from fastapi.testclient import TestClient
from warehouse_env.warehouse_env.server import app

client = TestClient(app)

print("Testing auto-expansion fix locally:\n")

for task_id in ['warehouse_easy', 'warehouse_medium', 'warehouse_hard']:
    print(f"=== {task_id} ===")
    
    # Reset
    r = client.post('/reset', json={'task': task_id})
    if r.status_code != 200:
        print(f"  Reset failed: {r.status_code}")
        continue
    
    reset_data = r.json()
    session_id = reset_data['session_id']
    
    # Step with single reorder (should auto-expand for multi-warehouse tasks)
    r = client.post(
        f'/step?session_id={session_id}',
        json={'reorder_quantities': [100], 'transfers': []}
    )
    
    if r.status_code == 200:
        step_data = r.json()
        reward = step_data['reward']
        info = step_data['info']
        
        if reward > 0:
            print(f"  [SUCCESS] reward = {reward:.4f}")
        else:
            print(f"  [FAILED] reward = {reward:.4f}")
            if 'error' in info:
                print(f"    error: {info['error']}")
    else:
        print(f"  [ERROR] Status {r.status_code}: {r.text}")
    
    print()
