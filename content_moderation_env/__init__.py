"""
Content Moderation Environment — Meta's Real-World Problem
A multi-turn RL environment for training content moderation agents.

Three domains:
  1. text_classification — classify posts by category and severity
  2. contextual_policy — enforce policies considering context, author history, cultural factors
  3. threat_assessment — detect coordinated threats, misinformation cascades, harassment networks
"""

from .environment import ContentModerationEnv
from .graders import ModeratorGrader, safe_clamp, TASK_DOMAINS, TASK_DIFFICULTIES

__all__ = [
    "ContentModerationEnv",
    "ModeratorGrader",
    "safe_clamp",
    "TASK_DOMAINS",
    "TASK_DIFFICULTIES",
]
