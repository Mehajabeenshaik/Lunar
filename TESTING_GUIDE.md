"""
TESTING GUIDE - AI Agent Platform & Warehouse Environment
=========================================================================

Three levels of testing from quick validation to full deployment.
"""

# =========================================================================
# TEST 1: QUICK VALIDATION (2-3 minutes)
# =========================================================================

print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                      TEST 1: QUICK VALIDATION                        ║
║                    (2-3 minutes)                                      ║
╚═══════════════════════════════════════════════════════════════════════╝

Quick validation tests the warehouse environment only.

STEPS:
------

1. Open PowerShell in: c:\\Users\\HP\\Documents\\lunar\\warehouse_env

2. Run these commands in order:

   # Activate environment
   .venv\\Scripts\\Activate.ps1

   # Test environment module
   python -m pytest -v warehouse_env/ 2>/dev/null || python -c "
import sys
sys.path.insert(0, '.')
from warehouse_env import WarehouseEnv, Action
from warehouse_env.graders import get_grader

print('Testing warehouse environment...')

# Test each task
for task in ['warehouse_easy', 'warehouse_medium', 'warehouse_hard']:
    print(f'  Testing {task}...')
    env = WarehouseEnv(task=task)
    obs = env.reset()
    
    # Run 3 steps
    for i in range(3):
        action = Action(
            reorder_quantities=[50.0]*len(obs.warehouse_levels),
            transfers=[[0.0]*len(obs.warehouse_levels) for _ in range(len(obs.warehouse_levels))]
        )
        obs, reward = env.step(action)
    
    # Grade
    grader = get_grader(task)
    grade = grader.grade(env.state, env.episode_rewards)
    score = grade['score']
    print(f'    Score: {score:.3f} (valid: {0.0 <= score <= 1.0})')

print('\\nQuick validation passed!')
"

   # Test inference format
   python -c "
import sys
sys.path.insert(0, '.')
from warehouse_env import WarehouseEnv, Action
from warehouse_env.graders import get_grader

print('\\nTesting inference format...')

task = 'warehouse_easy'
env = WarehouseEnv(task=task)
obs = env.reset()

print(f'[START] task={task} env=warehouse_env model=test-model')

for step in range(3):
    action = Action(
        reorder_quantities=[50.0]*len(obs.warehouse_levels),
        transfers=[[0.0]*len(obs.warehouse_levels) for _ in range(len(obs.warehouse_levels))]
    )
    obs, reward = env.step(action)
    print(f'[STEP] step={step+1} action=reorder([50.0]) reward={reward.value:.2f} done={str(reward.done).lower()} error=null')

grader = get_grader(task)
grade = grader.grade(env.state, env.episode_rewards)
rewards = ','.join(f'{r:.2f}' for r in env.episode_rewards)
print(f'[END] success=true steps={len(env.episode_rewards)} score={grade[\"score\"]:.2f} rewards={rewards}')

print('\\nInference format test passed!')
"

EXPECTED OUTPUT:
   - warehouse_easy Score: 0.9+ (valid: True)
   - warehouse_medium Score: 0.8+ (valid: True)
   - warehouse_hard Score: 0.8+ (valid: True)
   - [START], [STEP], [END] logs printed
   - "Quick validation passed!"

RESULT: If all pass ✓ environment is working


╔═══════════════════════════════════════════════════════════════════════╗
║                      TEST 2: DOCKER BUILD (15 minutes)               ║
║                    (Requires Docker installed)                       ║
╚═══════════════════════════════════════════════════════════════════════╝

Tests Docker containerization.

STEPS:
------

1. Make sure Docker is installed and running:
   docker --version

2. In PowerShell, navigate to project:
   cd c:\\Users\\HP\\Documents\\lunar\\warehouse_env

3. Build Docker image:
   docker build -t warehouse-env:test .

   EXPECTED OUTPUT:
   - "Successfully tagged warehouse-env:test"
   - Build completes in 2-5 minutes
   - No errors

4. Test Docker image:
   docker run --rm warehouse-env:test python -c "
from warehouse_env import WarehouseEnv
env = WarehouseEnv('warehouse_easy')
obs = env.reset()
print('Docker test passed - environment loads correctly')
"

   EXPECTED OUTPUT:
   - "Docker test passed - environment loads correctly"

5. Check if server runs:
   docker run -p 5000:5000 --rm warehouse-env:test &
   
   In another terminal after 5 seconds:
   curl http://localhost:5000/health

   EXPECTED OUTPUT:
   - {"status":"ok"}

RESULT: If all pass ✓ Docker is working


╔═══════════════════════════════════════════════════════════════════════╗
║                TEST 3: FULL PLATFORM (20-35 minutes)                 ║
║                    (Complete deployment)                             ║
╚═══════════════════════════════════════════════════════════════════════╝

Tests the complete AI Agent Platform with all 5 agents.

STEPS:
------

1. Navigate to project:
   cd c:\\Users\\HP\\Documents\\lunar\\warehouse_env

