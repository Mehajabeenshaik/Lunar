import os
import sys
import json
import textwrap
from typing import Optional

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from warehouse_env.warehouse_env import WarehouseEnv, Action, Observation
except ImportError:
    from warehouse_env import WarehouseEnv, Action, Observation

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://api.openai.com/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "gpt-4-turbo"
TASK_NAME = os.getenv("WAREHOUSE_TASK", "warehouse_easy")
MAX_STEPS = 8

client = None
if HAS_OPENAI and API_KEY:
    try:
        client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)
    except Exception as e:
        print(f"Warning: Could not initialize OpenAI client: {e}", file=sys.stderr)
        client = None


def format_observation(obs: Observation) -> str:
    """Format observation as human-readable text."""
    return textwrap.dedent(f"""
    Observation:
    - Day: {obs.day}
    - Warehouse Levels: {[f'{x:.1f}' for x in obs.warehouse_levels]}
    - Demand Forecast: {[f'{x:.1f}' for x in obs.demand_forecast]}
    - Supplier Status: {[f'{x:.1f}' for x in obs.supplier_status]}
    - Cumulative Holding Costs: ${obs.holding_costs:.2f}
    - Cumulative Shortage Penalty: ${obs.shortage_penalty:.2f}
    """).strip()


def parse_action(response_text: str, num_warehouses: int) -> Optional[Action]:
    """Parse LLM response to extract action."""
    try:
        # Try to extract JSON from response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            action_dict = json.loads(json_str)
            
            # Ensure correct structure
            if "reorder_quantities" not in action_dict:
                action_dict["reorder_quantities"] = [0.0] * num_warehouses
            if "transfers" not in action_dict:
                action_dict["transfers"] = [[0.0] * num_warehouses for _ in range(num_warehouses)]
            
            # Validate lengths
            if len(action_dict["reorder_quantities"]) != num_warehouses:
                action_dict["reorder_quantities"] = [0.0] * num_warehouses
            if len(action_dict["transfers"]) != num_warehouses:
                action_dict["transfers"] = [[0.0] * num_warehouses for _ in range(num_warehouses)]
            
            return Action(**action_dict)
    except (json.JSONDecodeError, ValueError):
        pass
    
    # Default action
    return Action(
        reorder_quantities=[0.0] * num_warehouses,
        transfers=[[0.0] * num_warehouses for _ in range(num_warehouses)]
    )


def run_episode(task: str, env: WarehouseEnv):
    """Run one episode and emit structured logs."""
    obs = env.reset()
    episode_rewards = []
    
    print(f"[START] task={task} env=warehouse_env model={MODEL_NAME}")
    
    for step_num in range(1, MAX_STEPS + 1):
        # Format observation for LLM
        obs_text = format_observation(obs)
        
        # Prepare prompt
        system_prompt = textwrap.dedent(f"""
        You are an AI agent managing a warehouse inventory system.
        Your goal is to minimize holding costs and shortage penalties while maintaining service level.
        
        Action Format (JSON):
        {{
            "reorder_quantities": [<units_for_warehouse_1>, ...],
            "transfers": [[<transfer_from_1_to_1>, ...], ...]
        }}
        
        Constraints:
        - Reorder quantity: 0-500 units per warehouse
        - Transfer between any two warehouses
        - Goal: minimize (holding_cost + shortage_penalty), maintain service level
        """).strip()
        
        action_text = "{}"
        error_msg = None
        
        if client:
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    max_tokens=200,
                    system=system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": f"{obs_text}\n\nWhat action should I take? Respond only with valid JSON."
                        }
                    ],
                )
                action_text = response.choices[0].message.content
            except Exception as e:
                error_msg = str(e)
                action_text = "{}"
        else:
            # Fallback when no OpenAI client
            action_text = json.dumps({
                "reorder_quantities": [50.0] * len(obs.warehouse_levels),
                "transfers": [[0.0] * len(obs.warehouse_levels) for _ in range(len(obs.warehouse_levels))]
            })
        
        # Parse action
        action = parse_action(action_text, len(obs.warehouse_levels))
        
        # Take step
        obs, reward = env.step(action)
        episode_rewards.append(reward.value)
        
        # Emit step log with proper format
        action_str = f"reorder({[round(x, 1) for x in action.reorder_quantities]})"
        error_str = "null" if not reward.info.get("error") else reward.info.get("error")
        
        print(
            f"[STEP] step={step_num} action={action_str} reward={reward.value:.2f} "
            f"done={str(reward.done).lower()} error={error_str}"
        )
        
        if reward.done:
            break
    
    # Calculate final score
    try:
        from warehouse_env.warehouse_env.graders import get_grader
    except ImportError:
        from warehouse_env.graders import get_grader
    
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


def main():
    """Run baseline inference."""
    env = WarehouseEnv(task=TASK_NAME)
    score = run_episode(TASK_NAME, env)
    sys.exit(0 if score > 0.3 else 1)


if __name__ == "__main__":
    main()
