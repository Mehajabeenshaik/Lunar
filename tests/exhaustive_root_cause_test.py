#!/usr/bin/env python3
"""
COMPREHENSIVE ROOT CAUSE ANALYSIS
Find EVERY boundary violation in LUNAR code
"""

import sys
sys.path.insert(0, 'c:\\Users\\HP\\Documents\\lunar')

print("\n" + "="*80)
print("LUNAR COMPREHENSIVE ROOT CAUSE ANALYSIS - FINDING ALL BOUNDARY ISSUES")
print("="*80)

# Test ALL 30 tasks with MULTIPLE prediction/grounding truth combinations
print("\n" + "="*80)
print("TESTING ALL 30 TASKS WITH MULTIPLE SCENARIOS")
print("="*80)

try:
    from content_moderation_env.graders import OptimizedModeratorGrader as ModeratorGrader
    
    grader = ModeratorGrader()
    
    # Different test scenarios
    scenarios = [
        ("Matching", {
            "prediction": {"category": "safe", "severity": 1, "action": "none", "reasoning": "OK"},
            "ground_truth": {"category": "safe", "severity": 1, "action": "none"}
        }),
        ("Mismatching", {
            "prediction": {"category": "toxic", "severity": 5, "action": "remove", "reasoning": "Bad"},
            "ground_truth": {"category": "safe", "severity": 1, "action": "none"}
        }),
        ("Empty", {
            "prediction": {},
            "ground_truth": {}
        }),
    ]
    
    boundary_violations = []
    
    for task_id in range(1, 31):
        for scenario_name, data in scenarios:
            try:
                score = grader.grade(task_id, data["prediction"], data["ground_truth"])
                
                # STRICT boundary check
                if score is None:
                    print(f"❌ Task {task_id} ({scenario_name}): None score")
                    boundary_violations.append((task_id, scenario_name, score))
                elif not isinstance(score, (int, float)):
                    print(f"❌ Task {task_id} ({scenario_name}): Wrong type {type(score)}")
                    boundary_violations.append((task_id, scenario_name, score))
                elif score <= 0.0:
                    print(f"❌ Task {task_id} ({scenario_name}): score={score} (<= 0.0)")
                    boundary_violations.append((task_id, scenario_name, score))
                elif score >= 1.0:
                    print(f"❌ Task {task_id} ({scenario_name}): score={score} (>= 1.0)")
                    boundary_violations.append((task_id, scenario_name, score))
                elif score == 0.0 or score == 1.0:
                    print(f"❌ Task {task_id} ({scenario_name}): score={score} (exactly 0 or 1)")
                    boundary_violations.append((task_id, scenario_name, score))
                else:
                    status_char = "✓" if (0 < score < 1) else "⚠"
                    print(f"{status_char} Task {task_id} ({scenario_name}): {score:.4f}")
                    
            except Exception as e:
                print(f"❌ Task {task_id} ({scenario_name}): ERROR - {str(e)[:40]}")
                boundary_violations.append((task_id, scenario_name, str(e)))
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if boundary_violations:
        print(f"❌ FOUND {len(boundary_violations)} BOUNDARY VIOLATIONS:")
        for task_id, scenario, score in boundary_violations[:10]:
            print(f"  Task {task_id} ({scenario}): {score}")
        if len(boundary_violations) > 10:
            print(f"  ... and {len(boundary_violations) - 10} more")
        sys.exit(1)
    else:
        print("✅ ALL 30 TASKS x 3 SCENARIOS = 90 TESTS PASSED!")
        print("Code should pass validator")
        sys.exit(0)
        
except Exception as e:
    print(f"\n❌ CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
