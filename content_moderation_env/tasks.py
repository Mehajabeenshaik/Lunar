"""
Content Moderation Tasks - Easy, Medium, Hard
Mirrors Meta's real-world content moderation at billion-post scale
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Tuple


class ContentCategory(str, Enum):
    """Content classification categories"""
    SAFE = "safe"
    HATE_SPEECH = "hate_speech"
    SPAM = "spam"
    MISINFORMATION = "misinformation"


class ModerationAction(str, Enum):
    """Actions for moderation"""
    KEEP = "keep"
    WARN = "warn"
    REMOVE = "remove"
    ESCALATE = "escalate"


@dataclass
class Post:
    """Social media post to moderate"""
    id: str
    text: str
    author: str
    timestamp: float
    engagement: int  # likes/shares
    ground_truth_category: ContentCategory
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "text": self.text,
            "author": self.author,
            "timestamp": self.timestamp,
            "engagement": self.engagement
        }


class Task1_Classification:
    """
    Easy Task: Classify a post
    
    Agent must classify post as: Safe / Hate Speech / Spam / Misinformation
    Observation: Post content (without label)
    Action: One of 4 categories
    Reward: 1.0 if correct, 0.0 if wrong
    """
    
    name = "Task 1: Post Classification"
    description = "Classify social media posts into Safe, Hate Speech, Spam, or Misinformation"
    difficulty = "easy"
    
    @staticmethod
    def calculate_reward(predicted_category: str, ground_truth: ContentCategory) -> float:
        """Exact match scoring"""
        try:
            predicted = ContentCategory(predicted_category.lower())
            return 1.0 if predicted == ground_truth else 0.0
        except (ValueError, AttributeError):
            return 0.0
    
    @staticmethod
    def get_observation(post: Post) -> Dict:
        """Return only the post content, not the label"""
        return {
            "task": "classification",
            "post": post.to_dict(),
            "action_space": ["safe", "hate_speech", "spam", "misinformation"]
        }


class Task2_ClassifyWithReasoning:
    """
    Medium Task: Classify + Provide Reasoning + Severity
    
    Agent must:
    1. Classify post (Safe/Hate/Spam/Misinformation)
    2. Provide brief reasoning
    3. Assign severity score (1-5)
    
    Observation: Post content
    Action: Dict with category, reasoning, severity
    Reward: Composite score (category=50%, severity=50%)
    """
    
    name = "Task 2: Classification with Reasoning"
    description = "Classify posts with explanations and severity scoring"
    difficulty = "medium"
    
    @staticmethod
    def calculate_reward(
        predicted_category: str,
        predicted_severity: int,
        ground_truth_category: ContentCategory,
        ground_truth_severity: int
    ) -> float:
        """Multi-factor scoring"""
        try:
            predicted = ContentCategory(predicted_category.lower())
        except (ValueError, AttributeError):
            predicted = None
        
        # Category accuracy (50% of score)
        category_score = 1.0 if predicted == ground_truth_category else 0.0
        
        # Severity accuracy (50% of score) - allow ±1 range for partial credit
        severity_diff = abs(predicted_severity - ground_truth_severity)
        if severity_diff == 0:
            severity_score = 1.0
        elif severity_diff == 1:
            severity_score = 0.5
        else:
            severity_score = 0.0
        
        return (category_score * 0.5) + (severity_score * 0.5)
    
    @staticmethod
    def get_observation(post: Post) -> Dict:
        """Return post content for classification with reasoning task"""
        return {
            "task": "classification_with_reasoning",
            "post": post.to_dict(),
            "categories": ["safe", "hate_speech", "spam", "misinformation"],
            "severity_range": [1, 2, 3, 4, 5],
            "instructions": "Provide category, reasoning, and severity (1-5)"
        }


class Task3_FullModeration:
    """
    Hard Task: Full Moderation Decision
    
    Agent must make complete moderation decision:
    1. Classify post
    2. Assign severity (1-5)
    3. Choose action (keep/warn/remove/escalate)
    4. Provide explanation
    
    Observation: Post content
    Action: Dict with all 4 components
    Reward: Weighted average (25% each component)
    """
    
    name = "Task 3: Full Moderation Decision"
    description = "Complete moderation decision with classification, severity, action, and explanation"
    difficulty = "hard"
    
    @staticmethod
    def calculate_reward(
        predicted_category: str,
        predicted_severity: int,
        predicted_action: str,
        ground_truth_category: ContentCategory,
        ground_truth_severity: int,
        ground_truth_action: ModerationAction
    ) -> float:
        """Weighted composite scoring (25% each)"""
        scores = {}
        
        # Category accuracy (25%)
        try:
            predicted = ContentCategory(predicted_category.lower())
            scores['category'] = 1.0 if predicted == ground_truth_category else 0.0
        except (ValueError, AttributeError):
            scores['category'] = 0.0
        
        # Severity accuracy (25%) - with ±1 partial credit
        severity_diff = abs(predicted_severity - ground_truth_severity)
        if severity_diff == 0:
            scores['severity'] = 1.0
        elif severity_diff == 1:
            scores['severity'] = 0.5
        else:
            scores['severity'] = 0.0
        
        # Action accuracy (25%)
        try:
            predicted_act = ModerationAction(predicted_action.lower())
            scores['action'] = 1.0 if predicted_act == ground_truth_action else 0.0
        except (ValueError, AttributeError):
            scores['action'] = 0.0
        
        # All 4 components must be reasonable (25%) - simplified to action correctness bonus
        # In production, this would evaluate explanation quality
        scores['explanation'] = scores['action']  # Simplified: action correctness implies good reasoning
        
        return sum(scores.values()) / 4.0
    
    @staticmethod
    def get_observation(post: Post) -> Dict:
        """Return post for full moderation task"""
        return {
            "task": "full_moderation",
            "post": post.to_dict(),
            "categories": ["safe", "hate_speech", "spam", "misinformation"],
            "severity_range": [1, 2, 3, 4, 5],
            "actions": ["keep", "warn", "remove", "escalate"],
            "instructions": "Provide category, severity, action, and explanation"
        }
