#!/usr/bin/env python3
"""
Comprehensive test to find ANY scenario that produces boundary scores
"""

from content_moderation_env.graders import ModeratorGrader

def test_extreme_cases():
    """Test with various edge case combinations"""
    grader = ModeratorGrader()
    
    test_cases = [
        # Test case 1: All matches (should be high scores)
        {
            "name": "All matches",
            "prediction": {"category": "hate", "severity": 3, "action": "remove", "tone": "hostile"},
            "ground_truth": {"category": "hate", "severity": 3, "action": "remove", "tone": "hostile"},
        },
        # Test case 2: All mismatches (should be low scores)
        {
            "name": "All mismatches",
            "prediction": {"category": "safe", "severity": 0, "action": "approved", "tone": "friendly"},
            "ground_truth": {"category": "hate", "severity": 5, "action": "remove", "tone": "hostile"},
        },
        # Test case 3: Empty prediction
        {
            "name": "Empty prediction",
            "prediction": {},
            "ground_truth": {"category": "hate", "severity": 3, "action": "remove"},
        },
        # Test case 4: None values
        {
            "name": "None values",
            "prediction": {"category": None, "severity": None},
            "ground_truth": {"category": "hate", "severity": 3},
        },
        # Test case 5: Mixed types
        {
            "name": "Mixed types",
            "prediction": {"severity": "3", "trust_score": "7.5"},
            "ground_truth": {"severity": 3, "trust_score": 7.5},
        },
    ]
    
    all_safe = True
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print("-" * 70)
        
        for task_id in range(1, 31):
            try:
                score = grader.grade(
                    task_id,
                    test_case["prediction"],
                    test_case["ground_truth"],
                    use_cache=False
                )
                
                if score <= 0.0 or score >= 1.0:
                    print(f"❌ Task {task_id}: BOUNDARY VIOLATION - Score: {score}")
                    all_safe = False
                elif score < 0.001 or score > 0.999:
                    print(f"⚠️  Task {task_id}: EXTREME VALUE - Score: {score}")
            except Exception as e:
                print(f"❌ Task {task_id}: ERROR - {e}")
                all_safe = False
        
        if all_safe:
            print("✅ All tasks safe for this test case")
    
    print("\n" + "=" * 70)
    if all_safe:
        print("✅ ALL TEST CASES PASSED")
    else:
        print("❌ SOME TEST CASES FAILED - Boundary violations found")
    
    return all_safe

if __name__ == "__main__":
    success = test_extreme_cases()
    exit(0 if success else 1)
