"""Agent Layer - Autonomous AI agents for task execution."""

import logging
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of tasks agents handle."""
    SETUP = "setup"
    VALIDATION = "validation"
    DEPLOYMENT = "deployment"
    INFERENCE = "inference"
    MONITORING = "monitoring"


class AgentState(Enum):
    """Agent execution state."""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class TaskResult:
    """Result from task execution."""
    task_type: TaskType
    state: AgentState
    duration_seconds: float
    status_message: str
    details: Dict
    success: bool


class BaseAgent(ABC):
    """Base class for autonomous agents."""

    def __init__(self, name: str):
        self.name = name
        self.state = AgentState.IDLE
        self.last_result: Optional[TaskResult] = None

    @abstractmethod
    def execute(self) -> TaskResult:
        """Execute the task."""
        pass

    def get_status(self) -> Dict:
        """Get agent status."""
        return {
            "name": self.name,
            "state": self.state.value,
            "last_result": self.last_result,
        }


class SetupAgent(BaseAgent):
    """Agent for environment setup."""

    def __init__(self, os_layer, repo_path: str):
        super().__init__("SetupAgent")
        self.os = os_layer
        self.repo_path = repo_path

    def execute(self) -> TaskResult:
        """Setup environment."""
        import time
        start = time.time()
        
        try:
            self.state = AgentState.RUNNING
            
            # Create directories
            self.os.create_directory(f"{self.repo_path}/.env_setup")
            
            # Install dependencies
            result = self.os.run_command(
                ["pip", "install", "-e", "."],
                cwd=self.repo_path,
                timeout=120
            )
            
            if result.exit_code != 0:
                raise Exception(f"Pip install failed: {result.stderr}")
            
            self.state = AgentState.SUCCESS
            return TaskResult(
                task_type=TaskType.SETUP,
                state=self.state,
                duration_seconds=time.time() - start,
                status_message="Environment setup complete",
                details={"pip_install": "success"},
                success=True
            )
        except Exception as e:
            self.state = AgentState.FAILED
            return TaskResult(
                task_type=TaskType.SETUP,
                state=self.state,
                duration_seconds=time.time() - start,
                status_message=f"Setup failed: {str(e)}",
                details={"error": str(e)},
                success=False
            )


class ValidationAgent(BaseAgent):
    """Agent for validation tasks."""

    def __init__(self, os_layer, validation_service, repo_path: str):
        super().__init__("ValidationAgent")
        self.os = os_layer
        self.validation = validation_service
        self.repo_path = repo_path

    def execute(self) -> TaskResult:
        """Validate environment."""
        import time
        start = time.time()
        
        try:
            self.state = AgentState.RUNNING
            
            # Validate files
            file_checks = self.validation.validate_environment(self.repo_path)
            all_files_exist = all(file_checks.values())
            
            # Test tasks
            task_results = self.validation.test_all_tasks()
            all_tasks_valid = all(t.get("valid", False) for t in task_results.values())
            
            success = all_files_exist and all_tasks_valid
            self.state = AgentState.SUCCESS if success else AgentState.FAILED
            
            return TaskResult(
                task_type=TaskType.VALIDATION,
                state=self.state,
                duration_seconds=time.time() - start,
                status_message="Validation complete",
                details={
                    "files": file_checks,
                    "tasks": task_results,
                    "all_passed": success
                },
                success=success
            )
        except Exception as e:
            self.state = AgentState.FAILED
            return TaskResult(
                task_type=TaskType.VALIDATION,
                state=self.state,
                duration_seconds=time.time() - start,
                status_message=f"Validation failed: {str(e)}",
                details={"error": str(e)},
                success=False
            )


class DockerAgent(BaseAgent):
    """Agent for Docker operations."""

    def __init__(self, docker_service, repo_path: str):
        super().__init__("DockerAgent")
        self.docker = docker_service
        self.repo_path = repo_path

    def execute(self) -> TaskResult:
        """Build Docker image."""
        import time
        start = time.time()
        
        try:
            self.state = AgentState.RUNNING
            
            success = self.docker.build_image(self.repo_path)
            self.state = AgentState.SUCCESS if success else AgentState.FAILED
            
            return TaskResult(
                task_type=TaskType.DEPLOYMENT,
                state=self.state,
                duration_seconds=time.time() - start,
                status_message="Docker build complete" if success else "Docker build failed",
                details={"image_built": success},
                success=success
            )
        except Exception as e:
            self.state = AgentState.FAILED
            return TaskResult(
                task_type=TaskType.DEPLOYMENT,
                state=self.state,
                duration_seconds=time.time() - start,
                status_message=f"Docker build failed: {str(e)}",
                details={"error": str(e)},
                success=False
            )


class InferenceAgent(BaseAgent):
    """Agent for running inference."""

    def __init__(self, os_layer, repo_path: str):
        super().__init__("InferenceAgent")
        self.os = os_layer
        self.repo_path = repo_path

    def execute(self) -> TaskResult:
        """Run inference script."""
        import time
        start = time.time()
        
        try:
            self.state = AgentState.RUNNING
            
            # Run inference script
            result = self.os.run_command(
                ["python", "inference.py"],
                cwd=self.repo_path,
                timeout=1200,
                env={"WAREHOUSE_TASK": "warehouse_easy"}
            )
            
            success = result.exit_code == 0
            self.state = AgentState.SUCCESS if success else AgentState.FAILED
            
            return TaskResult(
                task_type=TaskType.INFERENCE,
                state=self.state,
                duration_seconds=time.time() - start,
                status_message="Inference completed" if success else "Inference failed",
                details={
                    "exit_code": result.exit_code,
                    "stdout_lines": len(result.stdout.split('\n')),
                    "has_logs": "[START]" in result.stdout and "[END]" in result.stdout
                },
                success=success
            )
        except Exception as e:
            self.state = AgentState.FAILED
            return TaskResult(
                task_type=TaskType.INFERENCE,
                state=self.state,
                duration_seconds=time.time() - start,
                status_message=f"Inference failed: {str(e)}",
                details={"error": str(e)},
                success=False
            )


class MonitoringAgent(BaseAgent):
    """Agent for continuous monitoring."""

    def __init__(self, services: Dict):
        super().__init__("MonitoringAgent")
        self.services = services

    def execute(self) -> TaskResult:
        """Monitor all services."""
        import time
        start = time.time()
        
        try:
            self.state = AgentState.RUNNING
            
            health_results = {}
            for name, service in self.services.items():
                health = service.health_check()
                health_results[name] = {
                    "status": health.status.value,
                    "message": health.message
                }
            
            all_healthy = all(
                h["status"] == "healthy"
                for h in health_results.values()
            )
            
            self.state = AgentState.SUCCESS if all_healthy else AgentState.FAILED
            
            return TaskResult(
                task_type=TaskType.MONITORING,
                state=self.state,
                duration_seconds=time.time() - start,
                status_message="Monitoring complete",
                details=health_results,
                success=all_healthy
            )
        except Exception as e:
            self.state = AgentState.FAILED
            return TaskResult(
                task_type=TaskType.MONITORING,
                state=self.state,
                duration_seconds=time.time() - start,
                status_message=f"Monitoring failed: {str(e)}",
                details={"error": str(e)},
                success=False
            )
