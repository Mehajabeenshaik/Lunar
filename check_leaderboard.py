#!/usr/bin/env python3
"""Check leaderboard values."""

import requests

r = requests.get('http://localhost:7860/leaderboard?limit=10')
data = r.json()
print('All leaderboard entries:')
for entry in data['leaderboard']:
    print(f"  {entry['session_id'][:8]}: best_reward={entry.get('best_reward')}, reward={entry.get('reward')}")
