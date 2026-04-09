#!/usr/bin/env python
"""Complete diagnostic dump - what validator sees"""
import requests
import json

BASE = 'https://mehajabeen-lunar.hf.space'

print("=" * 80)
print("COMPLETE VALIDATOR DIAGNOSTIC")
print("=" * 80)

# Get manifest
r = requests.get(f'{BASE}/manifest', timeout=10)
manifest = r.json() if r.status_code == 200 else None

print("\n/manifest RESPONSE:")
if manifest:
    print(json.dumps(manifest, indent=2)[:2000])  # First 2000 chars
else:
    print(f"Status: {r.status_code if r else 'ERROR'}")

# Get tasks
r = requests.get(f'{BASE}/tasks', timeout=10)
tasks = r.json() if r.status_code == 200 else None

print("\n/tasks RESPONSE:")
if tasks:
    print(json.dumps(tasks, indent=2)[:2000])  # First 2000 chars
else:
    print(f"Status: {r.status_code if r else 'ERROR'}")

# Test each grader
print("\n" + "=" * 80)
print("GRADER TESTS")
print("=" * 80)

for task_id in ['warehouse_easy', 'warehouse_medium', 'warehouse_hard']:
    print(f"\n{task_id}:")
    
    r = requests.post(f'{BASE}/reset', json={'task': task_id}, timeout=10)
    if r.status_code != 200:
        print(f"  Reset failed: {r.status_code}")
        continue
    
    reset_data = r.json()
    session_id = reset_data['session_id']
    
    # Test with single reorder value
    r = requests.post(
        f'{BASE}/step?session_id={session_id}',
        json={'reorder_quantities': [100], 'transfers': []},
        timeout=10
    )
    
    if r.status_code == 200:
        step_data = r.json()
        print(json.dumps(step_data, indent=2))
    else:
        print(f"  Status: {r.status_code}")
        print(f"  Response: {r.text}")

print("\n" + "=" * 80)
print("\nSUMMARY FOR DEBUGGING:")
print("If you see POSITIVE rewards for all 3 tasks above^ = graders are working")
print("If you still get validator error = please share the EXACT error message")
