# LUNAR vs APEX: Requirements Comparison

## Executive Summary

APEX has successfully passed all OpenEnv v1 requirements and is deployed/running. This document compares LUNAR's current implementation with APEX's proven architecture to identify gaps and required updates.

---

## ✅ APEX Strengths (Passed All Requirements)

| Feature | Status | Details |
|---------|--------|---------|
| **3+ Tasks** | ✅ | 29 tasks across 3 domains |
| **Task Difficulty Progression** | ✅ | Easy → Medium → Hard |
| **Deterministic Graders** | ✅ | Same input = same score always |
| **Partial Credit Rewards** | ✅ | [0.1, 1.0] never binary, never zero |
| **OpenEnv API** | ✅ | /reset /step /state /health /docs |
| **Typed Models** | ✅ | Pydantic v2 Observation, Action, RewardInfo |
| **Session Management** | ✅ | File-based persistence (multi-worker safe) |
| **Inference.py** | ✅ | [START][STEP][END] log format |
| **Baseline Benchmark** | ✅ | Runs in 12 min (limit: 20 min) |
| **Environmental Variables** | ✅ | OPENAI_API_KEY, API_BASE_URL, MODEL_NAME |
| **Docker Build** | ✅ | 2 vCPU / 8GB RAM verified |
| **HF Spaces Deploy** | ✅ | Live at huggingface.co/spaces/ShaikB/Apex |
| **openenv.yaml** | ✅ | Correct app field + complete spec |
| **Gradio UI** | ✅ | app_gradio.py for integrated UI |
| **Security Sandbox** | ✅ | Restricted __builtins__, 5-sec timeout |

---

## 🔄 LUNAR Current Status

| Feature | Status | Current | Gap |
|---------|--------|---------|-----|
| **Tasks Implemented** | ⚠️ | 3 (warehouse_easy/medium/hard) | openenv.yaml claims 21 (OUTDATED) |
| **openenv.yaml** | ❌ | Claims 21 tasks, 5 domains | Must update to 3 tasks only |
| **Graders** | ✅ | Working for 3 tasks | None (sufficient) |
| **API Endpoints** | ✅ | /reset /step /state /health /manifest /tasks /sessions /leaderboard | None |
| **Pydantic Models** | ✅ | Observation, Action present | None |
| **Session Management** | ✅ | SessionManager implemented | None |
| **inference.py** | ✅ | Present | Need to verify [START][STEP][END] format |
| **Gradio UI** | ❌ | Not present | OPTIONAL (APEX has it) |
| **Docker Build** | ✅ | Dockerfile exists | None |
| **Environmental Vars** | ✅ | OPENAI_API_KEY support | None |

---

## 🎯 CRITICAL UPDATES REQUIRED

### 1. UPDATE openenv.yaml ⚠️ PRIORITY: HIGH
**Current Issue:** Claims 21 non-existent tasks
**APEX Standard:** Accurate task list matching implementation

**Fix:**
```yaml
name: lunar-warehouse-benchmark
version: "3.0.0"
description: "LUNAR: Warehouse Inventory Optimization Benchmark"
tasks:
  - id: warehouse_easy      # 1 warehouse, 30 steps
  - id: warehouse_medium    # 3 warehouses, 60 steps 
  - id: warehouse_hard      # 5 warehouses, 90 steps
total_tasks: 3
```

### 2. VERIFY inference.py Format ⚠️ PRIORITY: HIGH
**APEX Standard:** `[START] [STEP] [END]` exact format

**What APEX uses:**
```python
print(f"[START] task={task_id} env=apex-engineering-benchmark model={model}")
print(f"[STEP]  step={step} action=\"...\" reward={reward:.4f} done={done} error=None")
print(f"[END]   task={task_id} success={success} steps={steps} score={score:.4f}")
```

**Action:** Review LUNAR's inference.py and ensure matching log format.

### 3. VERIFY Grader Determinism ⚠️ PRIORITY: MEDIUM
**APEX Standard:** Same input → exact same reward score

