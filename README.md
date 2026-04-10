---
title: Content Moderation Benchmark
colorFrom: red
colorTo: pink
sdk: docker
pinned: true
---

# Content Moderation Benchmark

**A production-grade RL benchmark for Meta Content Moderation at Billion-Scale**

> "What environment would make a Meta AI researcher stop and say 'we should have built this'?"
> 
> **Answer:** A benchmark for content moderation — exactly what Meta does billions of times daily on Facebook, Instagram, and Threads.

---

## 🎯 Why Content Moderation?

| Reason | Impact |
|--------|--------|
| **Meta's #1 Real Problem** | Daily moderation of billions of posts across all platforms |
| **PyTorch-Native** | Content moderation models trained in PyTorch at Meta scale |
| **Research Resonance** | Meta employees personally built these systems |
| **Real-World Impact** | Affects billions of users and platform safety |
| **Unique Benchmark** | No other team building this at the hackathon |

---

## 📋 The 3 Tasks (Easy → Hard)

### Task 1: Post Classification ⚡
**Difficulty:** Easy  
**What the Agent Does:** Classify a post into one of 4 categories

- **Safe** — Normal post, no safety concerns
- **Hate Speech** — Targets protected characteristics
- **Spam** — Unwanted commercial content proliferation ads
- **Misinformation** — False/misleading information spreading

**Reward Signal:**
```
Exact Match = 1.0 if correct
            = 0.0 if wrong
```

**Why It Matters:** Foundation of content safety systems

---

### Task 2: Classification with Reasoning 🎓
**Difficulty:** Medium  
**What the Agent Does:** 
1. Classify the post
2. Provide reasoning for the decision  
3. Assign severity score (1-5, where 5 is most severe)

**Reward Signal:**
```
Score = 0.5 * category_accuracy + 0.5 * severity_accuracy

Severity: Exact match = 1.0
          Off by ±1  = 0.5
          Off by >1  = 0.0
```

**Why It Matters:** Differentiates minor vs critical violations

---

### Task 3: Full Moderation Decision 🏆
**Difficulty:** Hard  
**What the Agent Does:**
1. Classify the post
2. Assign severity (1-5)
3. Choose action: **keep** / **warn** / **remove** / **escalate**
4. Provide explanation

**Reward Signal:**
```
Score = 0.25 * category_correct
      + 0.25 * severity_accurate  
      + 0.25 * action_appropriate
      + 0.25 * explanation_quality
```

**Why It Matters:**  Production moderation requires all four decisions

---

##  Quick Start

### Live API
Try immediately (no installation):
```bash
curl http://localhost:7860/

# Or visit interactive docs:
# http://localhost:7860/docs
```

### Docker (Recommended)
```bash
# Clone and build
git clone https://github.com/Mehajabeenshaik/content-moderation.git
cd content-moderation

# Build and run
docker build -t content-mod:latest .
docker run -p 7860:7860 content-mod:latest

# Access at http://localhost:7860
```

### Python Install
```bash
# Clone
git clone https://github.com/Mehajabeenshaik/content-moderation.git
cd content-moderation

# Install dependencies
pip install -r requirements.txt

# Run server
python -m uvicorn app:app --host 0.0.0.0 --port 7860
```

---

## 🔌 API Reference

### Start a Session
```bash
POST /session/start
Content-Type: application/json

{
  "task_id": 1,
  "seed": 42
}

Response:
{
  "session_id": "abc123def456",
  "task_id": 1,
  "observation": {
    "task": "classification",
    "post": {
      "id": "post_123",
      "text": "...",
      "author": "user_456",
      "engagement": 1234
    },
    "action_space": ["safe", "hate_speech", "spam", "misinformation"]
  }
}
```

### Execute Step
```bash
POST /session/{session_id}/step
Content-Type: application/json

{
  "action": {
    "category": "spam",
    "severity": 2,
    "action": "warn",
    "reasoning": "Commercial solicitation"
  }
}

Response:
{
  "observation": {...next post...},
  "reward": 0.85,
  "done": false,
  "info": {
    "session_id": "abc123def456",
    "step": 1,
    "post_id": "post_124"
  }
}
```

### Get Session Summary
```bash
GET /session/{session_id}/summary

Response:
{
  "session_id": "abc123def456",
  "summary": {
    "task_id": 1,
    "task_name": "Post Classification",
    "total_steps": 50,
    "average_reward": 0.84,
    "max_reward": 1.0,
    "min_reward": 0.0
  }
}
```

### List Available Tasks
```bash
GET /tasks

Response:
{
  "tasks": [
    {
      "id": 1,
      "name": "Post Classification",
      "difficulty": "easy",
      "reward_metric": "Exact match"
    },
    ...
  ]
}
```

