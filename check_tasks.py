#!/usr/bin/env python3
"""Check which tasks are actually implemented."""

from warehouse_env.warehouse_env.task_config import get_task_variants
from warehouse_env.warehouse_env.env import WarehouseEnv

tasks = get_task_variants()
print('Checking task availability...\n')

working_tasks = []
failing_tasks = []

for task in tasks:
    try:
        env = WarehouseEnv(task=task)
        env.reset()
        working_tasks.append(task)
    except Exception as e:
        failing_tasks.append((task, str(e)[:50]))

print(f"✅ Working tasks: {len(working_tasks)}")
for task in working_tasks[:5]:
    print(f"   - {task}")
if len(working_tasks) > 5:
    print(f"   ... and {len(working_tasks) - 5} more")

if failing_tasks:
    print(f"\n❌ Failing tasks: {len(failing_tasks)}")
    for task, err in failing_tasks[:5]:
        print(f"   - {task}: {err}") 
    if len(failing_tasks) > 5:
        print(f"   ... and {len(failing_tasks) - 5} more")
