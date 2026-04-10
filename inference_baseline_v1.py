#!/usr/bin/env python3
"""
Content Moderation Benchmark - Enhanced Inference Script (9 Tasks + Multi-Turn)
Baseline agent for Meta Content Moderation Environment

MANDATORY REQUIREMENTS:
- OpenAI Client for all LLM calls
- Environment variables: API_BASE_URL, MODEL_NAME, HF_TOKEN
- Structured stdout logging: [START], [STEP], [END] format
- Runs all 9 tasks with multi-turn reasoning
- Target runtime: < 25 minutes
"""

import os
import sys
import json
import time
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

try:
    from openai import OpenAI
except ImportError:
    print("[ERROR] OpenAI package not found. Install with: pip install openai>=1.3.0")
    sys.exit(1)

# ============ ENVIRONMENT CONFIGURATION ============

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    print("[ERROR] HF_TOKEN environment variable not set")
    sys.exit(1)

BENCHMARK = "content-moderation-benchmark"
ENVIRONMENT_HOST = os.getenv("ENVIRONMENT_HOST", "http://localhost:7860")
MAX_STEPS = 8
MAX_RETRIES = 3

# ============ LOGGING UTILITIES ============

def log_start(task_name: str, task_id: int) -> None:
    """Emit [START] log line"""
    print(f"[START] task={task_name} env={BENCHMARK} model={MODEL_NAME}", flush=True)


def log_step(step_num: int, action: str, reward: float, done: bool, error: str = None) -> None:
    """Emit [STEP] log line"""
    error_str = f'"{error}"' if error else "null"
    done_str = "true" if done else "false"
    print(
        f"[STEP] step={step_num} action={action} reward={reward:.2f} done={done_str} error={error_str}",
        flush=True
    )


def log_end(success: bool, steps_taken: int, final_score: float, rewards: List[float]) -> None:
    """Emit [END] log line"""
    success_str = "true" if success else "false"
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={success_str} steps={steps_taken} score={final_score:.2f} rewards={rewards_str}",
        flush=True
    )


# ============ ENVIRONMENT INTERACTION ============

