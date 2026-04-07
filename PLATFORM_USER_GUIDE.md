# AI Agent Platform - User Guide

## What is This Platform?

The **AI Agent Platform** is an automated orchestration system that manages the complete lifecycle of the warehouse environment. It acts as an intelligent middleware between you (the user) and the OS, automating:

- Environment setup
- Validation
- Docker containerization
- Inference execution
- Monitoring
- Reporting

## Quick Start

### 1. Initialize & Deploy

```bash
cd warehouse_env
python platform_start.py
```

This executes the complete deployment pipeline automatically.

### 2. CLI Commands

```bash
# Full deployment
python -m platform.cli deploy --repo .

# Quick validation
python -m platform.cli validate --repo .

# Check status
python -m platform.cli status --repo .

# Generate report
python -m platform.cli report --repo . --output report.json
```

## Platform Architecture

The platform consists of 6 interconnected layers:

### Layer 1: OS Layer
**Location**: `platform/core/os_layer.py`

Interfaces with the operating system:
- Command execution
- File operations
- System resource management
- Process management

### Layer 2: Service Layer
**Location**: `platform/services/service_layer.py`

Individual service components:
- **EnvironmentService**: Manages warehouse RL environment
- **DockerService**: Handles Docker operations
- **APIService**: Manages REST API server
- **ValidationService**: Runs validation tests

### Layer 3: Agent Layer
**Location**: `platform/agents/agent_layer.py`

Autonomous agents that execute tasks:

#### SetupAgent
- Installs dependencies
- Configures environment
- Prepares system

#### ValidationAgent
- Tests warehouse tasks (easy/medium/hard)
- Validates file structure
- Checks graders

#### DockerAgent
- Builds container image
- Manages Docker builds

#### InferenceAgent
- Runs inference script
- Collects baseline scores
- Validates output format

#### MonitoringAgent
- Checks service health
- Monitors resource usage
- Reports status

### Layer 4: Orchestration Layer
**Location**: `platform/orchestration/orchestrator.py`

Coordinates workflow execution:

#### Orchestrator
- Manages workflow definitions
- Executes steps sequentially
- Handles dependencies
- Tracks results

#### PipelineExecutor
- Chains multiple workflows
- Manages pipeline state
- Handles failures

### Layer 5: Platform Layer
**Location**: `platform/platform.py`

High-level platform interface:
- Initializes all layers
- Registers agents
- Defines workflows
- Exposes APIs

### Layer 6: CLI Layer
**Location**: `platform/cli.py`

Command-line interface:
- User commands
- Argument parsing
- Output formatting

## Supported Workflows

### Setup Workflow
```
SetupAgent → InstallDependencies
             ↓
             ValidationAgent → VerifySetup
                             ↓
                             SUCCESS/FAILURE
```

### Docker Workflow
```
DockerAgent → BuildImage
            ↓
            MonitoringAgent → HealthCheck
                            ↓
                            SUCCESS/FAILURE
```

### Testing Workflow
```
ValidationAgent → TestAllTasks
               ↓
               InferenceAgent → RunInference
                             ↓
                             SUCCESS/FAILURE
```

### Monitoring Workflow
```
MonitoringAgent → CheckServices
               ↓
               SUCCESS/FAILURE
```

## Complete Deployment Pipeline

```
FULL_DEPLOYMENT
├── setup_workflow
│   ├── SetupAgent: pip install -e .
│   └── ValidationAgent: verify setup
│
├── docker_workflow
│   ├── DockerAgent: docker build
│   └── MonitoringAgent: health check
│
├── testing_workflow
│   ├── ValidationAgent: test 3 tasks
│   └── InferenceAgent: run inference.py
│
└── monitoring_workflow
    └── MonitoringAgent: final health check
```

## Results & Reports

After execution, you'll get:

1. **Deployment Report** (`deployment_report.json`)
   - All workflow results
   - Execution times
   - Service health
   - Agent status
   - Error details

2. **Console Output**
   - Real-time execution logs
   - Step-by-step progress
   - Summary statistics
   - Next steps

## Example Execution

```
[1/4] Initializing platform...
      Platform initialized successfully
      
[2/4] Checking platform status...
      OS: win32
      Python: 3.11.2
      CPU Cores: 8
      Memory: 16384MB
      
[3/4] Executing deployment pipeline...
      This will:
      - Setup environment
      - Build Docker image
      - Validate all 3 tasks
      - Run baseline inference
      - Monitor health
      
      [SETUP_WORKFLOW]
      
      ✓ SetupAgent: Environment setup (15.23s)
      ✓ ValidationAgent: Setup verification (8.45s)
      
      [DOCKER_WORKFLOW]
      
      ✓ DockerAgent: Docker build (45.67s)
      ✓ MonitoringAgent: Health check (3.21s)
      
      [TESTING_WORKFLOW]
      
      ✓ ValidationAgent: Task testing (22.34s)
      ✓ InferenceAgent: Inference execution (18.90s)
      
      [MONITORING_WORKFLOW]
      
      ✓ MonitoringAgent: Service monitoring (2.15s)

[4/4] Generating deployment report...
      Report saved to: deployment_report.json

================================================================================
  DEPLOYMENT SUCCESSFUL
================================================================================

Total Duration: 116.00 seconds
Workflows Executed: 4/4

SUMMARY
────────────────────────────────────────────────────────────────────────────
✓ PASS     | setup_workflow                  |    23.68s
✓ PASS     | docker_workflow                 |    48.88s
✓ PASS     | testing_workflow                |    41.24s
✓ PASS     | monitoring_workflow             |     2.15s

Next Steps:
1. Review deployment report: deployment_report.json
2. Test API: curl http://localhost:5000/health
3. Deploy to HF Spaces
4. Run: python -m platform.cli --help
```

