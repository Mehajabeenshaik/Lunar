"""Test script for warehouse environment."""

import sys
sys.path.insert(0, '/c/Users/HP/Documents/lunar/warehouse_env')

from warehouse_env import WarehouseEnv, Action
from warehouse_env.graders import get_grader

# Test easy task
print("=" * 60)
print("Testing Warehouse Environment")
print("=" * 60)

for task_name in ["warehouse_easy", "warehouse_medium", "warehouse_hard"]:
    print(f"\n--- Task: {task_name} ---")
    
    env = WarehouseEnv(task=task_name)
    obs = env.reset()
    
    print(f"Initial observation:")
    print(f"  Warehouses: {len(obs.warehouse_levels)}")
    print(f"  Inventory: {[f'{x:.1f}' for x in obs.warehouse_levels]}")
    print(f"  Demand: {[f'{x:.1f}' for x in obs.demand_forecast]}")
    
    # Simulate a few steps with random actions
    total_reward = 0
    for step in range(5):
        action = Action(
            reorder_quantities=[50.0] * len(obs.warehouse_levels),
            transfers=[[0.0] * len(obs.warehouse_levels) for _ in range(len(obs.warehouse_levels))]
        )
        obs, reward = env.step(action)
        total_reward += reward.value
        print(f"Step {step+1}: reward={reward.value:.3f}, done={reward.done}")
    
    # Test grader
    grader = get_grader(task_name)
    grade = grader.grade(env.state, env.episode_rewards)
    print(f"\nFinal Score: {grade['score']:.3f}")
    print(f"Grade details: {grade}")

print("\n" + "=" * 60)
print("✓ All tests passed!")
print("=" * 60)
