---
title: LUNAR - Multi-Domain RL Benchmark
colorFrom: blue
colorTo: purple
sdk: docker
pinned: true
---

# LUNAR:  Multi-Domain RL Benchmark

**A comprehensive, production-ready reinforcement learning environment for real-world optimization challenges.**


---

##  Quick Start

### Live Demo
Try the API immediately - no installation required:
- **API Endpoint:** [mehajabeen-lunar.hf.space](https://mehajabeen-lunar.hf.space)
- **Interactive Docs:** [mehajabeen-lunar.hf.space/docs](https://mehajabeen-lunar.hf.space/docs)
- **GitHub:** [github.com/Mehajabeenshaik/Lunar](https://github.com/Mehajabeenshaik/Lunar)

### Local Deployment

```bash
# Clone repository
git clone https://github.com/Mehajabeenshaik/Lunar.git
cd Lunar

# Docker deployment (recommended)
docker build -t lunar:latest .
docker run -p 7860:7860 lunar:latest

# API available at http://localhost:7860
```

---

## Benchmark Overview

| Metric | Value | Status |
|--------|-------|--------|
| **Domains** | 5 | Production Ready |
| **API Endpoints** | 9+ | Full OpenEnv v1 |
| **Score Validation** | (0, 1) Strict | 4-Level Pipeline |
| **Grading System** | Deterministic | Multi-objective |

### Task Distribution 

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

