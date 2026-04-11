#!/usr/bin/env python3
"""
ULTRA-COMPREHENSIVE boundary violation detector
- Tests all score values
- Checks for 0.0 and 1.0 both as floats and strings
- Tests floating point edge cases  
- Tests all 30 tasks with 100+ scenarios
"""

import sys
import traceback
from content_moderation_env.graders import ModeratorGrader

def comprehensive_boundary_test():
    """Test for ANY possible boundary violation"""
    grader = ModeratorGrader()
    violations = []
    
    print("=" * 80)
    print("ULTRA-COMPREHENSIVE BOUNDARY VIOLATION TEST")
    print("=" * 80)
    
    # Generate many test prediction/ground_truth combinations
    test_scenarios = []
    
    # Scenario 1-10: Various prediction values
    for i in range(1, 11):
        test_scenarios.append({
            "name": f"Scenario {i}",
            "prediction": {
                "category": ["safe", "hate", "spam", "misinformation", "harassment"][i % 5],
                "severity": (i % 5),
                "action": ["approved", "remove", "warn", "escalate"][i % 4],
                "confidence": i / 10.0,
                "tone": ["friendly", "hostile", "sarcastic", "neutral"][i % 4],
            },
            "ground_truth": {
                "category": ["safe", "hate", "spam", "misinformation", "harassment"][(i+1) % 5],
                "severity": ((i+1) % 5),
                "action": ["approved", "remove", "warn", "escalate"][(i+1) % 4],
                "tone": ["friendly", "hostile", "sarcastic", "neutral"][(i+1) % 4],
            }
        })
    
    # Scenario 11-20: Edge case confidence values
    for conf in [0.0, 0.001, 0.01, 0.1, 0.5, 0.9, 0.99, 0.999, 1.0]:
        test_scenarios.append({
            "name": f"Edge confidence {conf}",
            "prediction": {
                "confidence": conf,
                "is_coordinated": "true" if conf > 0.5 else "false",
            },
            "ground_truth": {
                "is_coordinated": "true"
            }
        })
    
    # Scenario 21: Completely empty
    test_scenarios.append({
        "name": "Empty prediction/ground_truth",
        "prediction": {},
        "ground_truth": {}
    })
    
    # Test all tasks with all scenarios
    for task_id in range(1, 31):
        for scenario in test_scenarios:
            try:
                score = grader.grade(
                    task_id,
                    scenario["prediction"],
                    scenario["ground_truth"],
                    use_cache=False
                )
                
                # Check 1: Is score exactly None?
                if score is None:
                    violations.append({
                        "task": task_id,
                        "scenario": scenario["name"],
                        "score": score,
                        "issue": "Score is None"
                    })
                    continue
                
                # Check 2: Convert to float
                try:
                    score_float = float(score)
                except:
                    violations.append({
                        "task": task_id,
                        "scenario": scenario["name"],
                        "score": score,
                        "issue": f"Cannot convert to float"
                    })
                    continue
                
                # Check 3: Is exactly 0.0?
                if score_float == 0.0 or score_float == -0.0:
                    violations.append({
                        "task": task_id,
                        "scenario": scenario["name"],
                        "score": score_float,
                        "issue": "Score is exactly 0.0"
                    })
                
                # Check 4: Is exactly 1.0?
                if score_float == 1.0:
                    violations.append({
                        "task": task_id,
                        "scenario": scenario["name"],
                        "score": score_float,
                        "issue": "Score is exactly 1.0"
                    })
                
                # Check 5: Is out of range?
                if score_float <= 0.0 or score_float >= 1.0:
                    violations.append({
                        "task": task_id,
                        "scenario": scenario["name"],
                        "score": score_float,
                        "issue": f"Out of range: {score_float}"
                    })
                
                # Check 6: String representation  
                score_str = str(score_float)
                if score_str == "0.0" or score_str == "1.0":
                    violations.append({
                        "task": task_id,
                        "scenario": scenario["name"],
                        "score": score_float,
                        "score_str": score_str,
                        "issue": f"String representation is boundary: {score_str}"
                    })
            
            except Exception as e:
                violations.append({
                    "task": task_id,
                    "scenario": scenario["name"],
                    "score": None,
                    "issue": f"Exception: {str(e)[:100]}",
                    "traceback": traceback.format_exc()[:200]
                })
    
    print(f"\nTested: {30 * len(test_scenarios)} task-scenario combinations")
    print(f"Total scenarios: {len(test_scenarios)}")
    print(f"Total tasks: 30")
    print()
    
    if violations:
        print(f"❌ FOUND {len(violations)} VIOLATIONS:\n")
        for i, v in enumerate(violations[:20], 1):  # Show first 20
            print(f"{i}. Task {v['task']}: {v['scenario']}")
            print(f"   Score: {v['score']}")
            print(f"   Issue: {v['issue']}")
            if 'score_str' in v:
                print(f"   String: {v['score_str']}")
            print()
        
        if len(violations) > 20:
            print(f"... and {len(violations) - 20} more violations")
        
        return False
    else:
        print("✅ ALL TESTS PASSED")
        print("NO BOUNDARY VIOLATIONS DETECTED")
        return True

if __name__ == "__main__":
    try:
        success = comprehensive_boundary_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
