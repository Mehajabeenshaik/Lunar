#!/usr/bin/env python
"""Test that grader scores are strictly within (0, 1)."""

from warehouse_env.warehouse_env.graders_comprehensive import ComprehensiveGrader

print("Testing ComprehensiveGrader score validation:")
grader = ComprehensiveGrader('warehouse_novice')

# Test cases
test_cases = [
    ([], "Empty rewards"),
    ([0.5, 0.6, 0.7], "Typical rewards"),
    ([0.0], "Zero reward"),
    ([1.0], "Max reward"),
]

all_valid = True
for rewards, label in test_cases:
    score = grader.grade(None, rewards)['score']
    valid = 0 < score < 1
    status = "✓" if valid else "✗"
    print(f"{status} {label}: {score:.4f} - {'Valid' if valid else 'INVALID'}")
    if not valid:
        all_valid = False

print()
print("=" * 50)
if all_valid:
    print("✓ All grader scores are strictly within (0, 1)")
else:
    print("✗ FAILURE: Some scores are out of range")
