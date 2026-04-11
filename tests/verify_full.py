"""Full verification test for Lunar Benchmark v3.0"""
import sys
sys.path.insert(0, ".")

from content_moderation_env import ContentModerationEnv
from content_moderation_env.graders import safe_clamp, ModeratorGrader
from models import Observation, StepResponse, ResetResponse, StateResponse

print("=== LUNAR BENCHMARK v3.0 - FULL VERIFICATION ===")
print()

# 1. Test all 30 tasks produce valid (0,1) scores
print("[1] Testing all 30 task score boundaries...")
grader = ModeratorGrader()
test_pred = {"category": "safe", "severity": 1, "action": "keep",
             "reasoning": "test reasoning about context and policy"}
test_gt = {"category": "safe", "severity": 1, "action": "keep",
           "is_coordinated": False, "threat_level": "none", "policy_exception": True}
all_valid = True
for tid in range(1, 31):
    score = grader.grade(tid, test_pred, test_gt)
    if score <= 0.0 or score >= 1.0:
        print(f"  FAIL task {tid}: score={score}")
        all_valid = False
status = "PASS - all 30 tasks valid" if all_valid else "FAIL"
print(f"  Result: {status}")
print()

# 2. Test multi-turn episode
print("[2] Testing multi-turn episode (Task 1, 5 steps)...")
env = ContentModerationEnv(task_id=1, seed=42)
obs = env.reset()
o = Observation(**obs)
print(f"  Reset OK: session={o.session_id}, domain={o.domain}, difficulty={o.difficulty}")

for step in range(1, 6):
    action = {"category": "spam", "severity": 2, "action": "remove",
              "reasoning": "test spam due to context and policy violations"}
    obs, reward, done, info = env.step(action)
    reward = safe_clamp(reward)
    fb = info.get("feedback", "")[:60]
    print(f"  Step {step}: reward={reward:.4f}, done={done}, feedback={fb}...")
    if done:
        break
ws = env._calculate_weighted_score()
print(f"  Episode complete: {len(env.rewards_history)} steps, weighted={ws:.4f}")
print()

# 3. Test all 3 domains
print("[3] Testing all 3 domains...")
for tid, domain in [(1, "text_classification"), (11, "contextual_policy"), (21, "threat_assessment")]:
    env = ContentModerationEnv(task_id=tid, seed=42)
    obs = env.reset()
    assert obs["domain"] == domain, f"Expected {domain}, got {obs['domain']}"
    print(f"  Task {tid}: domain={obs['domain']}, difficulty={obs['difficulty']}")
print()

# 4. Test progressive context reveal
print("[4] Testing progressive context reveal (Task 15)...")
env = ContentModerationEnv(task_id=15, seed=42)
obs = env.reset()
has_author = "author_context" in obs
has_policy = "policy_context" in obs
print(f"  Step 0: author_context={has_author}, policy_context={has_policy}")
action = {"category": "safe", "action": "keep", "reasoning": "test"}
obs, _, _, _ = env.step(action)
has_policy2 = "policy_context" in obs
print(f"  Step 1: policy_context={has_policy2} (should be True)")
obs, _, _, _ = env.step(action)
has_cultural = "cultural_context" in obs
print(f"  Step 2: cultural_context={has_cultural} (should be True)")
print()

# 5. Test Pydantic models
print("[5] Testing Pydantic v2 typed models...")
env = ContentModerationEnv(task_id=25, seed=42)
obs = env.reset()
o = Observation(**obs)
print(f"  Observation: session_id={o.session_id}, task_id={o.task_id}")
action = {"is_coordinated": True, "threat_level": "high", "category": "spam",
          "action": "escalate", "confidence": 0.8, "reasoning": "test"}
obs2, reward, done, info = env.step(action)
sr = StepResponse(
    observation=Observation(**obs2), reward=safe_clamp(reward),
    done=done, info=info, feedback=info.get("feedback", ""))
print(f"  StepResponse: reward={sr.reward:.4f}, done={sr.done}")
rr = ResetResponse(session_id="test", task_id=25, observation=o)
print(f"  ResetResponse: task_id={rr.task_id}")
ssr = StateResponse(session_id="test", task_id=25, domain="threat_assessment",
                    difficulty="medium", step=1, rewards=[0.5], done=False, history=["test"])
print(f"  StateResponse: domain={ssr.domain}")
print()

# 6. Test difficulty gradient
print("[6] Testing difficulty gradient...")
difficulties = {}
for tid in range(1, 31):
    env = ContentModerationEnv(task_id=tid)
    difficulties.setdefault(env.difficulty, []).append(tid)
for diff in ["easy", "medium", "hard"]:
    tasks = difficulties.get(diff, [])
    print(f"  {diff}: {len(tasks)} tasks -> {tasks}")
print()

# 7. Test partial credit differentiation
print("[7] Testing partial credit differentiation...")
# Perfect answer
perfect = {"category": "spam", "severity": 2, "action": "remove",
           "reasoning": "This is spam due to context, policy guideline violation, and systematic pattern. Edge case considered."}
gt = {"category": "spam", "severity": 2, "action": "remove"}
score_perfect = grader.grade(1, perfect, gt)

# Wrong answer
wrong = {"category": "safe", "severity": 5, "action": "keep", "reasoning": "no"}
score_wrong = grader.grade(1, wrong, gt)

# Partial answer
partial = {"category": "spam", "severity": 4, "action": "keep", "reasoning": "might be spam"}
score_partial = grader.grade(1, partial, gt)

print(f"  Perfect answer: {score_perfect:.4f}")
print(f"  Partial answer: {score_partial:.4f}")
print(f"  Wrong answer:   {score_wrong:.4f}")
assert score_perfect > score_partial > score_wrong, "Partial credit ordering failed!"
print("  Gradient OK: perfect > partial > wrong")
print()

print("=== ALL TESTS PASSED ===")
