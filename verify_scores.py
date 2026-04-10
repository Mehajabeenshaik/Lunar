#!/usr/bin/env python
"""Verify all production graders produce safe scores."""

from content_moderation_env.graders import ModeratorGrader
from content_moderation_env.graders_v1 import ModeratorGrader as ModeratorGraderV1

print("=" * 60)
print("PRODUCTION GRADER VERIFICATION")
print("=" * 60)

# Test main grader
print("\nTesting ModeratorGrader (main):")
g = ModeratorGrader()
test_scores = []
for task_id in [1, 5, 10, 20, 30]:
    score = g.grade(task_id, {'category': 'safe'}, {'category': 'safe'})
    test_scores.append(score)
    is_safe = 0 < score < 1
    status = 'PASS' if is_safe else 'FAIL'
    print(f"  Task {task_id:2d}: {score:.6f} [{status}]")

# Test v1 grader
print("\nTesting ModeratorGraderV1 (legacy):")
g_v1 = ModeratorGraderV1()
score_v1_1 = g_v1.grade_task_1({'category': 'safe'}, {'category': 'safe'})
score_v1_2 = g_v1.grade_task_2(
    {'category': 'safe', 'severity': 3},
    {'category': 'safe', 'severity': 3}
)
score_v1_3 = g_v1.grade_task_3(
    {'category': 'safe', 'severity': 3, 'action': 'keep', 'reasoning': 'test'},
    {'category': 'safe', 'severity': 3, 'action': 'keep'}
)

v1_scores = [score_v1_1, score_v1_2, score_v1_3]
for idx, score in enumerate(v1_scores, 1):
    is_safe = 0 < score < 1
    status = 'PASS' if is_safe else 'FAIL'
    print(f"  Task {idx} v1: {score:.6f} [{status}]")

# Summary
all_scores = test_scores + v1_scores
all_safe = all(0 < s < 1 for s in all_scores)
num_boundaries = sum(1 for s in all_scores if s <= 0.0 or s >= 1.0)

print("\n" + "=" * 60)
print(f"Total scores tested: {len(all_scores)}")
print(f"Boundary violations: {num_boundaries}")
print(f"Status: {'SUCCESS - ALL SAFE' if all_safe else 'FAILURE - HAS BOUNDARIES'}")
print("=" * 60)
