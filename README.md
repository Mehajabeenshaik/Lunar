---
title: Lunar Content Moderation Benchmark
emoji: 🌙
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: "Multi-turn RL benchmark for content moderation."
---

# 🌙 Lunar — Content Moderation Benchmark

> **Train agents to moderate content like Meta engineers — with context, nuance, and accountability.**

A multi-turn RL environment for benchmarking AI agents on real-world content moderation. 30 tasks across 3 domains, with progressive context reveal, rich partial-credit reward shaping, and domain-specific graders.

[![OpenEnv v1](https://img.shields.io/badge/OpenEnv-v1-blue)](https://openenv.dev)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-purple)](https://pydantic.dev)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue)](https://docker.com)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Lunar Benchmark v3.0                       │
├─────────────┬──────────────────┬────────────────────────────┤
│  Domain 1   │    Domain 2      │        Domain 3            │
│  Text       │    Contextual    │        Threat              │
│  Classification │  Policy      │        Assessment          │
│  (Tasks 1-10)│  (Tasks 11-20) │        (Tasks 21-30)       │
├─────────────┼──────────────────┼────────────────────────────┤
│ Category +  │ Policy compliance│ Detection + severity       │
│ Severity +  │ + context usage  │ + response plan            │
│ Reasoning   │ + edge cases     │ + confidence calibration   │
├─────────────┴──────────────────┴────────────────────────────┤
│         Multi-Turn Episodes (5 steps, weighted scoring)      │
│         Progressive Context Reveal + Grader Feedback         │
├──────────────────────────────────────────────────────────────┤
│         Pydantic v2 Typed Models (OpenEnv Spec)              │
│         FastAPI + Uvicorn (port 7860)                        │
└──────────────────────────────────────────────────────────────┘
```

---

## Key Features

| Feature | Details |
|---------|---------|
| **3 Distinct Domains** | Text Classification, Contextual Policy, Threat Assessment |
| **30 Tasks** | 10 per domain, easy → medium → hard difficulty gradient |
| **Multi-Turn Episodes** | 5-step episodes with grader feedback after each step |
| **Progressive Context** | More context revealed each step (author history, policies, threat signals) |
| **Rich Partial Credit** | 7 tiers of reward shaping per domain (not binary pass/fail) |
| **Weighted Scoring** | Later steps worth more (agent should improve from feedback) |
| **Typed Models** | Pydantic v2 Observation/Action/Reward models |
| **OpenEnv v1 Spec** | Full `reset()` / `step()` / `state()` compliance |
| **Deterministic Graders** | 3 domain-specific graders with distinct evaluation mechanics |

---

## Domains & Difficulty Gradient

### Domain 1: Text Classification (Tasks 1-10)
Classify social media posts by category, severity, and reasoning quality.

| Task | Name | Difficulty |
|------|------|-----------|
| 1 | Basic Post Classification | Easy |
| 2 | Spam Detection with Severity | Easy |
| 3 | Hate Speech Classification | Easy |
| 4 | Misinformation Flagging | Medium |
| 5 | Multi-label Classification | Medium |
| 6 | Severity Calibration | Medium |
| 7 | Nuanced Classification | Hard |
| 8 | Context-Dependent Classification | Hard |
| 9 | Sarcasm-Aware Classification | Hard |
| 10 | Full Classification Pipeline | Hard |

### Domain 2: Contextual Policy Enforcement (Tasks 11-20)
Moderate content considering author history, cultural context, and policy exceptions.

| Task | Name | Difficulty |
|------|------|-----------|
| 11 | Author History Review | Easy |
| 12 | New Account Screening | Easy |
| 13 | Trending Topic Exceptions | Easy |
| 14 | Policy Update Application | Medium |
| 15 | Cross-Cultural Moderation | Medium |
| 16 | Language-Aware Policy | Medium |
| 17 | Appeal Case Review | Hard |
| 18 | Trust Score Assessment | Hard |
| 19 | False Positive Recovery | Hard |
| 20 | Evolving Policy Compliance | Hard |

### Domain 3: Threat Assessment & Response (Tasks 21-30)
Detect coordinated attacks, misinformation cascades, and harassment networks.

| Task | Name | Difficulty |
|------|------|-----------|
| 21 | Bot Network Detection | Easy |
| 22 | Spam Campaign Detection | Easy |
| 23 | Harassment Network Mapping | Medium |
| 24 | Misinformation Cascade | Medium |
| 25 | Coordinated Inauthentic Behavior | Medium |
| 26 | Viral Threat Assessment | Hard |
| 27 | Cross-Platform Threat | Hard |
| 28 | Deepfake & Manipulation | Hard |
| 29 | Extremism Detection | Hard |
| 30 | Full Threat Response | Hard |

---

## Reward Shaping

All scores are strictly in **(0, 1)** — never 0.0 or 1.0.

### Text Classification Reward Tiers
```
0.05  Empty / invalid response
0.15  Valid format but wrong category
0.30  Correct category, wrong severity (off by 2+)
0.50  Correct category, close severity (off by 1)
0.70  Correct category + exact severity, weak reasoning
0.85  All correct with good reasoning
0.95  Perfect: all correct + expert-level reasoning with policy citations
```

### Contextual Policy Reward Tiers
```
0.05  No meaningful response
0.20  Response ignores context entirely
0.40  Correct base decision but no context reference
0.60  Good decision with some context awareness
0.80  Correct with strong context integration
0.95  Expert: considers edge cases, cultural factors, policy exceptions
```

### Threat Assessment Reward Tiers
```
0.05  No meaningful response
0.15  Response doesn't address threat detection
0.30  Detected threat presence correctly
0.50  Correct detection + severity in right range
0.70  Detection + severity + reasonable response plan
0.85  Comprehensive: detection + severity + response + confidence
0.95  Expert: all above + network analysis + escalation protocol
```

---

## Observation & Action Spaces

### Observation (returned by `/reset` and `/step`)
```json
{
  "session_id": "a1b2c3d4e5f67890",
  "task_id": "task_1",
  "domain": "text_classification",
  "difficulty": "easy",
  "title": "Basic Post Classification",
  "description": "Classify the post as safe, hate_speech, spam, or misinformation.",
  "post": {
    "text": "Just launched my startup! Check it out at totally-legit.ru...",
    "engagement": 12345,
    "author": "user_4321",
    "timestamp": "2026-04-11T12:00:00"
  },
  "step_number": 0,
  "max_steps": 5,
  "action_space": {
    "category": ["safe", "hate_speech", "spam", "misinformation", "harassment", "violence"],
    "severity": "integer 1-5",
    "action": ["keep", "label", "warn", "remove", "escalate", "ban"],
    "reasoning": "string explaining your decision"
  },
  "feedback": null,
  "previous_scores": null
}
```

### Action (sent to `/step`)

**Domain 1 — Text Classification:**
```json
{
  "category": "spam",
  "severity": 3,
  "action": "remove",
  "reasoning": "This post contains a suspicious URL and uses pressure tactics typical of spam. The urgency and promise of fast money are red flags."
}
```

**Domain 2 — Contextual Policy:**
```json
{
  "category": "misinformation",
  "action": "label",
  "policy_exception": false,
  "reasoning": "Author has 2 prior violations and the claim contradicts WHO data. No newsworthy exception applies."
}
```

**Domain 3 — Threat Assessment:**
```json
{
  "is_coordinated": true,
  "threat_level": "high",
  "category": "misinformation",
  "action": "escalate",
  "confidence": 0.85,
  "reasoning": "Multiple accounts with similar creation dates posting identical content. IP overlap detected. Escalate to trust & safety team for coordinated campaign investigation."
}
```

---

## API Reference

### `POST /reset`
Start a new episode.
```bash
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": 1}'
```

### `POST /step`
Submit an action and receive reward + feedback.
```bash
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "YOUR_SESSION_ID",
    "action": {
      "category": "spam",
      "severity": 3,
      "action": "remove",
      "reasoning": "Suspicious URL with urgency tactics."
    }
  }'
```

### `GET /state`
Get environment state.
```bash
curl http://localhost:7860/state
```

### `GET /health`
Health check (validates all 30 tasks produce valid scores).
```bash
curl http://localhost:7860/health
```

---

## Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py
# → Server running on http://localhost:7860

# Test health
curl http://localhost:7860/health
```

### Docker
```bash
# Build
docker build -t lunar-benchmark .

# Run
docker run -p 7860:7860 lunar-benchmark

# Or with docker-compose
docker-compose up
```

### Run Inference
```bash
export API_BASE_URL="https://api.openai.com/v1"
export API_KEY="your-key"
export MODEL_NAME="gpt-4"
export ENVIRONMENT_HOST="http://localhost:7860"

python inference.py
```

---

## Project Structure

```
lunar/
├── app.py                          # FastAPI server (OpenEnv endpoints)
├── models.py                       # Pydantic v2 typed models
├── inference.py                    # Baseline agent (multi-turn LLM)
├── openenv.yaml                    # OpenEnv spec manifest
├── content_moderation_env/
│   ├── __init__.py                 # Package exports
│   ├── environment.py              # Multi-turn environment engine
│   └── graders.py                  # 3 domain-specific graders
├── tests/                          # Test & validation scripts
├── Dockerfile                      # Docker deployment
├── docker-compose.yml              # Compose config
├── requirements.txt                # Python dependencies
└── pyproject.toml                  # Project metadata
```

---

## Pre-Submission Checklist

| Check | Status |
|-------|--------|
| `openenv.yaml` present and valid | ✅ |
| All 30 tasks produce scores in (0, 1) | ✅ |
| `POST /reset` works | ✅ |
| `POST /step` returns observation, reward, done, info | ✅ |
| `GET /state` returns environment state | ✅ |
| Multi-turn episodes (5 steps) | ✅ |
| Progressive context reveal | ✅ |
| Grader feedback per step | ✅ |
| 3 distinct domain graders | ✅ |
| Rich partial-credit (7 tiers per domain) | ✅ |
| Pydantic v2 typed models | ✅ |
| `inference.py` with baseline agent | ✅ |
| Docker builds and runs | ✅ |
| Difficulty gradient (easy → hard) | ✅ |
| Weighted scoring (later steps worth more) | ✅ |

---

## License

MIT License. Built for the OpenEnv Hackathon 2026.
