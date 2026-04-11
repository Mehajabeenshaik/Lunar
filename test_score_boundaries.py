"""
Test that ALL grader outputs are strictly within (0, 1).
Tests every task with multiple input combinations including edge cases.
"""
import sys
sys.path.insert(0, ".")

from content_moderation_env.graders import ModeratorGrader, safe_clamp

def test_safe_clamp():
    """Test the safe_clamp function with edge cases."""
    print("Testing safe_clamp...")
    test_cases = [
        (0.0, "exactly 0"),
        (1.0, "exactly 1"),
        (-1.0, "negative"),
        (2.0, "above 1"),
        (0.5, "normal"),
        (0.001, "very small"),
        (0.999, "very large"),
        (float('inf'), "infinity"),
        (float('-inf'), "neg infinity"),
        (float('nan'), "NaN"),
        (None, "None"),
        ("abc", "string"),
    ]
    
    all_pass = True
    for value, label in test_cases:
        result = safe_clamp(value)
        ok = 0 < result < 1
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_pass = False
        print(f"  {status}: safe_clamp({value}) = {result} ({label})")
    
    return all_pass


def test_all_graders():
    """Test every task grader with multiple input combinations."""
    print("\nTesting all 30 task graders...")
    
    grader = ModeratorGrader()
    
    # Test cases: (prediction, ground_truth, description)
    test_inputs = [
        # Matching inputs
        ({"category": "safe"}, {"category": "safe"}, "exact match"),
        # Mismatching inputs
        ({"category": "safe"}, {"category": "hate_speech"}, "mismatch"),
        # Empty inputs
        ({}, {}, "both empty"),
        # Partial inputs
        ({"category": "safe"}, {}, "gt empty"),
        ({}, {"category": "safe"}, "pred empty"),
        # Complex matching
        (
            {"category": "safe", "severity": 3, "action": "keep", "reasoning": "This is safe content with proper context and policy considerations."},
            {"category": "safe", "severity": 3, "action": "keep"},
            "full match with reasoning"
        ),
        # Complex mismatch
        (
            {"category": "hate_speech", "severity": 5, "action": "remove"},
            {"category": "safe", "severity": 1, "action": "keep"},
            "full mismatch"
        ),
        # Boolean-like inputs
        ({"is_false_positive": "true", "is_coordinated": "true", "is_bot": "true"},
         {"is_false_positive": True, "is_coordinated": True, "is_bot": True},
         "boolean matches"),
        # Numeric inputs
        ({"trust_score": 0, "confidence": 0.0}, {"trust_score": 10, "confidence": 1.0}, "extreme numbers"),
        ({"trust_score": 5, "confidence": 0.5}, {"trust_score": 5, "confidence": 0.5}, "matching numbers"),
        # None values
        ({"category": None}, {"category": None}, "None values"),
        # Multimodal inputs
        ({"image_assessment": "safe", "text_assessment": "safe", "safety": "safe", "toxicity": "low"},
         {"image_assessment": "safe", "text_assessment": "safe", "safety": "safe", "toxicity": "low"},
         "multimodal match"),
    ]
    
    all_pass = True
    failures = []
    
    for task_id in range(1, 31):
        for pred, gt, desc in test_inputs:
            try:
                score = grader.grade(task_id, pred, gt)
                ok = 0 < score < 1
                if not ok:
                    all_pass = False
                    failures.append(f"Task {task_id} ({desc}): score={score}")
                    print(f"  FAIL: Task {task_id} ({desc}): score={score}")
            except Exception as e:
                all_pass = False
                failures.append(f"Task {task_id} ({desc}): EXCEPTION {e}")
                print(f"  FAIL: Task {task_id} ({desc}): EXCEPTION {e}")
    
    if all_pass:
        print(f"  ALL PASS: {30 * len(test_inputs)} test cases passed!")
    else:
        print(f"\n  FAILURES ({len(failures)}):")
        for f in failures:
            print(f"    - {f}")
    
    return all_pass


def test_json_serialization():
    """Test that scores serialize to valid JSON without boundary values."""
    import json
    
    print("\nTesting JSON serialization...")
    grader = ModeratorGrader()
    
    all_pass = True
    for task_id in range(1, 31):
        for pred, gt in [({}, {}), ({"category": "safe"}, {"category": "safe"})]:
            score = grader.grade(task_id, pred, gt)
            json_str = json.dumps({"reward": score})
            parsed = json.loads(json_str)
            parsed_score = parsed["reward"]
            
            ok = 0 < parsed_score < 1
            if not ok:
                all_pass = False
                print(f"  FAIL: Task {task_id}: JSON round-trip produced {parsed_score} (from {score})")
    
    if all_pass:
        print("  ALL PASS: JSON serialization safe for all tasks")
    
    return all_pass


if __name__ == "__main__":
    print("=" * 60)
    print("SCORE BOUNDARY VALIDATION TEST")
    print("=" * 60)
    
    results = []
    results.append(("safe_clamp", test_safe_clamp()))
    results.append(("all_graders", test_all_graders()))
    results.append(("json_serialization", test_json_serialization()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    all_pass = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_pass = False
    
    print(f"\nOVERALL: {'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")
    sys.exit(0 if all_pass else 1)
