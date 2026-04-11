#!/usr/bin/env python3
"""
Lunar Content Moderation Benchmark — Inference Script
Multi-turn baseline agent for 30 tasks across 3 domains.

Mandatory env vars: API_BASE_URL, API_KEY (or OPENAI_API_KEY)
Optional: MODEL_NAME, ENVIRONMENT_HOST, HF_TOKEN
"""

import os
import sys
import json
import time
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

try:
    from openai import OpenAI
except ImportError:
    print("[ERROR] OpenAI package not found. Install with: pip install openai>=1.3.0")
    sys.exit(1)

# ============ ENVIRONMENT CONFIGURATION ============

try:
    API_BASE_URL = os.environ["API_BASE_URL"]
    API_KEY = os.environ.get("API_KEY") or os.environ.get("OPENAI_API_KEY") or os.environ.get("HF_TOKEN", "")
except KeyError as e:
    print(f"[ERROR] Missing required environment variable: {e}", file=sys.stderr)
    sys.exit(1)

MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
BENCHMARK = "lunar-content-moderation-benchmark"
ENVIRONMENT_HOST = os.getenv("ENVIRONMENT_HOST", "http://localhost:7860")
MAX_STEPS = 5
MAX_RETRIES = 3

# ============ OPENAI CLIENT ============

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)


# ============ TASK METADATA ============

TASK_NAMES = {
    1: "BasicClassification", 2: "SpamDetection", 3: "HateSpeech",
    4: "Misinformation", 5: "MultiLabel", 6: "SeverityCalibration",
    7: "NuancedClassification", 8: "ContextDependent", 9: "SarcasmAware",
    10: "FullPipeline", 11: "AuthorHistory", 12: "NewAccountScreening",
    13: "TrendingTopicExceptions", 14: "PolicyUpdate", 15: "CrossCultural",
    16: "LanguageAware", 17: "AppealReview", 18: "TrustScore",
    19: "FalsePositiveRecovery", 20: "EvolvingPolicy", 21: "BotNetwork",
    22: "SpamCampaign", 23: "HarassmentNetwork", 24: "MisinfoDisinfoCascade",
    25: "CoordinatedInauthentic", 26: "ViralThreat", 27: "CrossPlatformThreat",
    28: "DeepfakeManipulation", 29: "ExtremismDetection", 30: "FullThreatResponse",
}

TASK_DOMAINS = {
    i: ("text_classification" if i <= 10 else
        "contextual_policy" if i <= 20 else
        "threat_assessment")
    for i in range(1, 31)
}


# ============ SCORE CLAMPING ============

def clamp_score(value: Any) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.5
    if score <= 0.0:
        return 0.01
    if score >= 1.0:
        return 0.99
    if score != score:  # NaN
        return 0.5
    return round(score, 4)


# ============ LOGGING (OpenEnv format) ============