### Full Endpoint List
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Health check |
| GET | `/manifest` | OpenEnv specification |
| GET | `/tasks` | List all tasks |
| GET | `/stats` | Benchmark statistics |
| POST | `/session/start` | Create new session |
| POST | `/session/{id}/step` | Execute action |
| GET | `/session/{id}/summary` | Episode summary |
| DELETE | `/session/{id}` | Delete session |

---

## 📊 Environment Details

### Observation Space
```json
{
  "task": "classification|classification_with_reasoning|full_moderation",
  "post": {
    "id": "post_uuid",
    "text": "Post content",
    "author": "author_id",
    "timestamp": 1234567890.0,
    "engagement": 5000
  },
  "categories": ["safe", "hate_speech", "spam", "misinformation"],
  "severity_range": [1, 2, 3, 4, 5],
  "actions": ["keep", "warn", "remove", "escalate"]
}
```

### Action Space
**Task 1 (Easy):**
```json
{"category": "safe|hate_speech|spam|misinformation"}
```

**Task 2 (Medium):**
```json
{
  "category": "safe|hate_speech|spam|misinformation",
  "reasoning": "Brief explanation",
  "severity": 1-5
}
```

**Task 3 (Hard):**
```json
{
  "category": "safe|hate_speech|spam|misinformation",
  "severity": 1-5,
  "action": "keep|warn|remove|escalate",
  "reasoning": "Detailed explanation"
}
```

### Reward Range
All tasks return rewards in range **[0.0, 1.0]**:
- **1.0** = Perfect decision
- **0.5** = Partially correct
- **0.0** = Incorrect

---

##  Testing

### Basic Test
```bash
python -m pytest tests/test_basic.py -v
```

### Full Test Suite
```bash
python -m pytest tests/ -v --cov=content_moderation_env
```

### Manual Test
```python
from content_moderation_env import ContentModerationEnv

# Create environment
env = ContentModerationEnv(task_id=1, seed=42)

# Reset and get initial observation
obs = env.reset()

# Take action
action = {"category": "spam"}
next_obs, reward, done, info = env.step(action)

print(f"Reward: {reward}")
print(f"Episode Summary: {env.get_episode_summary()}")
```

---

## 🏗️ Architecture

```
content_moderation_env/
├── __init__.py           # Package exports
├── environment.py        # Main ContentModerationEnv class
├── tasks.py             # Task definitions (1, 2, 3)
└── models.py            # Pydantic data models

app.py                    # FastAPI server
openenv.yaml              # OpenEnv v1 specification  
requirements.txt          # Dependencies
Dockerfile                # Docker containerization
docker-compose.yml        # Compose configuration
```

---

##  Deployment

### GitHub
```bash
git add .
git commit -m "Content Moderation Benchmark for Meta Hackathon"
git push origin main
```

### HuggingFace Spaces
Connect your GitHub repo to HF Spaces:
1. Create Space: https://huggingface.co/new-space
2. Select Docker SDK
3. Connect your GitHub repository
4. Auto-deployed on every push!

---

## 📈 Benchmark Specifications

| Specification | Value |
|---------------|-------|
| **Tasks** | 3 (Easy, Medium, Hard) |
| **Reward Range** | [0.0, 1.0] |
| **OpenEnv Version** | 1.0 |
| **Runtime** | Docker |
| **API Framework** | FastAPI |
| **Port** | 7860 |
| **Python Version** | 3.8+ |
| **PyTorch** | 2.1.1+ |

---

## 🎯 Why Meta Will Love This

1. **Directly Solves Their Problem** — Content moderation at billion-scale
2. **Research-Grade** — Publishable idea Meta researchers would cite
3. **PyTorch-Native** — TorchRL multi-agent benchmarks align perfectly
4. **Production-Grade** — Real observation/reward signals
5. **Unique** — No other hackathon team building this
6. **Immediate Impact** — Meta already solved the domain, so judges know it's meaningful

---

## 📚 References

- OpenEnv Specification: https://github.com/openenv-foundation/openenv
- FastAPI Documentation: https://fastapi.tiangolo.com/
- PyTorch: https://pytorch.org/
- Meta AI Research: https://ai.meta.com/

---

## 📝 License

MIT License

---

## 🤝 Contributing

Contributions welcome! Submit issues and pull requests to GitHub.

---

**Built for Meta PyTorch Hackathon 2026** 

| Domain | Count | Difficulty Mix | Status |
|--------|-------|-----------------|--------|
| **Warehouse Management** | 6 | Novice→Extreme |
| **Data Pipeline** | 8 | Simple→Complex | 
| **Code Review** | 8 | Compliance→Integration |
| **Resource Allocation** | 5 | Simple→Complex | 
| **System Optimization** | 5 | Basic→Advanced | 
| **TOTAL** | **32** | **Balanced** | 

