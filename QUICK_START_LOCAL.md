# LUNAR - Quick Local Deployment Guide

If you want to run LUNAR immediately while HF Spaces completes its rebuild, follow these steps.

## Prerequisites

- Python 3.10+
- pip or conda

## Installation (1 minute)

```bash
cd lunar
pip install -r requirements.txt
```

## Running the Server (Local)

```bash
# Start the server
python run_server.py

# Output:
# INFO:     Uvicorn running on http://0.0.0.0:7860
# INFO:     Application startup complete
```

Server will be available at: **http://localhost:7860**

## Testing All Endpoints

### 1. Health Check
```bash
curl http://localhost:7860/health
# {"status": "ok", "version": "3.0.0", ...}
```

### 2. List All 21 Tasks
```bash
curl http://localhost:7860/tasks | jq
# Shows all task variants with configurations
```

### 3. Check Server Stats
```bash
curl http://localhost:7860/stats | jq
# Shows active sessions, memory usage, etc
```

### 4. View OpenEnv Manifest
```bash
curl http://localhost:7860/manifest | jq
# OpenEnv specification for this environment
```

### 5. Create a Session (warehouse_easy)
```bash
SESSION=$(curl -s -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "warehouse_easy"}' | jq -r '.session_id')

echo "Created session: $SESSION"
```

### 6. Get Initial State
```bash
curl "http://localhost:7860/state?session_id=$SESSION" | jq
```

### 7. Take an Action
```bash
curl -X POST "http://localhost:7860/step?session_id=$SESSION" \
  -H "Content-Type: application/json" \
  -d '{"warehouse_id": 0, "quantity": 50}' | jq
```

### 8. Check Leaderboard
```bash
curl "http://localhost:7860/leaderboard?limit=5" | jq
```

### 9. View Interactive API Docs
```bash
# Open in browser:
open http://localhost:7860/docs
# or
start http://localhost:7860/docs
```

## Python Client Example

```python
import requests
import json

BASE = "http://localhost:7860"

# Create session
session = requests.post(
    f"{BASE}/reset",
    json={"task": "warehouse_medium"}
).json()
session_id = session["session_id"]
print(f"Created session: {session_id}")

# Step 10 times
for i in range(10):
    response = requests.post(
        f"{BASE}/step",
        params={"session_id": session_id},
        json={"warehouse_id": 0, "quantity": 50}
    ).json()
    print(f"Step {i}:  Reward={response['reward']:.2f}, Done={response['done']}")
    
    if response["done"]:
        print("Episode complete!")
        break

# Check leaderboard
leaderboard = requests.get(f"{BASE}/leaderboard?limit=10").json()
print(f"\nTop session reward: {leaderboard['leaderboard'][0]['best_reward'] if leaderboard['leaderboard'] else 'N/A'}")
```

## Test Different Tasks

### Easy Tasks (Beginner)
```bash
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "warehouse_easy"}'
```

### Medium Tasks (Intermediate)
```bash
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "warehouse_medium"}'
```

### Hard Tasks (Advanced)
```bash
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "warehouse_hard"}'
```

### Supply Chain Tasks
```bash
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "supply_chain_optimization"}'
```

### Demand Forecasting Tasks
```bash
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "forecast_chaotic"}'
```

## Running Tests

```bash
# Test API endpoints locally
python test_api_endpoints.py

# Test environment logic
python test_quick.py

# Full deployment test
python test_full_deployment.py
```

## Access API Documentation

Once the server is running, open your browser to:
- **Swagger UI**: http://localhost:7860/docs
- **ReDoc**: http://localhost:7860/redoc

Both provide interactive API documentation and allow testing endpoints directly from the browser.

## Multi-Session Example

```python
import requests
import json

BASE = "http://localhost:7860"

# Run multiple tasks in parallel
tasks = ["warehouse_easy", "warehouse_medium", "warehouse_hard", "supply_chain_basic"]
sessions = {}

# Create sessions for each task
for task in tasks:
    r = requests.post(f"{BASE}/reset", json={"task": task}).json()
    sessions[task] = r["session_id"]
    print(f"✅ {task}: {r['session_id'][:8]}...")

# Step all sessions
for i in range(5):
    print(f"\n--- Step {i+1} ---")
    for task, sid in sessions.items():
        r = requests.post(
            f"{BASE}/step",
            params={"session_id": sid},
            json={"warehouse_id": 0, "quantity": 50}
        ).json()
        print(f"{task}: reward={r['reward']:.2f}")

# View leaderboard
lb = requests.get(f"{BASE}/leaderboard?limit=10").json()
print(f"\n✅ Leaderboard: {len(lb['leaderboard'])} sessions tracked")
```

## Performance Monitoring

```bash
# Watch stats in real-time (macOS/Linux)
watch -n 1 'curl -s http://localhost:7860/stats | jq'

# Or manually check every 5 seconds
while true; do
    curl -s http://localhost:7860/stats | jq .
    sleep 5
done
```

## Troubleshooting

### Port 7860 Already in Use
```bash
# Use different port
PORT=8000 python run_server.py
# Access at http://localhost:8000
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Session Not Found
Make sure to use the exact session_id returned from /reset:
```bash
# Correct format
curl "http://localhost:7860/state?session_id=abc-123-def"

# Wrong - missing session_id
curl "http://localhost:7860/state"  # ❌ Returns 400 error
```

## Next Steps

Once HF Spaces rebuilds, everything will work the same way but at:
```
https://mehajabeen-lunar.hf.space
```

Just replace `http://localhost:7860` with the HF Spaces URL in any of the examples above.

## Production Deployment

You can also deploy locally with production settings:
```bash
# Run production-grade server
uvicorn warehouse_env.server:app --host 0.0.0.0 --port 7860
```

---

**Note**: All features work identically on both local deployment and HF Spaces. Once HF Spaces comes online, you'll have public access to the LUNAR environment.
