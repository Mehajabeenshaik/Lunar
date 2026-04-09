#!/usr/bin/env python
import sys
sys.path.insert(0, '.')
from warehouse_env.warehouse_env.server import app
from fastapi.testclient import TestClient
import json

client = TestClient(app)
r = client.get('/manifest')
data = r.json()
print('Task specs with action formats:')
for task_id in data.get('task_specs', {}).keys():
    spec = data['task_specs'][task_id]
    print(f'{task_id}:')
    has_grader = spec.get('has_grader')
    action_format = spec.get('action_format')
    print(f'  has_grader: {has_grader}')
    print(f'  action_format: {action_format}')