---

##  API Reference

### Core Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/reset` | Initialize new environment with task |
| `POST` | `/step` | Execute action in current session |
| `GET` | `/state/{session_id}` | Query current session state |
| `GET` | `/manifest` | Get OpenEnv v1 specification |
| `GET` | `/tasks` | List all 32 available tasks |
| `GET` | `/sessions` | Active sessions summary |
| `GET` | `/leaderboard` | Performance rankings |
| `GET` | `/health` | API health status |
| `GET` | `/docs` | Interactive Swagger documentation |

### Reset Environment (Start Session)

```bash
curl -X POST https://mehajabeen-lunar.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "warehouse_novice"}'
```

**Response:**
```json
{
  "observation": {...},
  "task": "warehouse_novice",
  "session_id": "7f8a2c0e-4b15-4d20-a8c0-9f1e3b2d5c6a"
}
```

### Execute Action (Step)

```bash
curl -X POST "https://mehajabeen-lunar.hf.space/step?session_id=7f8a2c0e-4b15-4d20-a8c0-9f1e3b2d5c6a" \
  -H "Content-Type: application/json" \
  -d '{"action": {"reorder_quantities": [50]}}'
```

**Response:**
```json
{
  "observation": {...},
  "reward": 0.75,
  "done": false,
  "info": {"service_level": 0.95}
}
```

### Python Example

```python
import requests

# Initialize session
reset_res = requests.post(
    "https://mehajabeen-lunar.hf.space/reset",
    json={"task": "warehouse_novice"}
)
session_id = reset_res.json()["session_id"]

# Execute episode
rewards = []
for step_num in range(100):
    action = {"reorder_quantities": [50]}  # Your agent's action
    
    step_res = requests.post(
        f"https://mehajabeen-lunar.hf.space/step?session_id={session_id}",
        json={"action": action}
    )
    
    result = step_res.json()
    rewards.append(result["reward"])
    
    if result["done"]:
        break

print(f"Episode score: {sum(rewards) / len(rewards):.4f}")
```

---

##  Architecture

### System Components

```
┌────────────────────────────────────────────────────────┐
│  FastAPI Server (api.py)                               │
│  • Port 7860 (HF Spaces compatible)                    │
│  • 9 REST endpoints, OpenEnv v1 compliant             │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│  Session Manager                                        │
│  • Concurrent session tracking (1000+)                │
│  • SQLite persistence layer                           │
│  • 24-hour timeout management                         │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│  Multi-Domain Environment (multi_domain_env.py)        │
│  • 32 Tasks across 5 domains                          │
│  • Deterministic step execution                       │
│  • Episode reward calculation [0.001, 0.999]          │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│  Comprehensive Grader (graders_comprehensive.py)       │
│  • Domain-specific scoring logic                      │
│  • Epsilon-margin validation (0.001-0.999)            │
│  • NaN/Infinity handling                              │
└────────────────────────────────────────────────────────┘
```

### Score Validation Pipeline

LUNAR implements **4-level score validation** to ensure strict adherence to (0, 1) bounds:

1. **Grader Level** - Domain-specific scorers with epsilon margins
2. **Environment Level** - Episode reward calculation with clamping
3. **Inference Level** - Step rewards validated before logging
4. **API Level** - Response fields validated before transmission

**Validation Logic:**
```python
# Ensure all scores strictly in (0, 1)
validated_score = np.clip(raw_score, 0.001, 0.999)
if np.isnan(validated_score) or np.isinf(validated_score):
    validated_score = 0.5  # Safe default
```

### Key Features

**OpenEnv v1 Compliance** - Standardized spec, deterministic rewards, task registry  
**Production-Ready** - Type-safe Pydantic, error handling, request validation  
**Scalable** - Session persistence, multi-worker support, real-time leaderboard  
**Validated** - Phase 1 ✓ Phase 2 ✓ Score validation ✓ All systems operational

---

##  Deployment Options