class ContentModerationAgent:
    """Agent that uses LLM to moderate content via the environment API"""
    
    def __init__(self):
        """Initialize OpenAI client and environment"""
        self.client = OpenAI(
            api_key=HF_TOKEN,
            base_url=API_BASE_URL
        )
        self.env_url = ENVIRONMENT_HOST
        self.session_id = None
        self.current_task = None
        self.episode_rewards = []
        
    def start_session(self, task_id: int) -> Dict[str, Any]:
        """Start a new session with the environment"""
        try:
            import requests
            response = requests.post(
                f"{self.env_url}/session/start",
                json={"task_id": task_id, "seed": int(time.time()) % 10000},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            self.session_id = data["session_id"]
            return data.get("observation", {})
        except Exception as e:
            print(f"[ERROR] Failed to start session: {e}", file=sys.stderr)
            raise
    
    def step_environment(self, action: Dict[str, str]) -> Tuple[Dict, float, bool, Dict]:
        """Send action to environment and receive next observation"""
        try:
            import requests
            response = requests.post(
                f"{self.env_url}/session/{self.session_id}/step",
                json={"action": action},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return (
                data.get("observation", {}),
                data.get("reward", 0.0),
                data.get("done", False),
                data.get("info", {})
            )
        except Exception as e:
            print(f"[ERROR] Failed to step environment: {e}", file=sys.stderr)
            raise
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get final episode summary"""
        try:
            import requests
            response = requests.get(
                f"{self.env_url}/session/{self.session_id}/summary",
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("summary", {})
        except Exception as e:
            print(f"[ERROR] Failed to get session summary: {e}", file=sys.stderr)
            return {}
    
    def generate_action(self, observation: Dict, task_id: int, step_num: int) -> Dict[str, str]:
        """Use LLM to generate next action based on observation"""
        
        post_text = observation.get("post", {}).get("text", "")
        post_engagement = observation.get("post", {}).get("engagement", 0)
        
        # DOMAIN 1: BASIC CLASSIFICATION (Tasks 1-3)
        if task_id == 1:
            prompt = f"""You are a content moderator for a social media platform.

Post content: "{post_text}"
Post engagement: {post_engagement}

Classify this post into ONE of: safe, hate_speech, spam, misinformation

Respond with ONLY the category name, nothing else."""
            
            response = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=50,
                messages=[{"role": "user", "content": prompt}]
            )
            
            category = response.content[0].text.strip().lower()
            valid_categories = ["safe", "hate_speech", "spam", "misinformation"]
            if category not in valid_categories:
                category = "safe"
            
            return {"category": category}
        
        elif task_id == 2:
            prompt = f"""You are a content moderator for a social media platform.

Post content: "{post_text}"
Post engagement: {post_engagement}

Classify this post and rate its severity:
1. Category: safe | hate_speech | spam | misinformation
2. Severity: 1 (minimal) to 5 (critical)
3. Brief reasoning (1 sentence)

Respond in JSON format:
{{"category": "...", "severity": <1-5>, "reasoning": "..."}}"""
            
            response = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            try:
                result = json.loads(response.content[0].text.strip())
                category = result.get("category", "safe").lower()
                severity = max(1, min(5, int(result.get("severity", 1))))
                reasoning = result.get("reasoning", "")
                
                valid_categories = ["safe", "hate_speech", "spam", "misinformation"]
                if category not in valid_categories:
                    category = "safe"
                
                return {
                    "category": category,
                    "severity": severity,
                    "reasoning": reasoning
                }
            except:
                return {"category": "safe", "severity": 1, "reasoning": "Unable to determine"}
        
        elif task_id == 3:
            prompt = f"""You are a content moderator for Meta's social media platform.

Post content: "{post_text}"
Post engagement: {post_engagement}

Make a complete moderation decision:
1. Category: safe | hate_speech | spam | misinformation
2. Severity: 1 (minimal) to 5 (critical)
3. Action: keep | warn | remove | escalate
4. Explanation: Brief reasoning for the decision

Respond in JSON format:
{{"category": "...", "severity": <1-5>, "action": "...", "reasoning": "..."}}"""
            
            response = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            try:
                result = json.loads(response.content[0].text.strip())
                category = result.get("category", "safe").lower()
                severity = max(1, min(5, int(result.get("severity", 1))))
                action = result.get("action", "keep").lower()
                reasoning = result.get("reasoning", "")
                
                valid_categories = ["safe", "hate_speech", "spam", "misinformation"]
                valid_actions = ["keep", "warn", "remove", "escalate"]
                
                if category not in valid_categories:
                    category = "safe"
                if action not in valid_actions:
                    action = "keep"
                
                return {
                    "category": category,
                    "severity": severity,
                    "action": action,
                    "reasoning": reasoning
                }
            except:
                return {"category": "safe", "severity": 1, "action": "keep", "reasoning": "Unable to determine"}
        
        # DOMAIN 2: CONTEXT-AWARE MODERATION (Tasks 4-6)
        elif task_id == 4:
            # Task 4: Author History Context
            author_context = observation.get("author_context", {})
            prior_violations = author_context.get("prior_violations", 0)
            account_age = author_context.get("account_age_days", 100)
            followers = author_context.get("follower_count", 0)
            
            prompt = f"""You are a content moderator. Consider author's history when deciding severity.

Post: "{post_text}"
Author history:
- Prior violations: {prior_violations}
- Account age: {account_age} days
- Followers: {followers}

Instructions: Higher prior violations = potentially higher severity. Repeat offenders need stricter action.

Respond in JSON:
{{"category": "...", "severity": <1-5>, "reasoning": "Consider author history..."}}"""
            
            response = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            try:
                result = json.loads(response.content[0].text.strip())
                return {
                    "category": result.get("category", "safe").lower(),
                    "severity": max(1, min(5, int(result.get("severity", 1)))),
                    "reasoning": result.get("reasoning", "")
                }
            except:
                return {"category": "safe", "severity": 1, "reasoning": ""}
        
        elif task_id == 5:
            # Task 5: Trending Topic Context
            trending_topic = observation.get("trending_topic", "")
            policy_note = observation.get("policy_note", "")
            
            prompt = f"""Content moderation with policy context.

Post: "{post_text}"
Trending topic: {trending_topic}
Policy: {policy_note}

Some content allowed in certain contexts (e.g., political speech during elections).
Respond with: category, action (keep/remove/label), policy_exception if applicable

{{"category": "...", "action": "...", "policy_exception": "..."}}"""
            
            response = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            try:
                result = json.loads(response.content[0].text.strip())
                return {
                    "category": result.get("category", "safe").lower(),
                    "action": result.get("action", "keep").lower(),
                    "policy_exception": result.get("policy_exception", "")
                }
            except:
                return {"category": "safe", "action": "keep", "policy_exception": ""}
        
        elif task_id == 6:
            # Task 6: Appeal Case Review
            original_decision = observation.get("original_decision", {})
            appeal_evidence = observation.get("appeal_evidence", {})
            
            prompt = f"""Review appeal of moderation decision.

Original decision: {original_decision.get("action")} ({original_decision.get("category")})
Appeal claim: {appeal_evidence.get("author_claim")}
Context: {appeal_evidence.get("context")}
Similar content approved? {appeal_evidence.get("similar_content_approved")}

Decide: overturn or uphold? Provide new action if overturning.

{{"appeal_verdict": "overturn|uphold", "new_action": "...", "reasoning": "..."}}"""
            
            response = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=250,
                messages=[{"role": "user", "content": prompt}]
            )
            
            try:
                result = json.loads(response.content[0].text.strip())
                return {
                    "appeal_verdict": result.get("appeal_verdict", "uphold").lower(),
                    "new_action": result.get("new_action", "keep").lower(),
                    "reasoning": result.get("reasoning", "")
                }
            except:
                return {"appeal_verdict": "uphold", "new_action": "keep", "reasoning": ""}
        
        # DOMAIN 3: EDGE CASES (Tasks 7-9)
        elif task_id == 7:
            # Task 7: False Positive Detection
            flag_reason = observation.get("flag_reason", "")
            context = observation.get("additional_context", "")
            
            prompt = f"""Detect false positives in content moderation.

Post: "{post_text}"
Initially flagged as: {flag_reason}
Additional context: {context}

Is this a false positive (incorrectly flagged)?

{{"is_false_positive": true/false, "category": "...", "action": "..."}}"""
            
            response = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            
            try:
                result = json.loads(response.content[0].text.strip())
                return {
                    "is_false_positive": result.get("is_false_positive", False),
                    "category": result.get("category", "safe").lower(),
                    "action": result.get("action", "keep").lower()
                }
            except:
                return {"is_false_positive": False, "category": "safe", "action": "keep"}
        
        elif task_id == 8:
            # Task 8: Sarcasm & Irony Detection
            target = observation.get("target", "")
            context = observation.get("context", "")
            
            prompt = f"""Detect sarcasm and irony - critical for avoiding false positives.

Post: "{post_text}"
Target: {target}
Context: {context}

Tone analysis: Is this sarcastic, constructive, or neutral?
In workplace contexts, "Great job 🙄" is sarcasm, not harassment.

{{"tone": "sarcastic|constructive|neutral", "severity": <1-5>, "reasoning": "..."}}"""
            
            response = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            try:
                result = json.loads(response.content[0].text.strip())
                return {
                    "tone": result.get("tone", "neutral").lower(),
                    "severity": max(1, min(5, int(result.get("severity", 1)))),
                    "reasoning": result.get("reasoning", "")
                }
            except:
                return {"tone": "neutral", "severity": 1, "reasoning": ""}
        
        elif task_id == 9:
            # Task 9: Coordinated Inauthentic Behavior
            posts = observation.get("posts", [])
            metadata = observation.get("metadata", {})
            
            prompt = f"""Detect coordinated inauthentic behavior (CIB) - organized attacks.

Posts from multiple accounts: {len(posts)}
Metadata:
- Accounts created same day? {metadata.get("accounts_created_same_day")}
- Similar IP? {metadata.get("similar_ip")}
- Posting pattern: {metadata.get("posting_pattern")}

Sample post content: {posts[0].get("text", "")[:100] if posts else ""}

Detect CIB and recommend actions:
{{"coordinated_inauthentic": true/false, "individual_action": "remove_and_ban|warn|...", "network_action": "investigate_network|escalate_to_team", "urgency": "low|medium|high"}}"""
            
            response = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=250,
                messages=[{"role": "user", "content": prompt}]
            )
            
            try:
                result = json.loads(response.content[0].text.strip())
                return {
                    "coordinated_inauthentic": result.get("coordinated_inauthentic", False),
                    "individual_action": result.get("individual_action", "warn").lower(),
                    "network_action": result.get("network_action", "investigate_network").lower(),
                    "urgency": result.get("urgency", "medium").lower()
                }
            except:
                return {
                    "coordinated_inauthentic": False,
                    "individual_action": "warn",
                    "network_action": "investigate_network",
                    "urgency": "medium"
                }
        
        else:
            return {"error": f"Unknown task {task_id}"}
    
    def run_task(self, task_id: int) -> Tuple[bool, float]:
        """Run a single task and return (success, final_score)"""
        
        task_names = {
            1: "Post Classification",
            2: "Classification with Reasoning",
            3: "Full Moderation Decision",
            4: "Author History Context",
            5: "Trending Topic Context",
            6: "Appeal Case Review",
            7: "False Positive Detection",
            8: "Sarcasm & Irony",
            9: "Coordinated Inauthentic Behavior"
        }
        task_name = task_names.get(task_id, f"Task {task_id}")
        
        log_start(task_name, task_id)
        
        try:
            observation = self.start_session(task_id)
            
            self.episode_rewards = []
            step_count = 0
            success = False
            final_reward = 0.0
            
            for step_num in range(1, MAX_STEPS + 1):
                step_count = step_num
                
                try:
                    action = self.generate_action(observation, task_id, step_num)
                    action_str = json.dumps(action)[:80]
                    
                    observation, reward, done, info = self.step_environment(action)
                    
                    log_step(step_num, action_str, reward, done)
                    
                    self.episode_rewards.append(reward)
                    final_reward = reward
                    
                    if done:
                        success = True
                        break
                
                except Exception as e:
                    log_step(step_num, "error", 0.0, True, str(e))
                    break
            
            summary = self.get_session_summary()
            final_score = summary.get("average_reward", final_reward)
            
            log_end(success, step_count, final_score, self.episode_rewards)
            
            return success, final_score
        
        except Exception as e:
            print(f"[ERROR] Task {task_id} failed: {e}", file=sys.stderr)
            log_end(False, 0, 0.0, [])
            return False, 0.0


# ============ MAIN EXECUTION ============

def main():
    """Run baseline agent on all 9 tasks"""
    
    print("\n" + "="*60, file=sys.stderr)
    print("Content Moderation Benchmark - Enhanced Baseline Agent", file=sys.stderr)
    print("9 Tasks + Multi-Turn Reasoning", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print(f"API: {API_BASE_URL}", file=sys.stderr)
    print(f"Model: {MODEL_NAME}", file=sys.stderr)
    print(f"Environment: {ENVIRONMENT_HOST}", file=sys.stderr)
    print("="*60 + "\n", file=sys.stderr)
    
    try:
        import requests
    except ImportError:
        print("[ERROR] requests library not found. Install with: pip install requests")
        sys.exit(1)
    
    agent = ContentModerationAgent()
    
    task_results = {}
    total_score = 0.0
    
    # Run all 9 tasks
    for task_id in range(1, 10):
        try:
            success, score = agent.run_task(task_id)
            task_results[f"task_{task_id}"] = {
                "success": success,
                "score": score
            }
            total_score += score
            print("", file=sys.stderr)
        except Exception as e:
            print(f"[ERROR] Failed to run task {task_id}: {e}", file=sys.stderr)
            task_results[f"task_{task_id}"] = {
                "success": False,
                "score": 0.0
            }
    
    # Print summary
    avg_score = total_score / 9.0
    print("\n" + "="*60, file=sys.stderr)
    print("BASELINE SCORES (9 TASKS)", file=sys.stderr)
    print("="*60, file=sys.stderr)
    for task_id in range(1, 10):
        result = task_results.get(f"task_{task_id}", {"score": 0.0, "success": False})
        print(f"Task {task_id}: {result['score']:.2f} ({'✓' if result['success'] else '✗'})", file=sys.stderr)
    print(f"\nAverage: {avg_score:.2f}", file=sys.stderr)
    print("="*60 + "\n", file=sys.stderr)


if __name__ == "__main__":
    main()
