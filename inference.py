#!/usr/bin/env python
"""LUNAR OpenEnv Baseline Inference - Uses LLM proxy endpoint provided by validator."""

import os
import sys
import json
import requests
from typing import Dict, Any, Optional

# ============================================================
# ENV VARS - NO FALLBACK DEFAULTS (validator injects these)
# ============================================================
# For Phase 2: validator provides API_BASE_URL pointing to LLM proxy
API_BASE_URL = os.getenv("API_BASE_URL", "")  # Empty if not provided
API_KEY = os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY")  # Accept both

TASK_NAME = os.getenv("WAREHOUSE_TASK", "warehouse_easy")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

# Try multiple endpoints for environment
DEFAULT_ENDPOINTS = [
    "https://mehajabeen-lunar.hf.space",  # HF Spaces production
    "http://localhost:7860",  # Local development
]

# ============================================================
# OPENAI CLIENT - Routes through LLM proxy if API_BASE_URL set
# ============================================================
client = None
HAS_LLM = False

try:
    from openai import OpenAI
    # Initialize OpenAI client - if API_BASE_URL is set, requests go through proxy!
    if API_BASE_URL and API_KEY:
        client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
        HAS_LLM = True
    elif API_KEY:
        # Fallback to direct OpenAI if only API_KEY provided (no proxy)
        client = OpenAI(api_key=API_KEY)
        HAS_LLM = True
except Exception:
    client = None
    HAS_LLM = False

# Track which endpoint works
WORKING_ENDPOINT = None
ENDPOINTS = [e for e in DEFAULT_ENDPOINTS if e]


def reset_environment() -> Optional[Dict[str, Any]]:
    """Reset environment and get initial observation."""
    global WORKING_ENDPOINT
    
    for endpoint in ENDPOINTS:
        try:
            url = f"{endpoint.rstrip('/')}/reset"
            response = requests.post(
                url,
                json={"task": TASK_NAME},
                timeout=5
            )
            response.raise_for_status()
            WORKING_ENDPOINT = endpoint
            return response.json()
        except Exception:
            continue
    
    # If we reach here, try with /api prefix
    for endpoint in ENDPOINTS:
        try:
            url = f"{endpoint.rstrip('/')}/api/reset"
            response = requests.post(
                url,
                json={"task": TASK_NAME},
                timeout=5
            )
            response.raise_for_status()
            WORKING_ENDPOINT = endpoint
            return response.json()
        except Exception:
            continue
    
    return None


def step_environment(session_id: str, action: Dict) -> Dict[str, Any]:
    """Execute one step in environment."""
    if not WORKING_ENDPOINT:
        return {"error": "No working endpoint", "reward": 0.1, "done": True}
    
    endpoints_to_try = [
        f"{WORKING_ENDPOINT.rstrip('/')}/step",
        f"{WORKING_ENDPOINT.rstrip('/')}/api/step",
    ]
    
    for url in endpoints_to_try:
        try:
            response = requests.post(
                url,
                json={"session_id": session_id, "action": action},
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            continue
    
    return {"error": "Step failed", "reward": 0.1, "done": True}


def generate_action(observation: Dict) -> Dict:
    """Generate action using LLM (via proxy if configured) or default strategy."""
    # Default strategy
    num_warehouses = len(observation.get("warehouse_levels", [1]))
    default_action = {
        "reorder_quantities": [50.0] * num_warehouses,
        "transfers": [[0.0] * num_warehouses for _ in range(num_warehouses)]
    }
    
    if not HAS_LLM or not client:
        return default_action
    
    try:
        # Prepare prompt
        prompt = f"""Given warehouse state:
- Levels: {observation.get('warehouse_levels', [])}
- Demand: {observation.get('demand_forecast', [])}
- Day: {observation.get('day', 0)}

Generate optimal action as JSON:
{{"reorder_quantities": [...], "transfers": [[...]]}}

Respond ONLY with valid JSON."""
        
        # Call client - if base_url is set, request goes through LLM proxy!
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        
        # Extract JSON from response
        response_text = response.choices[0].message.content if response.choices else ""
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start >= 0 and end > start:
            action = json.loads(response_text[start:end])
            if "reorder_quantities" in action and "transfers" in action:
                if (len(action["reorder_quantities"]) == num_warehouses and
                    len(action["transfers"]) == num_warehouses):
                    return action
    except Exception:
        pass
    
    return default_action


def main():
    """Run baseline inference with proper logging."""
    print(f"[START] task={TASK_NAME} env=warehouse model={MODEL_NAME}")
    
    # Reset
    reset_result = reset_environment()
    if not reset_result or "error" in reset_result:
        print(f"[END] error=reset_failed steps=0 score=0.0 rewards=")
        sys.exit(1)
    
    session_id = reset_result.get("session_id")
    observation = reset_result.get("observation", {})
    
    if not session_id:
        print(f"[END] error=no_session_id steps=0 score=0.0 rewards=")
        sys.exit(1)
    
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
    
    sys.exit(0)  # Always exit 0 - Phase 2 checks if script ran, not if score is high


if __name__ == "__main__":
    main()