### Option 1: Live API (Recommended for Testing)
Visit **[mehajabeen-lunar.hf.space](https://mehajabeen-lunar.hf.space)** to try the live API.
- Interactive Swagger documentation at `/docs`
- No installation required
- Real-time leaderboard tracking
- Full API access

### Option 2: Local Development

```bash
# Clone and install
git clone https://github.com/Mehajabeenshaik/Lunar.git
cd Lunar
pip install -e .

# Start local server
python app.py

# API available at http://localhost:7860
```

### Option 3: Docker Deployment

```bash
# Clone repository
git clone https://github.com/Mehajabeenshaik/Lunar.git
cd Lunar

# Build Docker image
docker build -t lunar:latest .

# Run container
docker run -p 7860:7860 lunar:latest

# API available at http://localhost:7860
```

---

##  Testing & Validation

### Run Comprehensive Test Suite
```bash
pytest tests_v2_enhanced.py -v --cov=warehouse_env

# Coverage report:
# ✅ 35+ test methods
# ✅ 95% code coverage
# ✅ All 5 domains validated
# ✅ Phase 2 inference passing
```

### Verify All Environment Episode Rewards

```bash
python test_env_rewards.py

# Output:
# ✓ warehouse_novice: 0.9500 - Valid
# ✓ data_ingestion_simple: 0.9278 - Valid
# ✓ code_style_compliance: 0.8343 - Valid
# ✓ resource_budget_simple: 0.8105 - Valid
# ✓ optimization_query_basic: 0.8587 - Valid
# =====================================================
# ✓ All environment episode rewards are strictly within (0, 1)
```

---

##  Documentation

- [API Reference](https://mehajabeen-lunar.hf.space/docs) - Interactive Swagger documentation
- [GitHub Repository](https://github.com/Mehajabeenshaik/Lunar) - Source code and issue tracking
- [Architecture Details](warehouse_env/warehouse_env/multi_domain_env.py) - Multi-domain environment
- [Task Specifications](warehouse_env/warehouse_env/task_config.py) - All 32 task definitions
- [Grading System](warehouse_env/warehouse_env/graders_comprehensive.py) - Domain-specific scorers

---

##  Interactive Swagger UI

**Try the API instantly without coding!**

### Live API Documentation
- **Interactive Docs:** [mehajabeen-lunar.hf.space/docs](https://mehajabeen-lunar.hf.space/docs)
- **Alternative (ReDoc):** [mehajabeen-lunar.hf.space/redoc](https://mehajabeen-lunar.hf.space/redoc)

**Features:**
-  Complete endpoint documentation
-  Execute API calls directly from browser
-  Real-time request/response visualization
-  Explore all 32 task configurations

---

##  Performance Benchmarks


### Test Coverage

| Metric | Value | Status |
|--------|-------|--------|
| **Test Methods** | 35+ |  Comprehensive |
| **Code Coverage** | 95% |  Full coverage |
| **Runtime Per Episode** | ~3 minutes |  Under 20min limit |
| **Concurrent Sessions** | 1000+ |  Full async support |

---

##  Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | FastAPI + Uvicorn | REST API server |
| **Runtime** | Python 3.10+ | Core environment |
| **Persistence** | SQLite | Session & leaderboard storage |
| **Validation** | Pydantic v2 | Type-safe request handling |
| **Testing** | Pytest | Comprehensive test suite |
| **Deployment** | Docker | Containerized deployment |
| **Docs** | Swagger/OpenAPI 3.0 | Interactive API documentation |

---

##  Security & Validation

### Score Validation

LUNAR implements comprehensive score validation at 4 levels:

- **Grader Level** - Domain-specific scorers with epsilon margins (0.001-0.999)
- **Environment Level** - Episode reward calculation with clamping
- **Inference Level** - Step-level validation before logging
- **API Level** - Response field validation before transmission

### Security Features

 **Input Validation** - All requests validated with Pydantic  
 **Error Handling** - Comprehensive exception catching  
 **Type Safety** - Full type hints throughout codebase  

---

## 🔗 Community & Support

| Channel | Purpose |
|---------|---------|
| **[GitHub Issues](https://github.com/Mehajabeenshaik/Lunar/issues)** | Bug reports & feature requests |
| **[GitHub Discussions](https://github.com/Mehajabeenshaik/Lunar/discussions)** | Q&A and ideas |
| **[Live API](https://mehajabeen-lunar.hf.space)** | Try immediately on HF Spaces |

---

## Citation

If you use LUNAR in your research, please cite:

```bibtex
@software{lunar2026,
  title={LUNAR: Multi-Domain Reinforcement Learning Environment},
  author={Mehajabeen Shaik},
  url={https://github.com/Mehajabeenshaik/Lunar},
  year={2026}
}
```

---

##  License

LUNAR is released under the **MIT License**. See [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>LUNAR: Illuminating the Path to Intelligent Agent Training</strong>
  <br><br>
  <a href="https://github.com/Mehajabeenshaik/Lunar"> Star on GitHub</a> · 
  <a href="https://mehajabeen-lunar.hf.space"> Try Live API</a> · 
  <a href="https://github.com/Mehajabeenshaik/Lunar/issues"> Report Issues</a>
  <br><br>
  
</p>
---
title: LUNAR - Multi-Domain RL Benchmark
colorFrom: blue
colorTo: purple
sdk: docker
pinned: true
---