**Verification Needed:**
- Run same task twice with same parameters
- Confirm identical reward scores
- No randomness in grading logic

### 4. ADD Gradio UI (OPTIONAL) 📌 PRIORITY: LOW
**APEX:** Has `app_gradio.py` for web interface
**LUNAR:** Not critical for submission, but nice-to-have

---

## 📋 APEX's Pre-Submission Checklist (ALL ✅)

```
✅ HF Space deploys and returns 200
✅ POST /reset returns session_id + observation  
✅ POST /step returns reward + done + feedback
✅ GET /state returns session state
✅ OpenEnv spec: typed Pydantic models
✅ openenv.yaml present and valid
✅ 3+ tasks with graders scoring 0.0–1.0 (APEX has 29)
✅ Graders are deterministic
✅ Difficulty progression easy → medium → hard
✅ Reward provides partial progress signal (never binary)
✅ Baseline inference.py runs without error
✅ Reads OPENAI_API_KEY from environment
✅ API_BASE_URL, MODEL_NAME, HF_TOKEN defined
✅ inference.py in root directory
✅ Uses OpenAI client for all LLM calls
✅ [START] [STEP] [END] log format exact
✅ Runtime under 20 minutes
✅ Runs on 2 vCPU, 8GB RAM
✅ Dockerfile builds and runs cleanly
✅ README complete
```

---

## 🔧 LUNAR's Current Checklist

| Item | Status | Notes |
|------|--------|-------|
| HF Space deploys and returns 200 | ✅ | Live and working |
| POST /reset returns session_id + observation | ✅ | Implemented |
| POST /step returns reward + done + feedback | ✅ | Implemented |
| GET /state returns session state | ✅ | Implemented |
| OpenEnv spec: typed Pydantic models | ✅ | Present |
| openenv.yaml present and valid | ❌ | OUTDATED - needs update |
| 3+ tasks with graders | ✅ | 3 tasks working |
| Graders are deterministic | ✅ | Assumed true |
| Difficulty progression | ✅ | easy → medium → hard |
| Reward partial credit [0.0-1.0] | ✅ | Range guaranteed |
| inference.py present | ✅ | Present |
| Reads OPENAI_API_KEY | ✅ | Yes |
| API_BASE_URL, MODEL_NAME defined | ✅ | Yes |
| inference.py in root | ✅ | Yes |
| Uses OpenAI client | ✅ | Yes |
| [START] [STEP] [END] format | ⚠️ | NEEDS VERIFICATION |
| Runtime under 20 minutes | ⚠️ | NEEDS TESTING |
| Runs on 2 vCPU, 8GB RAM | ⚠️ | NEEDS TESTING |
| Dockerfile builds cleanly | ✅ | Yes |
| README complete | ✅ | Yes |

---

## 🚀 Recommended Actions

### Phase 1: CRITICAL (Must complete before submission)
1. ✏️ Update `openenv.yaml` - Replace full file with 3-task accurate spec
2. 🔍 Verify `inference.py` - Confirm [START][STEP][END] format matches APEX exactly
3. ✓️ Test grader determinism - Run same task 2x, verify identical scores
4. ⏱️ Benchmark runtime - Ensure inference completes under 20 min

### Phase 2: OPTIONAL (Enhancement)
- Add Gradio UI (app_gradio.py) for better UX
- Add file-based session persistence for cross-worker support
- Add comprehensive stress test suite

### Phase 3: DEPLOYMENT
- Rebuild Docker image with updated files
- Test locally: `docker run -p 7860:7860 lunar-benchmark`
- Push to HF Spaces for rebuild
- Retest all endpoints

---

## 📊 Expected Outcome

After these updates, LUNAR will:
- ✅ Match APEX's architecture and standards
- ✅ Pass all OpenEnv v1 compliance checks
- ✅ Be ready for production submission
- ✅ Have 3 fully-working, well-documented warehouse tasks
- ✅ Provide clear feedback loop for agent training

**Estimated time to complete: 30-45 minutes**

---
