"""
Content Moderation Environment - Meta's Real-World Problem
A learning agent that reviews social media posts and decides: keep / warn / remove / escalate
"""

from .environment import ContentModerationEnv
from .graders import ModeratorGrader
from .tasks import (
    Task1_Classification, Task2_ClassifyWithReasoning, Task3_FullModeration,
    Task4_AuthorHistoryContext, Task5_TrendingTopicContext, Task6_AppealCase,
    Task7_FalsePositiveDetection, Task8_SarcasmAndIrony, Task9_CoordinatedInauthenticBehavior,
    ALL_TASKS
)

__all__ = [
    "ContentModerationEnv",
    "ModeratorGrader",
    "Task1_Classification",
    "Task2_ClassifyWithReasoning", 
    "Task3_FullModeration",
    "Task4_AuthorHistoryContext",
    "Task5_TrendingTopicContext",
    "Task6_AppealCase",
    "Task7_FalsePositiveDetection",
    "Task8_SarcasmAndIrony",
    "Task9_CoordinatedInauthenticBehavior",
    "ALL_TASKS"
]
