"""
ContentModerationEnv — Multi-Turn Episode Environment

Key improvements over v1:
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


# ─── Task Metadata ──────────────────────────────────────────────────────────

TASK_METADATA = {
    # Domain 1: Text Classification (Tasks 1-10)
    1:  {"name": "Basic Post Classification", "desc": "Classify the post as safe, hate_speech, spam, or misinformation."},
    2:  {"name": "Spam Detection with Severity", "desc": "Identify spam content and rate its severity (1-5)."},
    3:  {"name": "Hate Speech Classification", "desc": "Detect hate speech with severity assessment and explanation."},
    4:  {"name": "Misinformation Flagging", "desc": "Identify false or misleading claims and explain why."},
    5:  {"name": "Multi-label Classification", "desc": "Content may belong to multiple violation categories."},
    6:  {"name": "Severity Calibration", "desc": "Assign precise severity scores with justification."},
    7:  {"name": "Nuanced Classification", "desc": "Handle borderline content requiring careful reasoning."},
    8:  {"name": "Context-Dependent Classification", "desc": "Classification that changes based on post context."},
    9:  {"name": "Sarcasm-Aware Classification", "desc": "Detect sarcasm that changes the meaning of content."},
    10: {"name": "Full Classification Pipeline", "desc": "Complete classification with category, severity, action, and reasoning."},
    # Domain 2: Contextual Policy (Tasks 11-20)
    11: {"name": "Author History Review", "desc": "Moderate considering author's prior violation history."},
    12: {"name": "New Account Screening", "desc": "Apply stricter policies for new/unverified accounts."},
    13: {"name": "Trending Topic Exceptions", "desc": "Apply policy exceptions for newsworthy content."},
    14: {"name": "Policy Update Application", "desc": "Apply newly updated content policies correctly."},
    15: {"name": "Cross-Cultural Moderation", "desc": "Moderate content considering cultural and regional context."},
    16: {"name": "Language-Aware Policy", "desc": "Apply language-specific moderation guidelines."},
    17: {"name": "Appeal Case Review", "desc": "Review an appeal and decide whether to overturn the original decision."},
    18: {"name": "Trust Score Assessment", "desc": "Assign user trust scores based on behavior patterns."},
    19: {"name": "False Positive Recovery", "desc": "Identify and correct false positive moderation decisions."},
    20: {"name": "Evolving Policy Compliance", "desc": "Moderate under changing policies with backward compatibility."},
    # Domain 3: Threat Assessment (Tasks 21-30)
    21: {"name": "Bot Network Detection", "desc": "Identify automated bot accounts in coordinated campaigns."},
    22: {"name": "Spam Campaign Detection", "desc": "Detect organized spam campaigns across multiple accounts."},
    23: {"name": "Harassment Network Mapping", "desc": "Identify coordinated harassment targeting individuals."},
    24: {"name": "Misinformation Cascade", "desc": "Track and assess spreading misinformation chains."},
    25: {"name": "Coordinated Inauthentic Behavior", "desc": "Detect state-sponsored or organized inauthentic accounts."},
    26: {"name": "Viral Threat Assessment", "desc": "Assess rapidly spreading dangerous content."},
    27: {"name": "Cross-Platform Threat", "desc": "Detect threats that span multiple platforms."},
    28: {"name": "Deepfake & Manipulation", "desc": "Identify synthetically generated or manipulated media."},
    29: {"name": "Extremism Detection", "desc": "Detect radicalization patterns and extremist content."},
    30: {"name": "Full Threat Response", "desc": "Complete threat assessment with detection, severity, response plan, and confidence."},
}


# ─── Sample Data ────────────────────────────────────────────────────────────

SAMPLE_POSTS = [
    {"text": "Just launched my startup! Check it out at totally-legit.ru - make money fast! 💰💰💰",
     "category": "spam", "severity": 2, "action": "remove",
     "threat_level": "low", "is_coordinated": False},
    {"text": "I disagree with your political opinion. That doesn't make either of us bad people.",
     "category": "safe", "severity": 1, "action": "keep",
     "threat_level": "none", "is_coordinated": False},
    {"text": "Report from WHO confirms vaccine effectiveness at 99.9%. Science saves lives.",
     "category": "safe", "severity": 1, "action": "keep",
     "threat_level": "none", "is_coordinated": False},
    {"text": "The vaccine is a bio-weapon engineered by the elites. EXPOSED! Share before they delete!",
     "category": "misinformation", "severity": 4, "action": "remove",
     "threat_level": "high", "is_coordinated": True},
    {"text": "[Targeted hateful speech against ethnic group with dehumanizing language]",
     "category": "hate_speech", "severity": 5, "action": "ban",
     "threat_level": "critical", "is_coordinated": False},
    {"text": "I love my community. We should all treat each other with kindness and respect.",
     "category": "safe", "severity": 1, "action": "keep",
     "threat_level": "none", "is_coordinated": False},
    {"text": "BREAKING: 5G towers cause cancer! Government hiding the truth! RT to spread awareness!",
     "category": "misinformation", "severity": 3, "action": "label",
     "threat_level": "medium", "is_coordinated": True},
    {"text": "This user's posts are garbage. Everyone report this account and get them banned.",
     "category": "harassment", "severity": 3, "action": "warn",
     "threat_level": "medium", "is_coordinated": False},
    {"text": "Earn $5000/day from home! Click bit.ly/scam123 Join 10,000 others NOW!",
     "category": "spam", "severity": 3, "action": "remove",
     "threat_level": "low", "is_coordinated": True},
    {"text": "Earth is flat. NASA is lying. Wake up sheeple! Share if you agree!",
     "category": "misinformation", "severity": 2, "action": "label",
     "threat_level": "low", "is_coordinated": False},
]


# ─── Environment ────────────────────────────────────────────────────────────

class ContentModerationEnv:
    """
    Multi-turn content moderation environment.

    Key features:
    - 5-step episodes with grader feedback after each step
    - Progressive context reveal (more context each step)
    - Weighted scoring (later steps worth 2x more)
    - 3 genuinely different domains
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
        self.current_post_data: Optional[Dict] = None

        # Task info
        self.domain = TASK_DOMAINS.get(task_id, "text_classification")
        self.difficulty = TASK_DIFFICULTIES.get(task_id, "easy")
        self.task_meta = TASK_METADATA.get(task_id, {"name": f"Task {task_id}", "desc": "Content moderation task"})

    def _generate_session_id(self) -> str:
        combined = f"{datetime.now().isoformat()}-{random.random()}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]

    def reset(self) -> Dict:
        """Reset environment and return initial observation."""
        self.steps = 0
        self.done = False
        self.rewards_history = []
        self.feedback_history = []
        self.current_post_data = random.choice(SAMPLE_POSTS)

        return self._build_observation()

    def step(self, action: Dict[str, Any]) -> Tuple[Dict, float, bool, Dict]:
        """
        Execute one step. Agent's action is graded, feedback is returned.

        Returns: (observation, reward, done, info)
        """
        self.steps += 1

        # Build ground truth from current post
        ground_truth = self._build_ground_truth()

        # Grade with domain-specific grader + feedback
        score, feedback, _ = self.grader.grade_with_feedback(
            self.task_id, action, ground_truth, self.steps
        )
        score = safe_clamp(score)

        self.rewards_history.append(score)
        self.feedback_history.append(feedback)

        # Episode ends after max steps or if agent achieves high score
        self.done = self.steps >= self.MAX_STEPS or (score >= 0.90 and self.steps >= 2)

        # Build next observation with feedback
        observation = self._build_observation(feedback=feedback)

        # Calculate weighted final score (later steps worth more)
        if self.done:
            weighted_score = self._calculate_weighted_score()
        else:
            weighted_score = score

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
        post = self.current_post_data

        obs = {
            "session_id": self.current_session_id,
            "task_id": f"task_{self.task_id}",
            "domain": self.domain,
            "difficulty": self.difficulty,
            "title": self.task_meta["name"],
            "description": self.task_meta["desc"],
            "post": {
                "text": post["text"],
                "engagement": random.randint(10, 50000),
                "author": f"user_{random.randint(1000, 9999)}",
                "timestamp": datetime.now().isoformat(),
            },
            "step_number": self.steps,
            "max_steps": self.MAX_STEPS,
        }

        # Feedback from previous step
        if feedback:
            obs["feedback"] = feedback
        if self.rewards_history:
            obs["previous_scores"] = self.rewards_history.copy()

        # Domain-specific action space hints
        if self.domain == "text_classification":
            obs["action_space"] = {
                "category": ["safe", "hate_speech", "spam", "misinformation", "harassment", "violence"],
                "severity": "integer 1-5",
                "action": ["keep", "label", "warn", "remove", "escalate", "ban"],
                "reasoning": "string explaining your decision"
            }
        elif self.domain == "contextual_policy":
            obs["action_space"] = {
                "category": ["safe", "hate_speech", "spam", "misinformation", "harassment", "violence"],
                "action": ["keep", "label", "warn", "remove", "escalate", "ban"],
                "policy_exception": "true/false",
                "reasoning": "string referencing context factors"
            }
            # Progressive context reveal
            obs["author_context"] = {
                "prior_violations": random.randint(0, 5),
                "account_age_days": random.randint(1, 3650),
                "verified": random.choice([True, False]),
                "follower_count": random.randint(0, 1000000),
            }
            if self.steps >= 1:
                obs["policy_context"] = {
                    "active_policies": ["no_hate_speech", "no_spam", "label_misinformation"],
                    "exceptions": ["public_interest_newsworthy", "artistic_expression"],
                    "region": random.choice(["US", "EU", "IN", "BR", "Global"]),
                }
            if self.steps >= 2:
                obs["cultural_context"] = {
                    "language": random.choice(["en", "es", "hi", "ar", "zh"]),
                    "cultural_norms": "Consider regional context and local standards.",
                }
        elif self.domain == "threat_assessment":
            obs["action_space"] = {
                "is_coordinated": "true/false",
                "threat_level": ["none", "low", "medium", "high", "critical"],
                "category": ["safe", "spam", "misinformation", "harassment", "hate_speech"],
                "action": ["keep", "label", "warn", "remove", "escalate", "ban"],
                "confidence": "float 0-1",
                "reasoning": "string with threat analysis"
            }
            obs["threat_context"] = {
                "related_accounts": random.randint(1, 20),
                "similar_posts_24h": random.randint(0, 100),
                "reports_received": random.randint(0, 50),
            }
            if self.steps >= 1:
                obs["threat_context"]["ip_overlap"] = random.choice([True, False])
                obs["threat_context"]["creation_date_cluster"] = random.choice([True, False])
            if self.steps >= 2:
                obs["threat_context"]["network_graph_density"] = round(random.random(), 2)
                obs["threat_context"]["known_campaign_similarity"] = round(random.random() * 0.8, 2)

        return obs

    def _build_ground_truth(self) -> Dict:
        """Build ground truth from current post data."""
        post = self.current_post_data
        gt = {
            "category": post["category"],
            "severity": post["severity"],
            "action": post["action"],
        }

        if self.domain == "contextual_policy":
            gt["policy_exception"] = post.get("category") == "safe"

        if self.domain == "threat_assessment":
            gt["is_coordinated"] = post.get("is_coordinated", False)
            gt["threat_level"] = post.get("threat_level", "none")

        return gt

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
