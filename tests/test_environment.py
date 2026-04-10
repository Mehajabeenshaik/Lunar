import pytest
from content_moderation_env import ContentModerationEnv, Task1_Classification, Task2_ClassifyWithReasoning, Task3_FullModeration
from content_moderation_env.tasks import ContentCategory, ModerationAction


def test_env_initialization():
    """Test environment initialization"""
    env = ContentModerationEnv(task_id=1, seed=42)
    assert env.task_id == 1
    assert env.max_steps == 100


def test_task1_reset():
    """Test Task 1 reset"""
    env = ContentModerationEnv(task_id=1, seed=42)
    obs = env.reset()
    
    assert "post" in obs
    assert "action_space" in obs
    assert obs["task"] == "classification"
    assert len(obs["action_space"]) == 4


def test_task1_step():
    """Test Task 1 step"""
    env = ContentModerationEnv(task_id=1, seed=42)
    env.reset()
    
    action = {"category": "safe"}
    obs, reward, done, info = env.step(action)
    
    assert isinstance(reward, float)
    assert 0.0 <= reward <= 1.0
    assert "posts_id" in info or "step" in info


def test_task2_step():
    """Test Task 2 step with reasoning"""
    env = ContentModerationEnv(task_id=2, seed=42)
    env.reset()
    
    action = {
        "category": "spam",
        "reasoning": "Commercial solicitation",
        "severity": 2
    }
    obs, reward, done, info = env.step(action)
    
    assert isinstance(reward, float)
    assert 0.0 <= reward <= 1.0


def test_task3_step():
    """Test Task 3 full moderation"""
    env = ContentModerationEnv(task_id=3, seed=42)
    env.reset()
    
    action = {
        "category": "spam",
        "severity": 2,
        "action": "warn",
        "reasoning": "Unsolicited commercial content"
    }
    obs, reward, done, info = env.step(action)
    
    assert isinstance(reward, float)
    assert 0.0 <= reward <= 1.0


def test_episode_summary():
    """Test episode summary generation"""
    env = ContentModerationEnv(task_id=1, seed=42)
    env.reset()
    
    # Take several steps
    for i in range(5):
        action = {"category": "safe"}
        env.step(action)
    
    summary = env.get_episode_summary()
    
    assert "average_reward" in summary
    assert "total_steps" in summary
    assert summary["total_steps"] == 5


def test_task1_classification_reward():
    """Test Task 1 reward calculation"""
    correct_reward = Task1_Classification.calculate_reward("safe", ContentCategory.SAFE)
    incorrect_reward = Task1_Classification.calculate_reward("spam", ContentCategory.SAFE)
    
    assert correct_reward == 1.0
    assert incorrect_reward == 0.0


def test_task2_reasoning_reward():
    """Test Task 2 reward calculation"""
    # Perfect score
    reward = Task2_ClassifyWithReasoning.calculate_reward(
        "spam", 2, ContentCategory.SPAM, 2
    )
    assert reward == 1.0
    
    # Partial score (category correct, severity off by 1)
    reward = Task2_ClassifyWithReasoning.calculate_reward(
        "spam", 3, ContentCategory.SPAM, 2
    )
    assert reward == 0.75  # 1.0 category + 0.5 severity = 1.5 / 2 = 0.75


def test_task3_full_moderation_reward():
    """Test Task 3 reward calculation"""
    reward = Task3_FullModeration.calculate_reward(
        "spam", 2, "warn",
        ContentCategory.SPAM, 2, ModerationAction.WARN
    )
    assert reward == 1.0  # All 4 components correct


def test_multiple_episodes():
    """Test multiple episodes"""
    env = ContentModerationEnv(task_id=1, seed=42)
    
    # Episode 1
    obs = env.reset()
    assert obs is not None
    
    # Episode 2
    obs = env.reset()
    assert obs is not None


def test_invalid_task_id():
    """Test invalid task ID"""
    with pytest.raises(ValueError):
        ContentModerationEnv(task_id=99)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
