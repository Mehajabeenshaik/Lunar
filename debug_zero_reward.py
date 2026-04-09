#!/usr/bin/env python
"""Debug why medium/hard tasks return 0 reward"""
import requests

BASE = 'https://mehajabeen-lunar.hf.space'

for task_id in ['warehouse_easy', 'warehouse_medium', 'warehouse_hard']:
    print(f'\n=== {task_id} ===')
    
    # Reset
    r = requests.post(f'{BASE}/reset', json={'task': task_id}, timeout=10)
    reset_data = r.json()
    session_id = reset_data['session_id']
    obs = reset_data['observation']
    
    print(f'Initial observation:')
    for key, val in obs.items():
        if isinstance(val, list):
            print(f'  {key}: {val}')
        else:
            print(f'  {key}: {val}')
    
    # Step
    r = requests.post(
        f'{BASE}/step?session_id={session_id}',
        json={'reorder_quantities': [100], 'transfers': []},
        timeout=10
    )
    step_data = r.json()
    reward = step_data['reward']
    done = step_data['done']
    obs = step_data['observation']
    info = step_data['info']
    
    print(f'After /step:')
    print(f'  reward: {reward}')
    print(f'  done: {done}')
    print(f'  observation:')
    for key, val in obs.items():
        if isinstance(val, list):
            print(f'    {key}: {val}')
        else:
            print(f'    {key}: {val}')
    print(f'  info:')
    for key, val in info.items():
        print(f'    {key}: {val}')
