#!/usr/bin/env python
"""Simulate what the validator sees when testing"""
import requests
import json
from datetime import datetime

BASE = 'https://mehajabeen-lunar.hf.space'

print("=" * 80)
print(f"VALIDATOR SIMULATION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

print("\n[PHASE 1] MANIFEST DISCOVERY")
try:
    r = requests.get(f'{BASE}/manifest', timeout=10)
    if r.status_code == 200:
        m = r.json()
        graders = m.get('graders', [])
        tasks_with_graders = m.get('features', {}).get('tasks_with_graders', 0)
        print(f"  Status: 200 OK")
        print(f"  Graders advertised: {graders}")
        print(f"  Count: {len(graders)}")
        print(f"  tasks_with_graders: {tasks_with_graders}")
        
        if tasks_with_graders >= 3:
            print("  ✓ PASS: Sufficient graders advertised")
        else:
            print(f"  ✗ FAIL: Only {tasks_with_graders} graders (need 3)")
    else:
        print(f"  ✗ FAIL: Status {r.status_code}")
except Exception as e:
    print(f"  ✗ EXCEPTION: {e}")

print("\n[PHASE 2] TASK VALIDATION - Testing each grader")
for task_id in ['warehouse_easy', 'warehouse_medium', 'warehouse_hard']:
    print(f"\n  Testing {task_id}...")
    try:
        # Reset
        r = requests.post(f'{BASE}/reset', json={'task': task_id}, timeout=10)
        if r.status_code != 200:
            print(f"    ✗ Reset failed: {r.status_code}")
            continue
        
        reset_data = r.json()
        session_id = reset_data.get('session_id')
        if not session_id:
            print(f"    ✗ No session_id returned")
            continue
        
        # Step with validator's default test action format
        r = requests.post(
            f'{BASE}/step?session_id={session_id}',
            json={'reorder_quantities': [100], 'transfers': []},
            timeout=10
        )
        
        if r.status_code != 200:
            print(f"    ✗ Step failed: {r.status_code}")
            continue
        
        step_data = r.json()
        reward = step_data.get('reward', -1)
        error = step_data.get('info', {}).get('error', None)
        
        if reward > 0:
            print(f"    ✓ PASS: reward={reward:.4f}")
        elif error:
            print(f"    ✗ FAIL: reward={reward:.4f}, error={error}")
        else:
            print(f"    ✗ FAIL: reward={reward:.4f}")
            
    except Exception as e:
        print(f"    ✗ EXCEPTION: {e}")

print("\n[PHASE 3] INFERENCE TEST - Check inference.py output format")
try:
    import subprocess
    import os
    
    # Set environment as validator would
    env = os.environ.copy()
    env['WAREHOUSE_TASK'] = 'warehouse_easy'
    env['MODEL_NAME'] = 'gpt-3.5-turbo'
    # Note: validator would set API_BASE_URL but we don't have LLM access locally
    
    # Run inference with short timeout
    result = subprocess.run(
        ['python', 'inference.py'],
        capture_output=True,
        text=True,
        timeout=30,
        env=env
    )
    
    print("  inference.py output (first 20 lines):")
    output_lines = result.stdout.split('\n')[:20]
    for line in output_lines:
        if line.strip():
            print(f"    {line}")
    
    if result.returncode == 0:
        print(f"  ✓ PASS: inference.py exited with code 0")
    else:
        print(f"  ✗ FAIL: inference.py exited with code {result.returncode}")
        if result.stderr:
            print(f"  stderr: {result.stderr[:500]}")
            
except Exception as e:
    print(f"  ✗ EXCEPTION: {e}")

print("\n" + "=" * 80)
print("END VALIDATION SIMULATION")
print("=" * 80)
