#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE VERIFICATION TEST
Validates ALL requirements for submission #70
"""
import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("FINAL COMPREHENSIVE VERIFICATION TEST")
print("=" * 80)

# TEST 1: Check required files exist
print("\n[TEST 1] Checking required files...")
required_files = [
    "openenv.yaml",
    "inference.py",
    "app.py",
    "Dockerfile",
    "requirements.txt",
    "README.md",
    "content_moderation_env/__init__.py",
    "content_moderation_env/environment.py",
    "content_moderation_env/graders.py",
    "content_moderation_env/tasks.py",
]

all_files_exist = True
for file in required_files:
    exists = os.path.exists(file)
    status = "✅" if exists else "❌"
    print(f"  {status} {file}")
    if not exists:
        all_files_exist = False

if not all_files_exist:
    print("\n🚨 FAILED: Missing required files!")
    sys.exit(1)
print("✅ PASSED: All required files exist")

# TEST 2: Verify openenv.yaml configuration
print("\n[TEST 2] Checking openenv.yaml configuration...")
import yaml
with open("openenv.yaml", "r") as f:
    openenv = yaml.safe_load(f)

checks = {
    "spec_version == 1": openenv.get("spec_version") == 1,
    "task count == 30": openenv.get("total_tasks") == 30,
    "reward_range [0.001, 0.999]": openenv.get("reward_range") == [0.001, 0.999],
    "grader count == 1": openenv.get("total_graders") == 1,
    "30 tasks defined": len(openenv.get("tasks", [])) == 30,
}

for check_name, result in checks.items():
    status = "✅" if result else "❌"
    print(f"  {status} {check_name}")
    if not result:
        print(f"\n🚨 FAILED: {check_name}")
        sys.exit(1)

print("✅ PASSED: openenv.yaml is correctly configured")

# TEST 3: Test all 30 graders
print("\n[TEST 3] Testing all 30 graders for boundary safety...")
from content_moderation_env.graders import OptimizedModeratorGrader

grader = OptimizedModeratorGrader()
violations = []

for task_id in range(1, 31):
    try:
        # Simple test case
        prediction = {"answer": "correct"}
        ground_truth = {"answer": "correct"}
        
        score = grader.grade(task_id, prediction, ground_truth, use_cache=False)
        
        # Check boundaries
        if score is None or score <= 0.0 or score >= 1.0:
            violations.append((task_id, score, "OUT_OF_BOUNDS"))
        elif not isinstance(score, float):
            violations.append((task_id, score, "NOT_FLOAT"))
        
        status = "✅" if (0 < score < 1) else "❌"
        print(f"  {status} Task {task_id}: {score:.4f}")
        
    except Exception as e:
        violations.append((task_id, None, str(e)))
        print(f"  ❌ Task {task_id}: ERROR - {e}")

if violations:
    print(f"\n🚨 FAILED: {len(violations)} graders have boundary violations!")
    for task_id, score, reason in violations:
        print(f"  Task {task_id}: {score} ({reason})")
    sys.exit(1)

print("✅ PASSED: All 30 graders produce safe boundary scores")

# TEST 4: Test environment.step() for all 30 tasks
print("\n[TEST 4] Testing environment.step() for all 30 tasks...")
from content_moderation_env import ContentModerationEnv

env_violations = []
for task_id in range(1, 31):
    try:
        env = ContentModerationEnv(task_id=task_id)
        env.reset()
        
        action = {
            "category": "safe",
            "severity": 1,
            "action": "approve",
            "reasoning": "Test"
        }
        
        obs, reward, done, info = env.step(action)
        
        if reward is None or reward <= 0.0 or reward >= 1.0:
            env_violations.append((task_id, reward, "OUT_OF_BOUNDS"))
        elif not isinstance(reward, float):
            env_violations.append((task_id, reward, "NOT_FLOAT"))
        
        status = "✅" if (0 < reward < 1) else "❌"
        print(f"  {status} Task {task_id}: {reward:.4f}")
        
    except Exception as e:
        env_violations.append((task_id, None, str(e)))
        print(f"  ❌ Task {task_id}: ERROR - {e}")

if env_violations:
    print(f"\n🚨 FAILED: {len(env_violations)} environment steps have issues!")
    sys.exit(1)

print("✅ PASSED: All 30 environment steps produce safe rewards")

# TEST 5: Verify inference.py has required components
print("\n[TEST 5] Checking inference.py requirements...")
with open("inference.py", "r") as f:
    inference_content = f.read()

inference_checks = {
    "Imports OpenAI": "from openai import OpenAI" in inference_content or "import openai" in inference_content,
    "Uses os.environ": 'os.environ["API_BASE_URL"]' in inference_content,
    "Has clamp_score": "def clamp_score" in inference_content,
    "Has [START]": '[START]' in inference_content,
    "Has [STEP]": '[STEP]' in inference_content,
    "Has [END]": '[END]' in inference_content,
}

for check_name, result in inference_checks.items():
    status = "✅" if result else "❌"
    print(f"  {status} {check_name}")
    if not result:
        print(f"\n🚨 FAILED: inference.py missing {check_name}")
        sys.exit(1)

print("✅ PASSED: inference.py has all required components")

# TEST 6: Verify requirements.txt has dependencies
print("\n[TEST 6] Checking requirements.txt...")
with open("requirements.txt", "r") as f:
    requirements = f.read().lower()

required_packages = ["fastapi", "pydantic", "openai", "pyyaml"]
missing_packages = []

for pkg in required_packages:
    if pkg not in requirements:
        missing_packages.append(pkg)
        print(f"  ❌ {pkg}")
    else:
        print(f"  ✅ {pkg}")

if missing_packages:
    print(f"\n🚨 FAILED: requirements.txt missing {missing_packages}")
    sys.exit(1)

print("✅ PASSED: requirements.txt has all dependencies")

# FINAL SUMMARY
print("\n" + "=" * 80)
print("ALL TESTS PASSED ✅✅✅")
print("=" * 80)
print("""
SUMMARY OF VERIFICATION:
✅ All 6 required files present
✅ openenv.yaml configured correctly (30 tasks, [0.001, 0.999] range)
✅ All 30 graders produce safe scores (0 < score < 1)
✅ All 30 environment steps produce safe rewards
✅ inference.py has all required components
✅ requirements.txt has all dependencies

SUBMISSION STATUS: READY FOR RESUBMISSION #70 ✅
""")
print("=" * 80)
