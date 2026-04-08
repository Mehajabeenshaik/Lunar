#!/usr/bin/env python
"""Simple baseline inference for LUNAR RL environment."""

import os
import sys
import json
import requests
from typing import Dict, Any

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")
TASK_NAME = os.getenv("WAREHOUSE_TASK", "warehouse_easy")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN")

# Try to import OpenAI client for reasoning
try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    HAS_LLM = OPENAI_API_KEY is not None
except ImportError:
    client = None
    HAS_LLM = False


def reset_environment() -> Dict[str, Any]:
    """Reset environment and get initial observation."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/reset",
            json={"task": TASK_NAME},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error resetting environment: {e}", file=sys.stderr)
        sys.exit(1)


def step_environment(session_id: str, action: Dict) -> Dict[str, Any]:
    """Execute one step in environment."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/step",
            json={"session_id": session_id, "action": action},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error stepping environment: {e}", file=sys.stderr)
        return {"error": str(e), "reward": 0.1, "done": True}


def generate_action(observation: Dict) -> Dict:
    """Generate action using LLM or default strategy."""
    if not HAS_LLM or not client:
        # Default strategy: order 50 units per warehouse
        num_warehouses = len(observation.get("warehouse_levels", [1]))
        return {
            "reorder_quantities": [50.0] * num_warehouses,
            "transfers": [[0.0] * num_warehouses for _ in range(num_warehouses)]
        }
    
    try:
        # Prepare prompt
        prompt = f"""
Given warehouse state:
- Levels: {observation.get('warehouse_levels', [])}
- Demand Forecast: {observation.get('demand_forecast', [])}
- Supplier Status: {observation.get('supplier_status', [])}
- Day: {observation.get('day', 0)}

Generate action as JSON only:
{{"reorder_quantities": [...], "transfers": [[...]]}}
"""
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7
        )
        
        # Extract JSON
        response_text = response.choices[0].message.content
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response_text[start:end])
    except Exception as e:
        pass
    
    # Fallback
    num_warehouses = len(observation.get("warehouse_levels", [1]))
    return {
        "reorder_quantities": [50.0] * num_warehouses,
        "transfers": [[0.0] * num_warehouses for _ in range(num_warehouses)]
    }


def main():
    """Run baseline inference with proper logging."""
    print(f"[START] task={TASK_NAME} env=warehouse model={MODEL_NAME}")
    
    # Reset
    reset_result = reset_environment()
    if "error" in reset_result:
        print(f"[END] error={reset_result['error']}")
        sys.exit(1)
    
    session_id = reset_result.get("session_id")
    observation = reset_result.get("observation", {})
    
    episode_rewards = []
    step_count = 0
    max_steps = 8
    
    while step_count < max_steps:
        step_count += 1
        
        # Generate action
        action = generate_action(observation)
        
        # Step
        step_result = step_environment(session_id, action)
        
        reward_value = step_result.get("reward", 0.1)
        episode_rewards.append(reward_value)
        done = step_result.get("done", False)
        
        # Log step
        action_str = f"reorder({action.get('reorder_quantities', [])})"
        print(
            f"[STEP] step={step_count} action={action_str} reward={reward_value:.2f} "
            f"done={str(done).lower()} error=null"
        )
        
        if done:
            break
        
        observation = step_result.get("observation", observation)
    
    # Calculate score
    avg_reward = sum(episode_rewards) / len(episode_rewards) if episode_rewards else 0.0
    score = avg_reward
    
    # Log end
    rewards_str = ",".join(f"{r:.2f}" for r in episode_rewards)
    success = score > 0.5
    
    print(
        f"[END] success={str(success).lower()} steps={step_count} score={score:.2f} "
        f"rewards={rewards_str}"
    )
    
    sys.exit(0 if score > 0.3 else 1)


if __name__ == "__main__":
    main()
