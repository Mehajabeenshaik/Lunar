"""
Lunar Content Moderation Benchmark — Pydantic v2 Typed Models
Type-safe request/response models for OpenEnv spec compliance.

Three domains:
  1. text_classification — classify posts by category and severity
  2. contextual_policy — enforce policies considering context, author history, cultural factors
  3. threat_assessment — detect coordinated threats, misinformation cascades, harassment networks
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


# ─── Enums ──────────────────────────────────────────────────────────────────

class Domain(str, Enum):
    """The three content moderation domains."""
    TEXT_CLASSIFICATION = "text_classification"
    CONTEXTUAL_POLICY = "contextual_policy"
    THREAT_ASSESSMENT = "threat_assessment"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ContentCategory(str, Enum):
    SAFE = "safe"
    HATE_SPEECH = "hate_speech"
    SPAM = "spam"
    MISINFORMATION = "misinformation"
    HARASSMENT = "harassment"
    VIOLENCE = "violence"


class ModerationAction(str, Enum):
    KEEP = "keep"
    LABEL = "label"
    WARN = "warn"
    REMOVE = "remove"
    ESCALATE = "escalate"
    BAN = "ban"


# ─── Observation  (returned by /reset and /step) ───────────────────────────

class Observation(BaseModel):
    """Environment observation — returned by reset() and step().
    
    Uses model_config extra='allow' to accept all dynamic fields
    from the environment (post, action_space, author_context, etc.)
    """
    model_config = {"extra": "allow"}

    session_id: str = Field(..., description="Unique session UUID")
    task_id: str = Field(..., description="Task identifier (e.g. 'task_1')")
    domain: str = Field(..., description="text_classification | contextual_policy | threat_assessment")
    difficulty: str = Field(..., description="easy | medium | hard")
    title: str = Field(..., description="Human-readable task name")
    description: str = Field(..., description="Full task description and requirements")

    # Post content — nested dict from environment
    post: Optional[Dict[str, Any]] = Field(None, description="Post text and metadata")

    # Episode state
    step_number: int = Field(0, description="Current step (starts at 0)")
    max_steps: int = Field(5, description="Maximum steps in this episode")
    feedback: Optional[str] = Field(None, description="Grader feedback from previous step")
    previous_scores: Optional[List[float]] = Field(None, description="Scores from previous steps")

    # Action space hint
    action_space: Optional[Dict[str, Any]] = Field(None, description="Available actions and expected format")

    # Context (domain-specific, progressively revealed)
    author_context: Optional[Dict[str, Any]] = Field(None, description="Author history, violations, account age")
    policy_context: Optional[Dict[str, Any]] = Field(None, description="Active policies, trending topics, exceptions")
    threat_context: Optional[Dict[str, Any]] = Field(None, description="Network data, coordination signals, related posts")
    cultural_context: Optional[Dict[str, Any]] = Field(None, description="Language, region, cultural norms")


# ─── Action  (sent to /step) ──────────────────────────────────────────────

class Action(BaseModel):
    """Agent action — sent in step() request."""
    session_id: str = Field(..., description="Must match active session from reset()")

    # Domain 1: Text Classification
    category: Optional[str] = Field(None, description="Content category (safe, hate_speech, spam, misinformation, ...)")
    severity: Optional[int] = Field(None, ge=1, le=5, description="Severity score 1-5")

    # Domain 2: Contextual Policy
    action: Optional[str] = Field(None, description="Moderation action (keep, label, warn, remove, escalate, ban)")
    policy_exception: Optional[bool] = Field(None, description="Whether a policy exception applies")

    # Domain 3: Threat Assessment
    threat_level: Optional[str] = Field(None, description="none, low, medium, high, critical")
    is_coordinated: Optional[bool] = Field(None, description="Whether coordinated inauthentic behavior is detected")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in assessment")

    # Shared
    reasoning: Optional[str] = Field(None, description="Explanation of the moderation decision")


# ─── Reward  (returned by /step) ─────────────────────────────────────────

class RewardInfo(BaseModel):
    """Reward information — returned by step()."""
    session_id: str
    task_id: str
    reward: float = Field(..., gt=0.0, lt=1.0, description="Reward strictly in (0, 1)")
    done: bool = Field(..., description="Is episode finished?")
    observation: Observation = Field(..., description="Updated observation with feedback")
    feedback: str = Field(..., description="Human-readable grading feedback")
    step_scores: Optional[List[float]] = Field(None, description="Per-step scores so far")
    info: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# ─── Request / Response Models ────────────────────────────────────────────

class ResetRequest(BaseModel):
    """Reset request body."""
    task_id: int = Field(default=1, ge=1, le=30, description="Task ID (1-30)")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")


class ResetResponse(BaseModel):
    """Reset response body."""
    session_id: str
    task_id: int
    observation: Observation


class StepRequest(BaseModel):
    """Step request body."""
    session_id: str
    action: Dict[str, Any] = Field(..., description="Agent's moderation action")


class StepResponse(BaseModel):
    """Step response body."""
    observation: Observation
    reward: float = Field(..., gt=0.0, lt=1.0)
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict)
    feedback: str = Field(default="", description="Grading feedback")
    step_scores: Optional[List[float]] = None


class StateResponse(BaseModel):
    """State response body."""
    session_id: str
    task_id: int
    domain: str
    difficulty: str
    step: int
    rewards: List[float]
    done: bool
    history: List[str]
