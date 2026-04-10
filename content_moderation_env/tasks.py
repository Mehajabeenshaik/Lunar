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


# Domain 2: Context-Aware Moderation (Tasks 4-6)

@dataclass
class AuthorContext:
    """Author metadata for context-aware moderation"""
    prior_violations: int
    account_age_days: int
    follower_count: int


class Task4_AuthorHistoryContext:
    """
    Easy Task: Context-Aware Moderation with Author History
    
    Agent must consider author's prior violation history
    when making moderation decision. Account age and follower count
    influence whether content should be handled more severely.
    
    Observation: Post + author history
    Action: Dict with category, severity, reasoning
    Reward: Based on whether severity was appropriately adjusted
    """
    
    name = "Task 4: Author History Context"
    description = "Classify posts considering author's violation history and account status"
    difficulty = "easy"
    
    @staticmethod
    def get_observation(post: Post, author_context: AuthorContext) -> Dict:
        """Return post with author context"""
        return {
            "task": "author_history_context",
            "post": post.to_dict(),
            "author_context": {
                "prior_violations": author_context.prior_violations,
                "account_age_days": author_context.account_age_days,
                "follower_count": author_context.follower_count
            },
            "instructions": "Consider author history when assigning severity. Repeat offenders should have higher severity."
        }


class Task5_TrendingTopicContext:
    """
    Medium Task: Policy Exception Based on Trending Topic
    
    Some content that would normally be removed might be allowed
    in specific contexts (e.g., political speech during elections).
    Agent must recognize policy exceptions based on trending topics
    and trending policies.
    
    Observation: Post + trending_topic + policy_override
    Action: Dict with category, action, policy_exception reasoning
    Reward: Based on recognizing correct policy exception
    """
    
    name = "Task 5: Trending Topic Context"
    description = "Apply policy exceptions based on trending topics and context"
    difficulty = "medium"
    
    @staticmethod
    def get_observation(post: Post, trending_topic: str, policy_override: str) -> Dict:
        """Return post with trending context"""
        return {
            "task": "trending_topic_context",
            "post": post.to_dict(),
            "trending_topic": trending_topic,
            "policy_note": f"Policy override active: {policy_override}",
            "instructions": "Recognize policy exceptions. Content that would normally be removed may be labeled instead."
        }


class Task6_AppealCase:
    """
    Hard Task: Appeal Case Review
    
    Users can appeal moderation decisions. Must decide whether to:
    1. Overturn the decision (original was wrong)
    2. Uphold the decision (original was correct)
    
    Observe: Original decision + appeal evidence
    Action: appeal_verdict (overturn/uphold), new_action, reasoning
    Reward: Based on correct appeal decision and reasoning quality
    """
    
    name = "Task 6: Appeal Case Review"
    description = "Review appeals of moderation decisions and determine if original decision should be overturned"
    difficulty = "hard"
    
    @staticmethod
    def get_observation(original_decision: Dict, appeal_evidence: Dict) -> Dict:
        """Return appeal case information"""
        return {
            "task": "appeal_case",
            "original_decision": {
                "action": original_decision.get("action"),
                "category": original_decision.get("category"),
                "confidence": original_decision.get("confidence")
            },
            "appeal_evidence": {
                "author_claim": appeal_evidence.get("author_claim"),
                "context": appeal_evidence.get("context"),
                "similar_content_approved": appeal_evidence.get("similar_content_approved")
            },
            "instructions": "Decide whether to overturn or uphold based on appeal evidence. Consider precedent."
        }


# Domain 3: Edge Cases & Escalation (Tasks 7-9)

class Task7_FalsePositiveDetection:
    """
    Easy Task: False Positive Detection
    
    Many moderation systems make mistakes (false positives).
    Agent must identify when content was incorrectly flagged
    for violation (e.g., "kill this project deadline" is not violence).
    
    Observation: Post flagged as violation, context showing it's safe
    Action: Dict with is_false_positive boolean, category
    Reward: Binary accuracy (correct or incorrect call)
    """
    
    name = "Task 7: False Positive Detection"
    description = "Identify and correct false positive moderation flags"
    difficulty = "easy"
    
    @staticmethod
    def get_observation(post: Post, flagged_as: str, context: str) -> Dict:
        """Return potentially misclassified post"""
        return {
            "task": "false_positive_detection",
            "post": post.to_dict(),
            "flag_reason": f"Flagged as {flagged_as}",
            "additional_context": context,
            "instructions": "Determine if this is a false positive (incorrectly flagged violation)"
        }


class Task8_SarcasmAndIrony:
    """
    Medium Task: Sarcasm & Irony Detection
    
    Critical for content moderation: "Great job on that feature 🙄"
    in a code review isn't harassment, it's sarcastic feedback.
    Must detect tone and adjust severity accordingly.
    
    Observation: Post with potential sarcasm, target, context
    Action: Dict with tone, severity, category adjusted for tone
    Reward: Based on tone detection and severity appropriateness
    """
    
    name = "Task 8: Sarcasm & Irony Detection"
    description = "Detect sarcasm and irony to avoid false positives in specific contexts"
    difficulty = "medium"
    
    @staticmethod
    def get_observation(post: Post, target: str, context: str) -> Dict:
        """Return post potentially containing sarcasm"""
        return {
            "task": "sarcasm_irony_detection",
            "post": post.to_dict(),
            "target": target,
            "context": context,
            "instructions": "Detect tone (sarcastic, constructive, neutral) and adjust moderation decision accordingly"
        }


class Task9_CoordinatedInauthenticBehavior:
    """
    Hard Task: Coordinated Inauthentic Behavior (CIB) Detection
    
    Most complex: Detect organized harassment campaigns.
    Multiple accounts created same day, similar IPs, synchronized posting,
    all posting similar content.
    
    Must decide:
    1. Are these accounts coordinated? (boolean)
    2. Individual action (remove_and_ban, warn, etc.)
    3. Network action (investigate_network, escalate_to_team)
    
    Observation: Multiple posts from similar accounts + metadata
    Action: Dict with CIB detection, individual and network actions
    Reward: Multi-component grading
    """
    
    name = "Task 9: Coordinated Inauthentic Behavior"
    description = "Detect and respond to organized harassment campaigns across multiple accounts"
    difficulty = "hard"
    
    @staticmethod
    def get_observation(posts_with_metadata: Dict) -> Dict:
        """Return multiple posts with network metadata"""
        return {
            "task": "coordinated_inauthentic_behavior",
            "posts": posts_with_metadata.get("posts", []),
            "metadata": {
                "accounts_created_same_day": posts_with_metadata.get("accounts_created_same_day"),
                "similar_ip": posts_with_metadata.get("similar_ip"),
                "posting_pattern": posts_with_metadata.get("posting_pattern")
            },
            "instructions": "Identify coordinated inauthentic behavior. Determine individual and network-level actions."
        }


# Task Registry: All 9 Tasks
ALL_TASKS = {
    1: Task1_Classification,
    2: Task2_ClassifyWithReasoning,
    3: Task3_FullModeration,
    4: Task4_AuthorHistoryContext,
    5: Task5_TrendingTopicContext,
    6: Task6_AppealCase,
    7: Task7_FalsePositiveDetection,
    8: Task8_SarcasmAndIrony,
    9: Task9_CoordinatedInauthenticBehavior,
}

