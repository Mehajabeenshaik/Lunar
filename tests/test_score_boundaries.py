"""Quick validation: all 30 tasks, all 3 domains, scores in (0,1), multi-turn works."""
import sys, json
sys.path.insert(0, ".")

from content_moderation_env.graders import ModeratorGrader, safe_clamp
from content_moderation_env.environment import ContentModerationEnv

def test_graders():
    g = ModeratorGrader()
    preds = [
        {"category": "safe","severity":1,"action":"keep","reasoning":"This is safe content with no issues.","is_coordinated":False,"threat_level":"none","confidence":0.9},
        {"category": "spam","severity":3,"action":"remove","reasoning":"Spam pattern detected due to repeated links.","is_coordinated":True,"threat_level":"medium","confidence":0.7},
        {"category": "hate_speech","severity":5,"action":"ban","reasoning":"","is_coordinated":False,"threat_level":"high","confidence":0.5},
        {},
    ]
    gts = [
        {"category": "safe","severity":1,"action":"keep","is_coordinated":False,"threat_level":"none","policy_exception":False},
        {"category": "spam","severity":3,"action":"remove","is_coordinated":True,"threat_level":"medium","policy_exception":False},
        {"category": "misinformation","severity":4,"action":"label","is_coordinated":True,"threat_level":"high","policy_exception":True},
        {"category": "safe","severity":1,"action":"keep","is_coordinated":False,"threat_level":"none"},
    ]
    fails = 0
    for tid in range(1, 31):
        for pred, gt in zip(preds, gts):
            score, feedback, done = g.grade_with_feedback(tid, pred, gt, step_num=1)
            if score <= 0.0 or score >= 1.0:
                print(f"FAIL: Task {tid} score={score}")
                fails += 1
    print(f"Grader test: {30*4} cases, {fails} failures")
    return fails == 0

def test_environment():
    fails = 0
    for tid in [1, 5, 10, 15, 20, 25, 30]:
        env = ContentModerationEnv(task_id=tid, seed=42)
        obs = env.reset()
        assert "session_id" in obs, f"Task {tid}: missing session_id in reset"
        assert "post" in obs, f"Task {tid}: missing post in reset"

        for step in range(1, 6):
            action = {"category":"safe","severity":1,"action":"keep",
                      "reasoning":"Safe content.","is_coordinated":False,
                      "threat_level":"none","confidence":0.8,"policy_exception":False}
            obs, reward, done, info = env.step(action)
            if reward <= 0.0 or reward >= 1.0:
                print(f"FAIL: Task {tid} step {step} reward={reward}")
                fails += 1
            if done:
                break

        summary = env.get_episode_summary()
        assert "weighted_score" in summary
    print(f"Environment test: 7 episodes, {fails} failures")
    return fails == 0

def test_api_import():
    from app import app
    print("API import OK")
    return True

if __name__ == "__main__":
    r1 = test_graders()
    r2 = test_environment()
    r3 = test_api_import()
    ok = all([r1, r2, r3])
    print(f"\nOVERALL: {'ALL PASS' if ok else 'FAILURES'}")
    sys.exit(0 if ok else 1)
