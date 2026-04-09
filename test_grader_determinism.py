#!/usr/bin/env python
"""Test grader determinism - same episode should produce same rewards."""

import requests

print("="*70)
print("TESTING GRADER DETERMINISM VIA API")
print("="*70)

tasks = ["warehouse_easy", "warehouse_medium", "warehouse_hard"]
results = {}

for task in tasks:
    print(f"\n{task}:")
    
    # First run
    run_1_rewards = []
    r = requests.post("http://localhost:7860/reset", json={"task": task})
    session_id_1 = r.json()["session_id"]
    obs = r.json()["observation"]
    
    for step in range(3):
        r = requests.post(
            "http://localhost:7860/step",
            json={"session_id": session_id_1, "action": {"reorder_quantities": [50.0, 50.0, 50.0]}}
        )
        reward = r.json().get("reward", 0.0)
        run_1_rewards.append(reward)
    
    # Second run - same action sequence
    run_2_rewards = []
    r = requests.post("http://localhost:7860/reset", json={"task": task})
    session_id_2 = r.json()["session_id"]
    obs = r.json()["observation"]
    
    for step in range(3):
        r = requests.post(
            "http://localhost:7860/step",
            json={"session_id": session_id_2, "action": {"reorder_quantities": [50.0, 50.0, 50.0]}}
        )
        reward = r.json().get("reward", 0.0)
        run_2_rewards.append(reward)
    
    # Compare
    match = run_1_rewards == run_2_rewards
    status = "✅" if match else "❌"
    print(f"  {status} Run 1: {[f'{r:.4f}' for r in run_1_rewards]}")
    print(f"  {status} Run 2: {[f'{r:.4f}' for r in run_2_rewards]}")
    results[task] = match

print("\n" + "="*70)
print("DETERMINISM CHECK RESULTS:")
for task, is_deterministic in results.items():
    status = "✅ DETERMINISTIC" if is_deterministic else "❌ NON-DETERMINISTIC"
    print(f"  {task}: {status}")

all_deterministic = all(results.values())
print("\n" + ("✅ ALL TASKS PRODUCE DETERMINISTIC REWARDS" if all_deterministic else "❌ SOME TASKS ARE NON-DETERMINISTIC"))
print("="*70)
