"""Quick live endpoint verification for Lunar v3.2"""
import requests

BASE = "https://mehajabeen-lunar.hf.space"

print("=== Lunar v3.2 Live Verification ===")

# Health
r = requests.get(f"{BASE}/health", timeout=20)
print("Health:", r.json().get("status"), "v" + r.json().get("version", "?"))

# Confirm unique task posts
print("\nVerifying unique task posts (v3.2 — no random sampling):")
for tid, expected_fragment in [
    (1, "EARN $5000"),
    (3, "ethnic slur"),
    (7, "Silicon Valley"),
    (12, "District 7"),
    (15, "MENA"),
    (23, "journalist_sarah"),
    (29, "GreatReplacement"),
    (30, "Hospital"),
]:
    r = requests.post(f"{BASE}/reset", json={"task_id": tid}, timeout=15)
    obs = r.json().get("observation", {})
    post_text = obs.get("post", {}).get("text", "")
    found = expected_fragment.lower() in post_text.lower()
    print("  Task %2d: %s  (unique post: %s)" % (tid, "OK" if found else "MISS", post_text[:60]))

# Leaderboard
print("\nLeaderboard endpoint:")
for tid in [1, 15, 30]:
    r = requests.post(f"{BASE}/reset", json={"task_id": tid}, timeout=15)
    sid = r.json()["session_id"]
    action = {"category": "spam", "severity": 2, "action": "remove",
              "reasoning": "coordinated spam with urgency tactics and policy violation"}
    for _ in range(5):
        r2 = requests.post(f"{BASE}/step", json={"session_id": sid, "action": action}, timeout=15)
        if r2.json().get("done"):
            break

r = requests.get(f"{BASE}/leaderboard?limit=5", timeout=15)
lb = r.json()
print("  Total sessions recorded:", lb.get("total_sessions"))
print("  Top entries:", len(lb.get("leaderboard", [])))
for e in lb.get("leaderboard", []):
    print("    task=%s  domain=%s  best_reward=%.4f" % (
        e.get("task_id"), e.get("domain"), e.get("best_reward", 0)))

# Domain-filtered leaderboard
r = requests.get(f"{BASE}/leaderboard?domain=threat_assessment", timeout=15)
print("  threat_assessment filter:", r.json().get("total_sessions"), "sessions")

print("\n=== v3.2 Live OK ===")