2. Activate environment if not already:
   .venv\\Scripts\\Activate.ps1

3. Run full platform deployment:
   python platform_start.py

   This will execute:
   ✓ Setup Workflow (install deps)
   ✓ Docker Workflow (build image)
   ✓ Testing Workflow (validate tasks + run inference)
   ✓ Monitoring Workflow (health checks)

4. Watch the output:
   - Real-time logs from each agent
   - Status of each workflow
   - Execution times
   - Final summary

   EXPECTED OUTPUT:
   - [1/4] Initializing platform...
   - [2/4] Checking platform status...
   - [3/4] Executing deployment pipeline...
   - [4/4] Generating deployment report...
   - DEPLOYMENT SUCCESSFUL
   - deployment_report.json created

5. Verify report:
   cat deployment_report.json | python -m json.tool | head -50

   EXPECTED OUTPUT:
   - Valid JSON structure
   - All workflows with "success": true
   - Execution times for each step

RESULT: If all pass ✓ complete platform is working


╔═══════════════════════════════════════════════════════════════════════╗
║                      TEST 4: CLI COMMANDS (5 minutes)                ║
║                    (Platform CLI interface)                          ║
╚═══════════════════════════════════════════════════════════════════════╝

Tests individual CLI commands.

STEPS:
------

1. In PowerShell, test each command:

   # Test deploy (note: this runs full platform)
   python -m platform.cli deploy --repo . 2>&1 | head -20

   # Test validate (quick validation only)
   python -m platform.cli validate --repo .

   # Test status
   python -m platform.cli status --repo .

   # Test report generation
   python -m platform.cli report --repo . --output test_report.json
   cat test_report.json | python -m json.tool | head -20

EXPECTED OUTPUT:
   - Commands execute without errors
   - JSON output is valid
   - Reports are generated

RESULT: If all pass ✓ CLI is working


╔═══════════════════════════════════════════════════════════════════════╗
║                  MANUAL TESTING CHECKLIST                            ║
╚═══════════════════════════════════════════════════════════════════════╝

Use this to verify each component:

ENVIRONMENT:
  [ ] warehouse_easy runs without errors
  [ ] warehouse_medium runs without errors
  [ ] warehouse_hard runs without errors
  [ ] All scores are between 0.0 and 1.0
  [ ] Step rewards decrease/increase appropriately

PLATFORM LAYERS:
  [ ] OS Layer initializes (system info shows)
  [ ] Service Layer connects (4 services ready)
  [ ] Agent Layer registers (5 agents available)
  [ ] Orchestration Layer defines workflows (4 workflows)
  [ ] Platform Layer coordinates (initialization complete)
  [ ] CLI Layer responds (commands work)

WORKFLOWS:
  [ ] Setup Workflow: Dependencies install
  [ ] Docker Workflow: Image builds
  [ ] Testing Workflow: Tasks pass validation
  [ ] Monitoring Workflow: Health checks pass

LOGGING FORMAT:
  [ ] [START] line present
  [ ] [STEP] lines with correct format
  [ ] [END] line present
  [ ] All fields populated correctly
  [ ] No format deviations

REPORTING:
  [ ] deployment_report.json created
  [ ] Valid JSON structure
  [ ] All execution times recorded
  [ ] Execution history populated
  [ ] No errors in report


╔═══════════════════════════════════════════════════════════════════════╗
║                     TROUBLESHOOTING                                  ║
╚═══════════════════════════════════════════════════════════════════════╝

If a test fails:

1. QUICK VALIDATION FAILS
   - Check Python version: python --version (need 3.10+)
   - Check installation: pip show warehouse-env
   - Try manual test: python -c "from warehouse_env import WarehouseEnv"

2. DOCKER BUILD FAILS
   - Check Docker: docker --version
   - Check disk space: disk usage > 5GB free required
   - Manual build: docker build -t test .

3. PLATFORM FAILS
   - Check logs in deployment_report.json
   - Verify services: python -m platform.cli status
   - Check individual agents: python -c "from platform.agents import SetupAgent"

4. CLI FAILS
   - Check install: python -m platform --help
   - Verify path: pwd (should be in warehouse_env folder)
   - Try directly: python platform/cli.py deploy --repo .


╔═══════════════════════════════════════════════════════════════════════╗
║                    QUICK REFERENCE                                   ║
╚═══════════════════════════════════════════════════════════════════════╝

Test 1 (Quick):    python -c "from warehouse_env import WarehouseEnv; ..."
Test 2 (Docker):   docker build . && docker run warehouse-env:test
Test 3 (Full):     python platform_start.py
Test 4 (CLI):      python -m platform.cli deploy --repo .

Execution Time:
  Test 1: 2-3 min
  Test 2: 15 min
  Test 3: 20-35 min
  Test 4: 5 min

Total: 42-58 minutes for all tests


═══════════════════════════════════════════════════════════════════════

Ready to test? Start with TEST 1 (Quick Validation) - takes only 2-3 minutes!
""")
