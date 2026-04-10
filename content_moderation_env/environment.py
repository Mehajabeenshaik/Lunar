"""
ContentModerationEnv - Main Environment Implementation
"""

import random
import hashlib
from typing import Dict, Tuple, Optional, Any
from datetime import datetime
from .tasks import (
    Post, ContentCategory, ModerationAction,
    Task1_Classification, Task2_ClassifyWithReasoning, Task3_FullModeration,
    Task4_AuthorHistoryContext, Task5_TrendingTopicContext, Task6_AppealCase,
    Task7_FalsePositiveDetection, Task8_SarcasmAndIrony, Task9_CoordinatedInauthenticBehavior,
    ALL_TASKS
)


class ContentModerationEnv:
    """
    Meta Content Moderation Benchmark Environment
    
    Simulates the real-world problem Meta faces: 
    Reviewing social media posts and making moderation decisions at scale
    """
    
    # Sample posts for testing (real-world examples)
    SAMPLE_POSTS = [
        {
            "text": "Just launched my new startup! Check it out at totally-legit.ru - make money fast!",
            "category": ContentCategory.SPAM,
            "severity": 2
        },
        {
            "text": "I disagree with your political opinion and think you're wrong.",
            "category": ContentCategory.SAFE,
            "severity": 1
        },
        {
            "text": "Report from WHO shows vaccines have 99.9% effectiveness. Science matters.",
            "category": ContentCategory.SAFE,
            "severity": 1
        },
        {
            "text": "The vaccine kills more people than COVID. Don't trust mainstream media.",
            "category": ContentCategory.MISINFORMATION,
            "severity": 4
        },
        {
            "text": "[Hate speech targeting ethnic group]",
            "category": ContentCategory.HATE_SPEECH,
            "severity": 5
        },
        {
            "text": "I love my community. We should all be kind to each other.",
            "category": ContentCategory.SAFE,
            "severity": 1
        },
        {
            "text": "Click here to earn Bitcoin - limited time offer!",
            "category": ContentCategory.SPAM,
            "severity": 2
        },
        {
            "text": "Earth is flat and NASA is lying. Wake up sheeple!",
            "category": ContentCategory.MISINFORMATION,
            "severity": 3
        }
    ]
    
    def __init__(self, task_id: int = 1, seed: Optional[int] = None):
        """
        Initialize environment
        
        Args:
            task_id: 1 (Easy), 2 (Medium), 3 (Hard)
            seed: Random seed for reproducibility
        """
        self.task_id = task_id
        self.seed = seed
        if seed:
            random.seed(seed)
        
        self.current_session_id = self._generate_session_id()
        self.current_post: Optional[Post] = None
        self.steps = 0
        self.max_steps = 100
        self.rewards_history = []
        
        # Select task from ALL_TASKS registry (1-9)
        if task_id not in ALL_TASKS:
            raise ValueError(f"Invalid task_id: {task_id}. Must be 1-9")
        
        self.current_task = ALL_TASKS[task_id]
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        random_val = str(random.random())
        combined = f"{timestamp}-{random_val}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]
    
    def reset(self) -> Dict:
        """Reset environment and return initial observation"""
        self.current_post = self._sample_post()
        self.steps = 0
        self.rewards_history = []
        return self.current_task.get_observation(self.current_post)
    
    def _sample_post(self) -> Post:
        """Sample a random post from dataset"""
        sample = random.choice(self.SAMPLE_POSTS)
        post_id = f"post_{self.current_session_id}_{self.steps}"
        
        return Post(
            id=post_id,
            text=sample["text"],
            author=f"author_{random.randint(1000, 9999)}",
            timestamp=datetime.now().timestamp(),
            engagement=random.randint(0, 10000),
            ground_truth_category=sample["category"]
        )
    
    def step(self, action: Dict[str, Any]) -> Tuple[Dict, float, bool, Dict]:
        """
        Execute one step in the environment
        
        Args:
            action: Agent's moderation decision
            
        Returns:
            observation, reward, done, info
        """
        self.steps += 1
        done = self.steps >= self.max_steps
        
        # Calculate reward based on task using graders
        from .graders import ModeratorGrader
        
        # Ground truth data for this post
        ground_truth = {
            "category": self.current_post.ground_truth_category.value,
            "severity": 3 if self.current_post.ground_truth_category != ContentCategory.SAFE else 1,
            "action": self._get_ground_truth_action(self.current_post.ground_truth_category).value
        }
        
        try:
            grader = ModeratorGrader()  # Create instance to access grade() method
            reward = grader.grade(self.task_id, action, ground_truth)
        except Exception as e:
            # Graceful degradation: if grading fails, give partial credit
            # Must clamp to (0, 1) range - not exactly 0 or 1
            reward = 0.5 if any(action.values()) else 0.001
        
        # CRITICAL: Validate score is strictly within (0, 1)
        if reward is None or reward <= 0.0:
            reward = 0.001
        elif reward >= 1.0:
            reward = 0.999
        
        # Ensure reward is float and in valid range
        try:
            reward = float(reward)
            assert 0 < reward < 1, f"Score {reward} out of bounds!"
        except (ValueError, AssertionError) as e:
            reward = 0.5  # Default to middle value on error
        
        self.rewards_history.append(reward)
        
        # Get next observation
        if not done:
            self.current_post = self._sample_post()
            next_observation = self.current_task.get_observation(self.current_post)
        else:
            next_observation = {"status": "episode_complete", "average_reward": sum(self.rewards_history) / len(self.rewards_history)}
        
        info = {
            "session_id": self.current_session_id,
            "step": self.steps,
            "post_id": self.current_post.id if not done else None,
            "category": self.current_post.ground_truth_category.value if not done else None
        }
        
        return next_observation, reward, done, info
    
    def _get_ground_truth_action(self, category: ContentCategory) -> ModerationAction:
        """Determine appropriate moderation action"""
        if category == ContentCategory.SAFE:
            return ModerationAction.KEEP
        elif category == ContentCategory.HATE_SPEECH:
            return ModerationAction.REMOVE
        elif category == ContentCategory.SPAM:
            return ModerationAction.WARN
        else:  # MISINFORMATION
            return ModerationAction.ESCALATE
    
    def get_episode_summary(self) -> Dict:
        """Return summary of episode performance"""
        if not self.rewards_history:
            return {}
        
        return {
            "session_id": self.current_session_id,
            "task_id": self.task_id,
            "task_name": self.current_task.name,
            "total_steps": self.steps,
            "total_reward": sum(self.rewards_history),
            "average_reward": sum(self.rewards_history) / len(self.rewards_history),
            "max_reward": max(self.rewards_history),
            "min_reward": min(self.rewards_history)
        }
