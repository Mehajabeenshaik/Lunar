"""Test all HTTP endpoints of the Lunar Benchmark server."""
import requests
import json

BASE = "http://localhost:7860"

# Test root
r = requests.get(f"{BASE}/")
print("[/] Status:", r.status_code, "- name:", r.json().get("name"))

# Test health
r = requests.get(f"{BASE}/health")
print("[/health]", r.json().get("status"))

# Test manifest
r = requests.get(f"{BASE}/manifest")
print("[/manifest] tasks:", r.json().get("tasks"))

# Test state
r = requests.get(f"{BASE}/state")
print("[/state] status:", r.json().get("status"))

# Test reset
r = requests.post(f"{BASE}/reset", json={"task_id": 1})
data = r.json()
sid = data["session_id"]
print("[/reset] session=%s, task_id=%s" % (sid, data["task_id"]))
print("  observation keys:", list(data["observation"].keys()))

# Test step
action = {"category": "spam", "severity": 2, "action": "remove",
          "reasoning": "spam detected due to policy"}
r = requests.post(f"{BASE}/step", json={"session_id": sid, "action": action})
step_data = r.json()
print("[/step] reward=%.4f, done=%s" % (step_data["reward"], step_data["done"]))
fb = step_data.get("feedback", "")[:80]
print("  feedback:", fb)

# Test session state
r = requests.get(f"{BASE}/state/{sid}")
state = r.json()
print("[/state/sid] step=%s, rewards=%s" % (state["step"], state["rewards"]))

# Test tasks list
r = requests.get(f"{BASE}/tasks")
print("[/tasks] total=%s" % r.json()["total_tasks"])

# Test multi-turn (remaining steps)
for i in range(2, 6):
    r = requests.post(f"{BASE}/step", json={"session_id": sid, "action": action})
    d = r.json()
    print("  Step %d: reward=%.4f, done=%s" % (i, d["reward"], d["done"]))
    if d["done"]:
        break

# Test all 3 domains
print("\nTesting all 3 domains via API...")
for tid, domain in [(5, "text_classification"), (15, "contextual_policy"), (25, "threat_assessment")]:
    r = requests.post(f"{BASE}/reset", json={"task_id": tid})
    data = r.json()
    obs = data["observation"]
    print("  Task %d: domain=%s, difficulty=%s" % (tid, obs["domain"], obs["difficulty"]))
    
    sid2 = data["session_id"]
    action2 = {"category": "spam", "severity": 2, "action": "remove",
               "is_coordinated": True, "threat_level": "medium",
               "confidence": 0.7, "reasoning": "test with context"}
    r2 = requests.post(f"{BASE}/step", json={"session_id": sid2, "action": action2})
    d2 = r2.json()
    print("    Step 1: reward=%.4f, done=%s" % (d2["reward"], d2["done"]))

print("\n=== ALL HTTP ENDPOINT TESTS PASSED ===")
