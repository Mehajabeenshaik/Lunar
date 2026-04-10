#!/usr/bin/env python
"""Exhaustive boundary test - try to find ANY possible 0.0 or 1.0 from graders."""

from content_moderation_env.graders import ModeratorGrader
import sys

print("=" * 70)
print("EXHAUSTIVE BOUNDARY TEST - ALL 30 TASKS")
print("=" * 70)

grader = ModeratorGrader()

# Generate diverse test inputs that might expose boundary values
test_inputs = [
    # Perfect matches
    ({'category': 'safe'}, {'category': 'safe'}, "perfect_match"),
    ({'category': 'safe', 'severity': 1}, {'category': 'safe', 'severity': 1}, "perfect_with_severity"),
    
    # Complete mismatches
    ({'category': 'safe'}, {'category': 'hate'}, "complete_mismatch"),
    ({}, {}, "empty"),
    
    # Edge cases
    ({'category': ''}, {'category': ''}, "empty_strings"),
    
    # Partial matches
    ({'category': 'safe', 'severity': 1}, {'category': 'safe', 'severity': 3}, "severity_diff_2"),
    
    # Various formats
    ({'category': 'SAFE'}, {'category': 'safe'}, "case_mismatch"),
    
    # Large inputs
    ({'category': 'safe', 'reasoning': 'x' * 1000}, {'category': 'safe'}, "long_reasoning"),
]

boundary_issues = []
task_results = {}

for task_id in range(1, 31):
    task_results[task_id] = []
    
    for pred, gt, test_name in test_inputs:
        try:
            score = grader.grade(task_id, pred, gt)
            
            # Check if score is boundary
            is_boundary = (score <= 0.0 or score >= 1.0)
            is_safe = (0 < score < 1)
            
            if is_boundary:
                boundary_issues.append(f"Task {task_id} ({test_name}): BOUNDARY VALUE {score}")
            
            task_results[task_id].append({
                'test': test_name,
                'score': score,
                'safe': is_safe,
                'boundary': is_boundary
            })
        except Exception as e:
            boundary_issues.append(f"Task {task_id} ({test_name}): EXCEPTION {str(e)[:40]}")
            task_results[task_id].append({
                'test': test_name,
                'score': None,
                'safe': False,
                'boundary': False,
                'error': str(e)[:40]
            })

# Print summary
print(f"\nTest Cases: {len(test_inputs)}")
print(f"Tasks: 30")
print(f"Total Checks: {30 * len(test_inputs)}")
print()

if boundary_issues:
    print("⚠️  BOUNDARY VIOLATIONS FOUND:")
    for issue in boundary_issues[:20]:  # Print first 20
        print(f"  {issue}")
else:
    print("✅ NO BOUNDARY VIOLATIONS - ALL SCORES SAFE!")

# Show score ranges for each task
print("\n" + "=" * 70)
print("SCORE RANGES BY TASK:")
print("=" * 70)

for task_id in range(1, 31):
    scores = [r['score'] for r in task_results[task_id] if r['score'] is not None]
    if scores:
        min_score = min(scores)
        max_score = max(scores)
        avg_score = sum(scores) / len(scores)
        print(f"Task {task_id:2d}: [{min_score:.6f}, {max_score:.6f}] avg={avg_score:.6f}")

print("\n" + "=" * 70)
print(f"FINAL STATUS: {'SUCCESS' if not boundary_issues else 'FAILURE'}")
print("=" * 70)

sys.exit(0 if not boundary_issues else 1)