## Platform APIs

### Python API

```python
from platform.platform import WarehouseEnvPlatform

# Initialize
platform = WarehouseEnvPlatform('/path/to/repo')

# Execute deployment
result = platform.execute_full_deployment()

# Get status
status = platform.get_status()

# Save report
platform.save_report('report.json')
```

### CLI API

```bash
# Deploy
python -m platform.cli deploy --repo /path/to/repo

# Validate
python -m platform.cli validate --repo /path/to/repo

# Status
python -m platform.cli status --repo /path/to/repo

# Report
python -m platform.cli report --repo /path/to/repo --output report.json
```

## Error Handling

The platform handles errors gracefully:

- **Setup Failures**: Stop pipeline (required)
- **Docker Build Failures**: Stop pipeline (required)
- **Task Test Failures**: Stop pipeline (required)
- **Monitoring Failures**: Non-blocking (optional)

Required steps that fail terminate the pipeline.
Optional steps that fail are logged but continue.

## Performance

Typical execution times:
- Setup: 2-5 minutes
- Docker build: 5-10 minutes
- Validation: 2-3 minutes
- Inference: 10-15 minutes
- **Total**: 20-35 minutes

Varies based on system resources and network.

## Troubleshooting

### Setup Fails

```bash
# Check Python environment
python --version

# Install dependencies manually
pip install -e .

# Validate setup
python -m platform.cli validate --repo .
```

### Docker Build Fails

```bash
# Check Docker installation
docker --version

# Build manually
docker build -t warehouse-env:latest .

# Check disk space
df -h
```

### Inference Fails

```bash
# Check API credentials
echo $OPENAI_API_KEY

# Test API
curl https://api.openai.com/v1/models

# Run inference directly
WAREHOUSE_TASK=warehouse_easy python inference.py
```

### Memory Issues

```bash
# Check available memory
python -c "import psutil; print(psutil.virtual_memory())"

# Required: ~2GB free
```

## Configuration

Set environment variables before running:

```bash
export OPENAI_API_KEY=sk-...
export HF_TOKEN=...
export API_BASE_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4-turbo
```

Or create `.env` file:

```
OPENAI_API_KEY=sk-...
HF_TOKEN=...
API_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4-turbo
```

## Advanced Usage

### Custom Workflows

```python
from platform.orchestration import Orchestrator, WorkflowStep

orchestrator = Orchestrator()

# Create custom workflow
steps = [
    WorkflowStep("Custom Step 1", "setup", required=True, timeout=60),
    WorkflowStep("Custom Step 2", "validation", required=False, timeout=120),
]

orchestrator.define_workflow("custom", steps)
result = orchestrator.execute_workflow("custom")
```

### Custom Agents

```python
from platform.agents import BaseAgent, TaskResult, TaskType, AgentState
import time

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("CustomAgent")
    
    def execute(self) -> TaskResult:
        start = time.time()
        # Your logic here
        return TaskResult(
            task_type=TaskType.DEPLOYMENT,
            state=AgentState.SUCCESS,
            duration_seconds=time.time() - start,
            status_message="Custom task completed",
            details={},
            success=True
        )

# Register with platform
platform.orchestrator.register_agent("custom", CustomAgent())
```

## Monitoring & Logs

All operations are logged to console:

- **INFO**: Operation progress
- **WARNING**: Non-critical issues
- **ERROR**: Failed operations
- **DEBUG**: Detailed execution (with -v flag)

Enable verbose logging:

```bash
python -m platform.cli deploy --repo . --verbose
```

## Next Steps

1. **Run Deployment**: `python platform_start.py`
2. **Review Report**: Check `deployment_report.json`
3. **Deploy to HF Spaces**: Follow `HF_SPACES_DEPLOYMENT.md`
4. **Monitor Services**: `python -m platform.cli status`
5. **Generate Reports**: `python -m platform.cli report`

## Support

- **Platform Docs**: See `PLATFORM_ARCHITECTURE.md`
- **Deployment Docs**: See `HF_SPACES_DEPLOYMENT.md`
- **Environment Docs**: See `README.md`
- **Architecture**: See `COMPLETION_SUMMARY.md`

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: April 6, 2026
