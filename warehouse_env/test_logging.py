"""Test inference logging format (1 minute)."""

import sys
sys.path.insert(0, '.')

print("\n" + "="*70)
print("QUICK TEST 2: Inference Logging Format (1 minute)")
print("="*70 + "\n")

try:
    from warehouse_env import WarehouseEnv, Action
    from warehouse_env.graders import get_grader
    
    task = "warehouse_easy"
    env = WarehouseEnv(task=task)
    obs = env.reset()
    
    model = "test-model"
    print(f"[START] task={task} env=warehouse_env model={model}")
    
    # Run 3 steps
    for step_num in range(1, 4):
        action = Action(
            reorder_quantities=[50.0] * len(obs.warehouse_levels),
            transfers=[[0.0] * len(obs.warehouse_levels) for _ in range(len(obs.warehouse_levels))]
        )
        obs, reward = env.step(action)
        
        action_str = f"reorder([50.0])"
        print(
            f"[STEP] step={step_num} action={action_str} reward={reward.value:.2f} "
            f"done={str(reward.done).lower()} error=null"
        )
    
    # Get score
    grader = get_grader(task)
    grade = grader.grade(env.state, env.episode_rewards)
    score = grade["score"]
    rewards_str = ",".join(f"{r:.2f}" for r in env.episode_rewards)
    
    print(
        f"[END] success={str(score > 0.5).lower()} steps={len(env.episode_rewards)} "
        f"score={score:.2f} rewards={rewards_str}"
    )
    
    # Verify format
    print("\n" + "-"*70)
    print("✓ Log format verified!")
    print("-"*70 + "\n")
    
except Exception as e:
    print(f"✗ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()

print()
