#!/usr/bin/env python
"""Check manifest and grader registry."""

import requests
import json
from warehouse_env.warehouse_env.task_config import get_task_variants
from warehouse_env.warehouse_env.graders import get_grader

print("="*60)
print("MANIFEST AND GRADER CHECK")
print("="*60)

# Check task_config
print("\n1. TASK_CONFIG:")
tasks = get_task_variants()
print(f"Tasks defined: {list(tasks.keys())}")
print(f"Total: {len(tasks)}")

# Check graders
print("\n2. GRADERS FOR EACH TASK:")
for task_id in tasks.keys():
    try:
        grader = get_grader(task_id)
        print(f"  ✅ {task_id}: {grader.__class__.__name__}")
    except Exception as e:
        print(f"  ❌ {task_id}: {e}")

# Check manifest endpoint
print("\n3. MANIFEST ENDPOINT:")
try:
    resp = requests.get("http://localhost:7860/manifest")
    manifest = resp.json()
    print(f"Status: {resp.status_code}")
    print(f"Tasks in manifest: {manifest.get('tasks', [])}")
    print(f"Has 'graders' field: {'graders' in manifest}")
    print(f"Has 'task_specs' field: {'task_specs' in manifest}")
    print(f"Has 'domains' field: {'domains' in manifest}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*60)
