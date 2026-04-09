#!/usr/bin/env python
"""Test what validator might be checking"""
import requests
import json

BASE = 'https://mehajabeen-lunar.hf.space'

print('=== CHECKING WHAT VALIDATOR MIGHT BE LOOKING FOR ===\n')

# Maybe validator is looking at openapi.json?
print('1. Checking /openapi.json')
try:
    r = requests.get(f'{BASE}/openapi.json', timeout=10)
    if r.status_code == 200:
        data = r.json()
        print(f'   Status: {r.status_code} ✓')
        print(f'   Available paths: {list(data.get("paths", {}).keys())}')
    else:
        print(f'   Status: {r.status_code}')
except Exception as e:
    print(f'   Error: {e}')

# Maybe validator is looking for graders endpoint?
print('\n2. Checking for /graders endpoint')
try:
    r = requests.get(f'{BASE}/graders', timeout=10)
    print(f'   Status: {r.status_code}')
    if r.status_code == 200:
        print(f'   Response: {r.json()}')
except Exception as e:
    print(f'   Not found (expected)')

# Maybe validator is looking for tasks endpoint with specific format?
print('\n3. Checking /tasks endpoint')
try:
    r = requests.get(f'{BASE}/tasks', timeout=10)
    if r.status_code == 200:
        data = r.json()
        print(f'   Status: 200 ✓')
        print(f'   Total: {data.get("total")}')
        tasks = data.get('tasks', {})
        for task_id in tasks:
            t = tasks[task_id]
            has_grader = t.get('has_grader') if isinstance(t, dict) else 'unknown'
            print(f'      {task_id}: {has_grader}')
except Exception as e:
    print(f'   Error: {e}')

# Check if there's a schema or spec endpoint
print('\n4. Checking /schema or /spec endpoints')
for endpoint in ['/schema', '/spec', '/environment', '/info']:
    try:
        r = requests.get(f'{BASE}{endpoint}', timeout=5)
        print(f'   {endpoint}: {r.status_code}')
    except:
        pass

# Re-check manifest format more carefully
print('\n5. Re-checking /manifest - EXACT STRUCTURE')
r = requests.get(f'{BASE}/manifest', timeout=10)
if r.status_code == 200:
    data = r.json()
    print(f'   Top-level keys: {list(data.keys())}')
    print(f'     - tasks: {type(data.get("tasks"))} = {data.get("tasks")}')
    print(f'     - graders: {type(data.get("graders"))} = {data.get("graders")}')
    print(f'     - task_specs: {type(data.get("task_specs"))}')
    if data.get('task_specs'):
        print(f'       Keys: {list(data.get("task_specs", {}).keys())}')
    print(f'     - features: {type(data.get("features"))}')
    if data.get('features'):
        print(f'       - tasks_with_graders: {data.get("features").get("tasks_with_graders")}')