def log_start(task: str, env: str = BENCHMARK, model: str = MODEL_NAME):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error=None):
    reward = clamp_score(reward)
    action_short = str(action)[:120].replace('\n', ' ')
    err = f"{error}" if error else "None"
    print(f"[STEP] step={step} action={action_short!r} reward={reward:.4f} done={done} error={err}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    score = clamp_score(score)
    rewards_clamped = [clamp_score(r) for r in rewards]
    rstr = "[" + ", ".join(f"{r:.2f}" for r in rewards_clamped) + "]"
    print(f"[END] task={TASK_NAMES.get(current_task_id, 'unknown')} success={str(success).lower()} steps={steps} score={score:.4f} rewards={rstr}", flush=True)

current_task_id = 1  # Track globally for log_end


# ============ HTTP CLIENT ============

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def make_session():
    s = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s

http = make_session()


# ============ AGENT ============

def build_prompt(observation: Dict, domain: str, step_num: int, feedback: str = "") -> str:
    """Build domain-specific prompt from observation."""
    post = observation.get("post", {})
    post_text = post.get("text", "No content")[:200]
    action_space = observation.get("action_space", {})

    base = f"You are a content moderation expert. Analyze the following post and respond in JSON.\n\nPost: \"{post_text}\"\n"

    if feedback and step_num > 1:
        base += f"\n--- Feedback from previous step ---\n{feedback}\nPlease improve your response based on the feedback.\n---\n"

    if domain == "text_classification":
        base += f"""
Respond with a JSON object:
{{
  "category": one of {action_space.get('category', ['safe','hate_speech','spam','misinformation'])},
  "severity": integer 1-5 (1=none, 5=extreme),
  "action": one of {action_space.get('action', ['keep','label','warn','remove','escalate','ban'])},
  "reasoning": "brief explanation citing context, policy, or intent"
}}"""

    elif domain == "contextual_policy":
        author_ctx = observation.get("author_context", {})
        policy_ctx = observation.get("policy_context", {})
        base += f"\nAuthor context: {json.dumps(author_ctx)[:200]}"
        if policy_ctx:
            base += f"\nPolicy context: {json.dumps(policy_ctx)[:200]}"
        base += f"""
Consider author history, active policies, and cultural context.
Respond with JSON:
{{
  "category": one of {action_space.get('category', ['safe','hate_speech','spam','misinformation'])},
  "action": one of {action_space.get('action', ['keep','label','warn','remove','escalate','ban'])},
  "policy_exception": true/false,
  "reasoning": "explain referencing author history, policy guidelines, cultural context"
}}"""

    elif domain == "threat_assessment":
        threat_ctx = observation.get("threat_context", {})
        base += f"\nThreat signals: {json.dumps(threat_ctx)[:200]}"
        base += f"""
Assess the threat level and coordination.
Respond with JSON:
{{
  "is_coordinated": true/false,
  "threat_level": one of {action_space.get('threat_level', ['none','low','medium','high','critical'])},
  "category": one of {action_space.get('category', ['safe','spam','misinformation','harassment','hate_speech'])},
  "action": one of {action_space.get('action', ['keep','label','warn','remove','escalate','ban'])},
  "confidence": float 0.0-1.0,
  "reasoning": "explain threat detection, severity assessment, and response plan"
}}"""

    return base


def call_llm(prompt: str) -> str:
    """Call the LLM with the prompt."""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=300,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[DEBUG] LLM call failed: {e}", file=sys.stderr)
        return '{"category":"safe","severity":1,"action":"keep","reasoning":"fallback"}'


def parse_action(response_text: str, domain: str) -> Dict:
    """Parse LLM response into action dict."""
    # Try to extract JSON from response
    try:
        # Find JSON in response
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(response_text[start:end])
    except json.JSONDecodeError:
        pass

    # Fallback action by domain
    if domain == "text_classification":
        return {"category": "safe", "severity": 1, "action": "keep", "reasoning": "Unable to parse response."}
    elif domain == "contextual_policy":
        return {"category": "safe", "action": "keep", "policy_exception": False, "reasoning": "Unable to parse response."}
    else:
        return {"is_coordinated": False, "threat_level": "none", "category": "safe",
                "action": "keep", "confidence": 0.5, "reasoning": "Unable to parse response."}


def run_episode(task_id: int) -> Tuple[bool, float, List[float]]:
    """Run a single multi-turn episode."""
    global current_task_id
    current_task_id = task_id
    domain = TASK_DOMAINS[task_id]
    task_name = TASK_NAMES[task_id]

    log_start(task=task_name)

    rewards = []
    success = False
    steps_taken = 0

    try:
        # Reset environment
        resp = http.post(f"{ENVIRONMENT_HOST}/reset", json={"task_id": task_id}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        session_id = data["session_id"]
        observation = data.get("observation", {})

        feedback = ""

        for step in range(1, MAX_STEPS + 1):
            steps_taken = step

            # Build prompt with feedback from previous step
            prompt = build_prompt(observation, domain, step, feedback)

            # Call LLM
            llm_response = call_llm(prompt)

            # Parse action
            action = parse_action(llm_response, domain)

            # Step environment
            try:
                step_resp = http.post(
                    f"{ENVIRONMENT_HOST}/session/{session_id}/step",
                    json={"session_id": session_id, "action": action},
                    timeout=10
                )
                step_resp.raise_for_status()
                step_data = step_resp.json()
            except Exception as e:
                log_step(step, json.dumps(action)[:100], 0.01, True, str(e))
                rewards.append(0.01)
                break

            reward = clamp_score(step_data.get("reward", 0.5))
            done = step_data.get("done", False)
            observation = step_data.get("observation", {})
            feedback = step_data.get("feedback", "")

            rewards.append(reward)
            log_step(step, json.dumps(action)[:100], reward, done)

            if done:
                success = True
                break

        score = sum(rewards) / len(rewards) if rewards else 0.5
        score = clamp_score(score)

    except Exception as e:
        print(f"[DEBUG] Episode failed: {e}", file=sys.stderr)
        score = clamp_score(0.01)
        rewards = rewards or [0.01]

    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    return success, score, rewards


# ============ MAIN ============

def main():
    """Run baseline agent on representative tasks from each domain."""
    print("=" * 70, file=sys.stderr)
    print("LUNAR CONTENT MODERATION BENCHMARK v3.0 — Baseline Inference", file=sys.stderr)
    print(f"Model: {MODEL_NAME}", file=sys.stderr)
    print(f"Environment: {ENVIRONMENT_HOST}", file=sys.stderr)
    print(f"Domains: text_classification | contextual_policy | threat_assessment", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    # Run 9 representative episodes (3 per domain × 3 difficulties)
    episodes = [
        # Text Classification: easy, medium, hard
        1, 5, 9,
        # Contextual Policy: easy, medium, hard
        11, 15, 19,
        # Threat Assessment: easy, medium, hard
        21, 25, 30,
    ]

    all_results = {}
    all_rewards = []
    start_time = time.time()

    for task_id in episodes:
        success, score, rewards = run_episode(task_id)
        all_results[task_id] = {"success": success, "score": score, "rewards": rewards}
        all_rewards.extend(rewards)

    elapsed = time.time() - start_time

    # Print summary
    print("\n" + "=" * 70, file=sys.stderr)
    print("BENCHMARK SUMMARY", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(f"Episodes completed : {len(episodes)}/{len(episodes)}", file=sys.stderr)
    print(f"Average reward     : {clamp_score(sum(r['score'] for r in all_results.values()) / len(all_results)):.4f}", file=sys.stderr)
    print(f"Total time         : {elapsed:.1f}s", file=sys.stderr)

    # Per-domain breakdown
    domains = {
        "text_classification": [1, 5, 9],
        "contextual_policy": [11, 15, 19],
        "threat_assessment": [21, 25, 30],
    }
    print("\nPer-Domain Performance:", file=sys.stderr)
    for domain_name, task_ids in domains.items():
        scores = [all_results[t]["score"] for t in task_ids if t in all_results]
        avg = sum(scores) / len(scores) if scores else 0
        easy = all_results.get(task_ids[0], {}).get("score", 0)
        med = all_results.get(task_ids[1], {}).get("score", 0)
        hard = all_results.get(task_ids[2], {}).get("score", 0)
        print(f"  {domain_name:25s} → avg={avg:.4f}  (easy: {easy:.4f} | medium: {med:.4f} | hard: {hard:.4f})", file=sys.stderr)

    # Difficulty gradient
    print("\nDifficulty Gradient:", file=sys.stderr)
    easy_scores = [all_results[t]["score"] for t in [1, 11, 21] if t in all_results]
    med_scores = [all_results[t]["score"] for t in [5, 15, 25] if t in all_results]
    hard_scores = [all_results[t]["score"] for t in [9, 19, 30] if t in all_results]
    if easy_scores:
        print(f"  easy   → avg: {sum(easy_scores)/len(easy_scores):.4f}", file=sys.stderr)
    if med_scores:
        print(f"  medium → avg: {sum(med_scores)/len(med_scores):.4f}", file=sys.stderr)
    if hard_scores:
        print(f"  hard   → avg: {sum(hard_scores)/len(hard_scores):.4f}", file=sys.stderr)
    print("=" * 70, file=sys.stderr)


if __name__ == "__main__":
    main()
