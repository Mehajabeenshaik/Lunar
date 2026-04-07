"""Quick test script - Run this to verify environment works (2 minutes)."""

import sys
sys.path.insert(0, '.')

print("\n" + "="*70)
print("QUICK TEST 1: Environment Validation (2 minutes)")
print("="*70 + "\n")

try:
    from warehouse_env import WarehouseEnv, Action
    from warehouse_env.graders import get_grader
    
    print("✓ Imports successful\n")
    
    # Test all 3 tasks
    results = {}
    for task_name in ["warehouse_easy", "warehouse_medium", "warehouse_hard"]:
        print(f"Testing {task_name}...")
        
        # Create environment
        env = WarehouseEnv(task=task_name)
        obs = env.reset()
        
        # Run 5 steps
        for step_num in range(5):
            action = Action(
                reorder_quantities=[50.0] * len(obs.warehouse_levels),
                transfers=[[0.0] * len(obs.warehouse_levels) for _ in range(len(obs.warehouse_levels))]
            )
            obs, reward = env.step(action)
        
        # Get grade
        grader = get_grader(task_name)
        grade = grader.grade(env.state, env.episode_rewards)
        score = grade["score"]
        
        # Verify score in range
        valid = 0.0 <= score <= 1.0
        results[task_name] = {
            "score": score,
            "valid": valid,
            "steps": len(env.episode_rewards)
        }
        
        status = "✓ PASS" if valid else "✗ FAIL"
        print(f"  {status} | Score: {score:.3f} | Steps: {len(env.episode_rewards)}")
    
    print("\n" + "-"*70)
    print("RESULT: " + ("✓ ALL TESTS PASSED" if all(r["valid"] for r in results.values()) else "✗ SOME TESTS FAILED"))
    print("-"*70 + "\n")
    
    # Print summary table
    print("Summary:")
    print(f"{'Task':<20} {'Score':<12} {'Valid':<10}")
    print("-"*42)
    for task, result in results.items():
        print(f"{task:<20} {result['score']:<12.3f} {str(result['valid']):<10}")
    
except Exception as e:
    print(f"✗ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()

print()
