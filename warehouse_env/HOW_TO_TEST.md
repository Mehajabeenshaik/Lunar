# TESTING YOUR AI AGENT PLATFORM

## Quick Tests (No waiting required)

### Test 1: Environment Validation (2 min) ✓
Verify the warehouse environment works for all 3 tasks.

```bash
cd c:\Users\HP\Documents\lunar\warehouse_env
python test_quick.py
```

**Expected Output:**
```
✓ PASS | warehouse_easy Score: 0.969
✓ PASS | warehouse_medium Score: 0.774
✓ PASS | warehouse_hard Score: 0.901
RESULT: ✓ ALL TESTS PASSED
```

**What it tests:**
- Environment initialization
- All 3 task graders work
- Scores are valid (0.0-1.0)
- Step execution works

---

### Test 2: Inference Logging Format (1 min) ✓
Verify logging matches requirements exactly.

```bash
python test_logging.py
```

**Expected Output:**
```
[START] task=warehouse_easy env=warehouse_env model=test-model
[STEP] step=1 action=reorder([50.0]) reward=0.97 done=false error=null
[STEP] step=2 action=reorder([50.0]) reward=0.98 done=false error=null
[STEP] step=3 action=reorder([50.0]) reward=0.99 done=false error=null
[END] success=true steps=3 score=0.98 rewards=0.97,0.98,0.99
✓ Log format verified!
```

**What it tests:**
- [START] format correct
- [STEP] format correct
- [END] format correct
- All fields present
- All values valid

---

### Test 3: Full Deployment (20-35 min, CPU intensive)
Complete platform deployment with all 5 agents.

```bash
python test_full_deployment.py
```

**This will:**
1. Initialize platform (all 6 layers)
2. Setup environment (install deps)
3. Build Docker image
4. Validate all 3 tasks
5. Run inference script
6. Perform monitoring
7. Generate report

**Expected Output:**
```
[1/2] Initializing platform...
      ✓ Platform initialized

[2/2] Executing deployment pipeline...
      Running all workflows...

================================================================================
✓ DEPLOYMENT SUCCESSFUL
================================================================================

Total Duration: ...s
Workflows: 4/4
Report saved to: test_deployment_report.json
```

---

## Test via CLI Commands

### Validate only (2 min)
```bash
python -m platform.cli validate --repo .
```

### Deploy (20-35 min)
```bash
python -m platform.cli deploy --repo .
```

### Check status
```bash
python -m platform.cli status --repo .
```

### Generate report
```bash
python -m platform.cli report --repo . --output my_report.json
```

---

## Manual Testing Checklist

### Environment Tests
- [ ] `from warehouse_env import WarehouseEnv` works
- [ ] warehouse_easy task runs
- [ ] warehouse_medium task runs  
- [ ] warehouse_hard task runs
- [ ] All scores 0.0-1.0
- [ ] Reward signals appear each step

### API Tests
```bash
# Start server
python -m warehouse_env.server &

# In another terminal:
curl http://localhost:5000/health

# Expected: {"status":"ok"}
```

- [ ] /health responds
- [ ] /reset works
- [ ] /step works
- [ ] /state returns state
- [ ] /render returns text

### Docker Tests (if Docker installed)
```bash
docker build -t warehouse-env:test .
docker run --rm warehouse-env:test python -c "from warehouse_env import WarehouseEnv; print('OK')"
```

- [ ] Docker build succeeds
- [ ] Container runs
- [ ] Environment loads inside container

### Platform Tests
```bash
python platform_start.py
```

- [ ] Platform initializes
- [ ] All 5 agents register
- [ ] All 4 workflows defined
- [ ] Workflows execute successfully
- [ ] Report generated

---

## Test Results Summary

| Test | Time | Status |
|------|------|--------|
| Test 1: Environment | 2 min | ✓ PASS |
| Test 2: Logging | 1 min | ✓ PASS |
| Test 3: Full Deploy | 20-35 min | ✓ READY |
| CLI Commands | 5 min | ✓ READY |
| Manual Checklist | 10 min | ✓ READY |

**Total Test Time:** 40-50 minutes (optional full tests)  
**Critical Tests:** 3 minutes (Tests 1 & 2)

---

## What Gets Tested

### Environment
- ✓ 3 tasks (easy/medium/hard)
- ✓ Reward function
- ✓ Graders
- ✓ Scoring (0.0-1.0)

### Platform Layers
- ✓ OS Layer (system calls)
- ✓ Service Layer (4 services)
- ✓ Agent Layer (5 agents)
- ✓ Orchestration Layer (workflows)
- ✓ Platform Layer (coordination)
- ✓ CLI Layer (commands)

### Workflows
- ✓ Setup Workflow
- ✓ Docker Workflow
- ✓ Testing Workflow
- ✓ Monitoring Workflow

### Output Format
- ✓ [START] line
- ✓ [STEP] lines (multiple)
- ✓ [END] line
- ✓ Field order correct
- ✓ Field values correct
- ✓ Decimal formatting (0.00)

### Error Handling
- ✓ Invalid actions handled
- ✓ API errors managed
- ✓ Docker fails gracefully
- ✓ Service failures logged

---

## Quick Test Now

Run these 2 commands RIGHT NOW to verify everything:

```bash
# Test 1: 2 minutes
python test_quick.py

# Test 2: 1 minute  
python test_logging.py
```

**Expected: ✓ ALL TESTS PASSED on both**

If both pass → **You're good to deploy to HF Spaces!**

---

## Next: Deploy to HF Spaces

After testing completes:

1. Review `deployment_report.json`
2. Follow `HF_SPACES_DEPLOYMENT.md`
3. Create HF Space
4. Push code
5. Add secrets
6. Space deploys automatically
7. Submit URL to competition

---

## Verify Your Build

| Component | Test Command | Expected |
|-----------|--------------|----------|
| Imports | `python -c "from warehouse_env import WarehouseEnv"` | No error |
| Environment | `python test_quick.py` | ✓ ALL TESTS PASSED |
| Logging | `python test_logging.py` | ✓ Log format verified |
| Platform | `python platform_start.py` | ✓ DEPLOYMENT SUCCESSFUL |
| CLI | `python -m platform.cli status` | JSON output |
| API | `curl http://localhost:5000/health` | {"status":"ok"} |

---

**Status: Ready to Test & Deploy** ✓

Start with `python test_quick.py` - takes only 2 minutes!
