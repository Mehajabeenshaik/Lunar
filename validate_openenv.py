#!/usr/bin/env python
import yaml

with open('openenv.yaml') as f:
    spec = yaml.safe_load(f)

print("OPENENV.YAML VALIDATION")
print("=" * 60)

# Check graders
graders = spec.get('graders', [])
print(f"\nGraders field: {graders}")
print(f"Count: {len(graders)}")

# Check tasks
tasks = spec.get('tasks', [])
print(f"\nTasks in openenv.yaml: {len(tasks)}")

grader_count = 0
for task in tasks:
    task_id = task.get('id')
    has_grader = task.get('has_grader')
    grader_type = task.get('grader_type')
    print(f"  - {task_id}: has_grader={has_grader}, type={grader_type}")
    if has_grader:
        grader_count += 1

print(f"\nTotal tasks with has_grader=true: {grader_count}")

if grader_count >= 3:
    print("\n✓ VALID: 3+ tasks with graders")
else:
    print(f"\n✗ INVALID: Only {grader_count} tasks with graders (need 3)")
