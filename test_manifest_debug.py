#!/usr/bin/env python
import sys
sys.path.insert(0, '.')
from warehouse_env.warehouse_env.server import app
from fastapi.testclient import TestClient
import json

client = TestClient(app)

# Test manifest endpoint
response = client.get('/manifest')
print(f'Status: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    tasks = data.get('tasks')
    tasks_with_graders = data.get('features', {}).get('tasks_with_graders')
    graders_array = data.get('graders')
    
    print(f'Tasks: {tasks}')
    print(f'Tasks with graders: {tasks_with_graders}')
    print(f'Graders array: {graders_array}')
    print()
    print('Task specs:')
    for task_id, spec in data.get('task_specs', {}).items():
        has_grader = spec.get('has_grader')
        grader_type = spec.get('grader_type')
        print(f'  {task_id}: has_grader={has_grader}, grader_type={grader_type}')
    
    print()
    print('=== POTENTIAL ISSUE: Validator might need different format ===')
    print(f'Is tasks_with_graders >= 3? {tasks_with_graders >= 3}')
else:
    print(f'Error: {response.text}')
