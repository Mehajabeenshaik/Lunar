"""
ContentModerationEnv — Multi-Turn Episode Environment

Key features:
- 30 unique, deterministic tasks (via tasks.py) — no random post sampling
- Multi-turn episodes (5 steps max) — agent improves based on feedback
- Progressive context reveal — more info each step
- Weighted scoring (later steps worth more)
- Rich feedback from domain-specific graders
"""

import random
import hashlib
from typing import Dict, Tuple, Optional, Any, List
from datetime import datetime

from .graders import ModeratorGrader, safe_clamp, TASK_DOMAINS, TASK_DIFFICULTIES


# ─── Task Metadata (for /tasks endpoint compatibility) ──────────────────────

TASK_METADATA = {
    1:  {"name": "Basic Spam Detection",                "desc": "Classify, rate severity, and recommend action for a spam post."},
    2:  {"name": "Pharmaceutical Spam with Severity",   "desc": "Identify spam involving health risk and rate severity."},
    3:  {"name": "Hate Speech Classification",          "desc": "Detect hate speech and assess its severity."},
    4:  {"name": "Credible-Looking Misinformation",     "desc": "Identify false claims disguised as credible reporting."},
    5:  {"name": "Multi-Category Violation",            "desc": "Content violates multiple policies simultaneously."},
    6:  {"name": "Severity Calibration",                "desc": "Assign precise severity scores with justification."},
    7:  {"name": "Sarcasm vs Genuine Threat",           "desc": "Determine if post is satire or genuine violation."},
    8:  {"name": "Quoted Hate Speech (Research)",       "desc": "Classify post quoting hate speech in research context."},
    9:  {"name": "Coordinated Astroturfing",            "desc": "Detect fake organic sponsored content."},
    10: {"name": "Full Classification Pipeline",        "desc": "Complete moderation with expert-level reasoning."},
    11: {"name": "Repeat Offender Review",              "desc": "Moderate considering author's prior violation history."},
    12: {"name": "New Account Screening",               "desc": "Apply stricter policies for new/unverified accounts."},
    13: {"name": "Journalist Reporting Exception",      "desc": "Apply public interest exception for press coverage."},
    14: {"name": "Updated Policy Application",          "desc": "Apply newly enacted AI content disclosure policy."},
    15: {"name": "Cross-Cultural Context (Arabic)",     "desc": "Moderate Arabic post with MENA cultural context."},
    16: {"name": "Satire vs Incitement (Spanish)",      "desc": "Classify Spanish-language satire with cultural cues."},
    17: {"name": "Appeal Case Review",                  "desc": "Review a ban appeal and decide to uphold or overturn."},
    18: {"name": "Trust Score Assessment",              "desc": "Assign trust classification from behavior patterns."},
    19: {"name": "False Positive Recovery",             "desc": "Identify and correct an automated false positive."},
    20: {"name": "Evolving Policy Compliance",          "desc": "Enforce new policy with proportional response."},
    21: {"name": "Bot Network Detection",               "desc": "Identify automated bot accounts in a campaign."},
    22: {"name": "Coordinated Spam Campaign",           "desc": "Detect organized spam across multiple accounts."},
    23: {"name": "Targeted Harassment Network",         "desc": "Identify coordinated harassment targeting a journalist."},
    24: {"name": "Misinformation Cascade",              "desc": "Track and assess a spreading bank-run misinformation."},
    25: {"name": "State-Sponsored Inauthentic Behavior","desc": "Detect foreign-influence election interference."},
    26: {"name": "Viral Dangerous Content",             "desc": "Assess rapidly spreading dangerous chemical instructions."},
    27: {"name": "Cross-Platform Threat Actor",         "desc": "Track a ban-evading threat actor across platforms."},
    28: {"name": "Deepfake Detection",                  "desc": "Identify AI-generated political deepfake video."},
    29: {"name": "Radicalization Pipeline",             "desc": "Detect radicalization stage and recommend intervention."},
    30: {"name": "Full Threat Response Protocol",       "desc": "Complete threat assessment for a coordinated attack."},
}


# ─── Environment ────────────────────────────────────────────────────────────

