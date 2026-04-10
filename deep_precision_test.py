#!/usr/bin/env python3
"""
Deep-dive floating point precision test
Check if any grader returns values that APPEAR safe but might round to 0.0 or 1.0
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from content_moderation_env.graders import ModeratorGrader
import numpy as np

print("="*80)
print("DEEP FLOATING POINT PRECISION TEST")
print("="*80)

grader = ModeratorGrader()

# Test inputs with different patterns
test_cases = [
    # Test case format: (task_id, prediction, ground_truth, description)
    (1, {'category': 'safe'}, {'category': 'safe'}, "Task 1 perfect match"),
    (1, {'category': 'hate'}, {'category': 'safe'}, "Task 1 mismatch"),
    (14, {'workplace': True, 'home': True, 'public': True}, {'workplace': True, 'home': True, 'public': True}, "Task 14 perfect (3/3 = 1.0)"),
    (14, {'workplace': True, 'home': False, 'public': False}, {'workplace': True, 'home': True, 'public': True}, "Task 14 partial (1/3)"),
    (14, {'workplace': False, 'home': False, 'public': False}, {'workplace': True, 'home': True, 'public': True}, "Task 14 none (0/3 = 0.0)"),
    (10, {'safety': 'safe'}, {'safety': 'safe'}, "Task 10 match"),
    (10, {'safety': 'explicit'}, {'safety': 'safe'}, "Task 10 mismatch"),
]

all_safe = True
problematic_scores = []

for task_id, pred, gt, desc in test_cases:
    try:
        score = grader.grade(task_id, pred, gt)
        
        # Extreme precision checks
        is_zero_exact = (score == 0.0)
        is_one_exact = (score == 1.0)
        is_between_bounds = (0 < score < 1)
        
        # Check if string representation might be problematic
        score_str = str(score)
        str_is_zero = (score_str == "0.0")
        str_is_one = (score_str == "1.0")
        
        # Check numpy values
        is_numpy_type = isinstance(score, (np.floating, np.integer))
        if is_numpy_type:
            score_as_float = float(score)
        else:
            score_as_float = score
        
        # Check various rounding edge cases
        round_4 = round(score, 4)
        round_4_is_boundary = (round_4 == 0.0 or round_4 == 1.0)
        
        status = "✅ SAFE" if is_between_bounds else "❌ UNSAFE"
        
        print(f"\n{status} | {desc}")
        print(f"  Raw value: {score} (type: {type(score).__name__})")
        print(f"  Exact 0.0: {is_zero_exact}, Exact 1.0: {is_one_exact}")
        print(f"  Between bounds: {is_between_bounds}")
        print(f"  String: '{score_str}', Str='0.0': {str_is_zero}, Str='1.0': {str_is_one}")
        print(f"  NumPy type: {is_numpy_type}")
        print(f"  After round(4): {round_4} (is boundary: {round_4_is_boundary})")
        
        if not is_between_bounds or round_4_is_boundary:
            all_safe = False
            problematic_scores.append((task_id, pred, gt, score, desc))
            
    except Exception as e:
        print(f"\n❌ ERROR in {desc}: {e}")
        all_safe = False

print("\n" + "="*80)
if all_safe:
    print("✅ ALL VALUES SAFE - No floating-point edge cases detected!")
else:
    print(f"❌ PROBLEMS FOUND: {len(problematic_scores)} problematic scores")
    for task_id, pred, gt, score, desc in problematic_scores:
        print(f"  - Task {task_id}: {score} ({desc})")

print("="*80)

# Additional numpy-specific check
print("\nNUMPY EDGE CASE CHECK:")
print("-" * 80)

# Check numpy division results
for ctx_count in [0, 1, 2, 3]:
    result = ctx_count / 3
    clamped = max(0.1, min(0.999, result))
    
    print(f"Contexts: {ctx_count}/3 → {result} → clamped: {clamped}")
    print(f"  Clamped == 0.0? {clamped == 0.0}, == 1.0? {clamped == 1.0}")
    print(f"  In bounds (0,1)? {0 < clamped < 1}")
    
print("\n" + "="*80)
