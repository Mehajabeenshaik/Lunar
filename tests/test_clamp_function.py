#!/usr/bin/env python3
"""Test the clamp_score function specifically"""

import sys
sys.path.insert(0, 'c:\\Users\\HP\\Documents\\lunar')

from content_moderation_env.graders import OptimizedModeratorGrader

grader = OptimizedModeratorGrader()

# Test the _clamp_score function directly
test_values = [
    0.0, 1.0,  # Exact boundaries
    -0.1, 1.1,  # Out of range
    0.5, 0.99, 0.01,  # Valid
    0.9999999, 1.0000001,  # Floating point edge cases
    None, float('nan'), float('inf'),  # Special values
]

print("Testing _clamp_score function:")
print("="*60)

for val in test_values:
    try:
        result = grader._clamp_score(val)
        is_valid = 0 < result < 1
        status = "✓ VALID" if is_valid else "✗ BOUNDARY"
        print(f"  Input: {val:>15} → Output: {result:>10.6f} {status}")
    except Exception as e:
        print(f"  Input: {val:>15} → ERROR: {e}")

# Now test with actual graders and edge case inputs
print("\n" + "="*60)
print("Testing actual graders with edge case inputs:")
print("="*60)

edge_cases = [
    (1, {}, {}, "empty inputs"),
    (1, {'category': None}, {'category': None}, "None values"),  
    (14, {'workplace': True, 'home': True, 'public': True}, 
          {'workplace': True, 'home': True, 'public': True}, "task 14 - perfect 3/3"),
    (14, {'workplace': False, 'home': False, 'public': False},
          {'workplace': True, 'home': True, 'public': True}, "task 14 - none 0/3"),
    (20, {'trust_score': 5}, {'trust_score': 5}, "task 20 - equal values"),
    (24, {}, {}, "task 24 - empty contexts"),
]

for task_id, pred, gt, desc in edge_cases:
    try:
        # Call through the grade() method which should apply _clamp_score
        score = grader.grade(task_id, pred, gt)
        is_valid = 0 < score < 1
        is_exact_boundary = (score == 0.0 or score == 1.0)
        
        status = "✓ SAFE" if is_valid else "✗ BOUNDARY"
        print(f"  Task {task_id:2d} {desc:30s}: {score:.6f} {status}")
        
        if is_exact_boundary:
            print(f"               ^^ CRITICAL: Exact boundary value detected!")
            
    except Exception as e:
        print(f"  Task {task_id:2d} {desc:30s}: ERROR - {str(e)[:40]}")

print("\n" + "="*60)