class ContentModerationEnv:
    """
    Multi-turn content moderation environment.

    Each task_id maps to a unique, specific scenario (via tasks.py).
    No random post sampling — fully deterministic per task.

    Key features:
    - 5-step episodes with grader feedback after each step
    - Progressive context reveal (more context each step)
    - Weighted scoring (later steps worth 2x more)
    - 3 genuinely different domains with domain-specific context
    """

    MAX_STEPS = 5

    def __init__(self, task_id: int = 1, seed: Optional[int] = None):
        if task_id < 1 or task_id > 30:
            raise ValueError(f"task_id must be 1-30, got {task_id}")

        self.task_id = task_id
        self.seed = seed
        if seed is not None:
            random.seed(seed)

        self.current_session_id = self._generate_session_id()
        self.grader = ModeratorGrader()

        # Episode state
        self.steps = 0
        self.done = False
        self.rewards_history: List[float] = []
        self.feedback_history: List[str] = []

        # Task info sourced from tasks.py
        self.domain = TASK_DOMAINS.get(task_id, "text_classification")
        self.difficulty = TASK_DIFFICULTIES.get(task_id, "easy")
        self.task_meta = TASK_METADATA.get(task_id, {"name": f"Task {task_id}", "desc": "Content moderation task"})

        # Load the specific task definition
        self._load_task(task_id)

    def _load_task(self, task_id: int) -> None:
        """Load the deterministic task definition from tasks.py."""
        try:
            from tasks import get_task
            task_def = get_task(task_id)
            self._task_def = task_def
            self._post_data = task_def["post"]
            self._ground_truth = task_def["ground_truth"]
            self._task_context = task_def.get("context", {})
            self._scoring_hints = task_def.get("scoring_hints", {})
        except Exception:
            # Fallback to generic post if tasks.py unavailable
            self._task_def = {}
            self._post_data = {
                "text": "This is a moderation task. Analyze and respond.",
                "engagement": 100,
                "author": f"user_{task_id}000",
                "platform": "social_media",
                "timestamp": datetime.now().isoformat(),
            }
            self._ground_truth = {"category": "safe", "severity": 1, "action": "keep"}
            self._task_context = {}
            self._scoring_hints = {}

    def _generate_session_id(self) -> str:
        combined = f"{datetime.now().isoformat()}-{random.random()}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]

    def reset(self) -> Dict:
        """Reset environment and return initial observation."""
        self.steps = 0
        self.done = False
        self.rewards_history = []
        self.feedback_history = []
        return self._build_observation()

    def step(self, action: Dict[str, Any]) -> Tuple[Dict, float, bool, Dict]:
        """
        Execute one step. Agent's action is graded, feedback returned.

        Returns: (observation, reward, done, info)
        """
        self.steps += 1

        # Grade with domain-specific grader + feedback
        score, feedback, _ = self.grader.grade_with_feedback(
            self.task_id, action, self._ground_truth, self.steps
        )
        score = safe_clamp(score)

        self.rewards_history.append(score)
        self.feedback_history.append(feedback)

        # Episode ends after max steps or high score achieved
        self.done = self.steps >= self.MAX_STEPS or (score >= 0.90 and self.steps >= 2)

        # Build next observation with feedback
        observation = self._build_observation(feedback=feedback)

        # Calculate weighted final score (later steps worth more)
        weighted_score = self._calculate_weighted_score() if self.done else score

        info = {
            "session_id": self.current_session_id,
            "step": self.steps,
            "domain": self.domain,
            "difficulty": self.difficulty,
            "step_score": score,
            "weighted_score": weighted_score if self.done else None,
            "feedback": feedback,
        }

        return observation, safe_clamp(weighted_score if self.done else score), self.done, info

    def _build_observation(self, feedback: Optional[str] = None) -> Dict:
        """Build observation with progressive context reveal."""
        post = self._post_data

        obs = {
            "session_id": self.current_session_id,
            "task_id": f"task_{self.task_id}",
            "domain": self.domain,
            "difficulty": self.difficulty,
            "title": self.task_meta["name"],
            "description": self.task_meta["desc"],
            "post": {
                "text": post.get("text", ""),
                "engagement": post.get("engagement", 0),
                "author": post.get("author", "unknown"),
                "platform": post.get("platform", "social_media"),
                "timestamp": post.get("timestamp", datetime.now().isoformat()),
            },
            "step_number": self.steps,
            "max_steps": self.MAX_STEPS,
        }

        # Feedback from previous step
        if feedback:
            obs["feedback"] = feedback
        if self.rewards_history:
            obs["previous_scores"] = self.rewards_history.copy()

        # Domain-specific action space + progressive context reveal
        if self.domain == "text_classification":
            obs["action_space"] = {
                "category": ["safe", "hate_speech", "spam", "misinformation", "harassment", "violence"],
                "severity": "integer 1-5 (1=minimal, 5=extreme)",
                "action": ["keep", "label", "warn", "remove", "escalate", "ban"],
                "reasoning": "Detailed explanation citing specific policy, content signals, and context"
            }
            # Progressive: reveal scoring hints at step 2+
            if self.steps >= 1 and self._scoring_hints.get("policy_refs"):
                obs["policy_refs"] = self._scoring_hints["policy_refs"]

        elif self.domain == "contextual_policy":
            obs["action_space"] = {
                "category": ["safe", "hate_speech", "spam", "misinformation", "harassment", "violence"],
                "action": ["keep", "label", "warn", "remove", "escalate", "ban"],
                "policy_exception": "true/false — does a policy exception apply?",
                "reasoning": "Explain referencing author history, active policies, cultural context"
            }
            # Progressive context reveal
            ctx = self._task_context.get("author_context", {})
            if ctx:
                obs["author_context"] = ctx

            if self.steps >= 1:
                policy_ctx = self._task_context.get("policy_context", {})
                if policy_ctx:
                    obs["policy_context"] = policy_ctx

            if self.steps >= 2:
                cultural_ctx = self._task_context.get("cultural_context", {})
                if cultural_ctx:
                    obs["cultural_context"] = cultural_ctx

        elif self.domain == "threat_assessment":
            obs["action_space"] = {
                "is_coordinated": "true/false — is this coordinated inauthentic behavior?",
                "threat_level": ["none", "low", "medium", "high", "critical"],
                "category": ["safe", "spam", "misinformation", "harassment", "hate_speech", "violence"],
                "action": ["keep", "label", "warn", "remove", "escalate", "ban"],
                "confidence": "float 0.0-1.0 — confidence in your assessment",
                "reasoning": "Threat analysis: detection → severity → response plan → prevention"
            }
            # Progressive threat signal reveal
            threat_ctx = self._task_context.get("threat_context", {})
            if threat_ctx:
                # Step 0: basic signals
                basic = {k: v for k, v in threat_ctx.items()
                         if k in ["related_accounts_posting_same", "similar_posts_24h",
                                  "reports_received", "account_age_days", "posting_interval_seconds"]}
                obs["threat_context"] = basic or threat_ctx

            if self.steps >= 1 and threat_ctx:
                # Step 1: coordination signals
                obs["threat_context"] = {k: v for k, v in threat_ctx.items()
                                          if k not in ["real_world_harm", "similar_attacks_other_cities"]}

            if self.steps >= 2 and threat_ctx:
                # Step 2+: full context including real-world impact
                obs["threat_context"] = threat_ctx

        return obs

    def _calculate_weighted_score(self) -> float:
        """Calculate weighted average where later steps count more."""
        if not self.rewards_history:
            return 0.5

        # Weights: step 1→1x, step 2→1.5x, step 3→2x, step 4→2.5x, step 5→3x
        weights = [1.0 + (i * 0.5) for i in range(len(self.rewards_history))]
        weighted_sum = sum(r * w for r, w in zip(self.rewards_history, weights))
        total_weight = sum(weights)

        return safe_clamp(weighted_sum / total_weight)

    def get_episode_summary(self) -> Dict:
        """Return summary of episode performance."""
        if not self.rewards_history:
            return {}

        return {
            "session_id": self.current_session_id,
            "task_id": self.task_id,
            "domain": self.domain,
            "difficulty": self.difficulty,
            "task_name": self.task_meta["name"],
            "total_steps": self.steps,
            "step_scores": self.rewards_history,
            "weighted_score": self._calculate_weighted_score(),
            "average_reward": sum(self.rewards_history) / len(self.rewards_history),
            "max_reward": max(self.rewards_history),
            "min_reward": min(self.rewards_history),
            "improvement": self.rewards_history[-1] - self.rewards_history[0] if len(self.rewards_history) > 1 else 0,
            "feedback_history": self.feedback_history,
        }
