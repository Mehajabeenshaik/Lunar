"""Test inference script output format."""

import sys
sys.path.insert(0, r'c:\Users\HP\Documents\lunar\warehouse_env')

import os
# Don't require API key for this test
os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("HF_TOKEN", None)

from warehouse_env import WarehouseEnv, Action
from warehouse_env.graders import get_grader

def test_inference_format():
    """Test that inference logging matches required format."""
    task = "warehouse_easy"
    env = WarehouseEnv(task=task)
    obs = env.reset()
    episode_rewards = []
    
    # Simulate log output
    model = "gpt-4-turbo"
    print(f"[START] task={task} env=warehouse_env model={model}")
    
    for step_num in range(1, 6):
        # Simple deterministic action
        action = Action(
            reorder_quantities=[50.0] * len(obs.warehouse_levels),
            transfers=[[0.0] * len(obs.warehouse_levels) for _ in range(len(obs.warehouse_levels))]
        )
        
        obs, reward = env.step(action)
        episode_rewards.append(reward.value)
        
        # Emit step in required format
        action_str = f"reorder({[round(x, 1) for x in action.reorder_quantities]})"
        error_str = "null"
        
        print(
            f"[STEP] step={step_num} action={action_str} reward={reward.value:.2f} "
            f"done={str(reward.done).lower()} error={error_str}"
        )
    
    # Calculate final score
    grader = get_grader(task)
    grade_result = grader.grade(env.state, episode_rewards)
    score = grade_result["score"]
    
    # Emit end log
    rewards_str = ",".join(f"{r:.2f}" for r in episode_rewards)
    success = score > 0.5
    print(
        f"[END] success={str(success).lower()} steps={len(episode_rewards)} score={score:.2f} "
        f"rewards={rewards_str}"
    )
    
    return score

if __name__ == "__main__":
    score = test_inference_format()
    print(f"\nTest completed with score: {score:.2f}")
