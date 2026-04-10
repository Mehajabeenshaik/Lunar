"""
Test the environment step() function end-to-end
"""
from content_moderation_env import ContentModerationEnv
import json

violations = []

# Test all 30 tasks
for task_id in range(1, 31):
    try:
        env = ContentModerationEnv(task_id=task_id)
        env.reset()
        
        # Create a simple action
        action = {
            "category": "safe",
            "severity": 1,
            "action": "approve",
            "reasoning": "Test reasoning"
        }
        
        obs, reward, done, info = env.step(action)
        
        print(f"Task {task_id}: Reward: {reward:.6f}, Type: {type(reward).__name__}")
        
        # Check for violations
        if reward is None:
            violations.append((task_id, reward, "None value"))
        elif reward <= 0.0 or reward >= 1.0:
            violations.append((task_id, reward, "OUT OF BOUNDS"))
            print(f"  ❌ VIOLATION: {reward}")
        elif reward < 0.001 or reward > 0.999:
            print(f"  ⚠️  NEAR BOUNDARY: {reward}")
            
    except Exception as e:
        print(f"Task {task_id}: ERROR - {e}")
        violations.append((task_id, None, str(e)))
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
if violations:
    print(f"🚨 VIOLATIONS FOUND:")
    for task_id, reward, reason in violations:
        print(f"  Task {task_id}: {reward} ({reason})")
else:
    print("✅ All environment steps passed!")
