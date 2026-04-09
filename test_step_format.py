#!/usr/bin/env python
"""Test step endpoint locally"""
import sys
sys.path.insert(0, '.')
from warehouse_env.warehouse_env.server import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Test reset first
response = client.post('/reset', json={'task': 'warehouse_easy'})
print(f'Reset: {response.status_code}')
if response.status_code != 200:
    print(f'Error: {response.text}')
    sys.exit(1)

session_id = response.json()['session_id']
print(f'Session: {session_id}')

# Test step with query parameter
print("\nTest 1: /step with query param")
response = client.post(
    f'/step?session_id={session_id}',
    json={'reorder_quantities': [100], 'transfers': []}
)
print(f'Status: {response.status_code}')
if response.status_code != 200:
 print(f'Error: {response.text}')
else:
    data = response.json()
    reward = data.get('reward')
    print(f'Reward: {reward}')

# Also test step with StepRequest body format
print("\nTest 2: /step with action in body")
response = client.post(
    f'/step?session_id={session_id}',
    json={'action': {'reorder_quantities': [100], 'transfers': []}}
)
print(f'Status: {response.status_code}')
if response.status_code != 200:
    print(f'Error: {response.text}')
else:
    data = response.json()
    reward = data.get('reward')
    print(f'Reward: {reward}')
