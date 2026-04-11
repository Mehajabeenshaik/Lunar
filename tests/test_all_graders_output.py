"""
Test all graders to find boundary violations
"""
from content_moderation_env.graders import OptimizedModeratorGrader
from content_moderation_env.tasks import ContentCategory, ModerationAction

grader = OptimizedModeratorGrader()

# Test each task with extreme cases
test_cases = {
    1: {"prediction": {"category": "safe"}, "ground_truth": {"category": "safe"}},
    2: {"prediction": {"category": "safe", "severity": 1}, "ground_truth": {"category": "safe", "severity": 1}},
    3: {"prediction": {"category": "safe", "severity": 1, "action": "approve", "reasoning": "This is safe"}, "ground_truth": {"category": "safe", "severity": 1, "action": "approve"}},
    4: {"prediction": {"context": "author_history", "decision": "approve"}, "ground_truth": {"context": "author_history", "decision": "approve"}},
    5: {"prediction": {"trending": "yes", "action": "leave"}, "ground_truth": {"trending": "yes", "action": "leave"}},
    6: {"prediction": {"verdict": "uphold", "reasoning": "Clear policy violation"}, "ground_truth": {"verdict": "uphold", "reasoning": "Clear policy violation"}},
    7: {"prediction": {"is_false_positive": "false", "category": "safe"}, "ground_truth": {"is_false_positive": "false", "category": "safe"}},
    8: {"prediction": {"tone": "sarcasm", "severity": 1}, "ground_truth": {"tone": "sarcasm", "severity": 1}},
    9: {"prediction": {"coordinated": "no"}, "ground_truth": {"coordinated": "no"}},
}

# Add tasks 10-30
for i in range(10, 31):
    test_cases[i] = {
        "prediction": {"answer": "correct"},
        "ground_truth": {"answer": "correct"}
    }

print("Testing all 30 tasks for boundary violations...")
print("=" * 80)

violations = []

for task_id in range(1, 31):
    test = test_cases[task_id]
    try:
        score = grader.grade(task_id, test["prediction"], test["ground_truth"], use_cache=False)
        
        # Check for boundary violations
        if score <= 0.0 or score >= 1.0:
            violations.append((task_id, score, "EXACT BOUNDARY"))
            print(f"❌ Task {task_id}: BOUNDARY VIOLATION - Score: {score}")
        elif score < 0.0001 or score > 0.9999:
            print(f"⚠️  Task {task_id}: NEAR BOUNDARY - Score: {score:.6f}")
        else:
            print(f"✅ Task {task_id}: Safe - Score: {score:.6f}")
    except Exception as e:
        print(f"❌ Task {task_id}: ERROR - {e}")
        violations.append((task_id, None, str(e)))

print("=" * 80)
if violations:
    print(f"\n🚨 Found {len(violations)} violations:")
    for task_id, score, reason in violations:
        print(f"  Task {task_id}: {score} ({reason})")
else:
    print("\n✅ All tasks passed!")
