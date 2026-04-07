"""Service Layer - Individual component management services."""

import logging
from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)

try:
    from warehouse_env import Action
except ImportError:
    Action = None


class ServiceStatus(Enum):
    """Service health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealth:
    """Service health information."""
    name: str
    status: ServiceStatus
    message: str
    details: Dict


class EnvironmentService:
    """Manages warehouse environment instance."""

    def __init__(self):
        self.is_running = False
        self.task = "warehouse_easy"

    def health_check(self) -> ServiceHealth:
        """Check service health."""
        try:
            from warehouse_env import WarehouseEnv
            env = WarehouseEnv(task=self.task)
            obs = env.reset()
            env.step(Action(
                reorder_quantities=[0.0] * len(obs.warehouse_levels),
                transfers=[[0.0] * len(obs.warehouse_levels) for _ in range(len(obs.warehouse_levels))]
            ))
            return ServiceHealth(
                name="EnvironmentService",
                status=ServiceStatus.HEALTHY,
                message="Environment running normally",
                details={"task": self.task, "running": True}
            )
        except Exception as e:
            return ServiceHealth(
                name="EnvironmentService",
                status=ServiceStatus.UNHEALTHY,
                message=f"Environment failed: {str(e)}",
                details={"error": str(e)}
            )


class DockerService:
    """Manages Docker operations."""

    def __init__(self, os_layer):
        self.os = os_layer
        self.image_name = "warehouse-env"
        self.image_tag = "latest"

    def health_check(self) -> ServiceHealth:
        """Check Docker availability."""
        result = self.os.run_command(["docker", "--version"])
        if result.exit_code == 0:
            return ServiceHealth(
                name="DockerService",
                status=ServiceStatus.HEALTHY,
                message=result.stdout.strip(),
                details={"installed": True}
            )
        return ServiceHealth(
            name="DockerService",
            status=ServiceStatus.UNHEALTHY,
            message="Docker not available",
            details={"error": result.stderr}
        )

    def build_image(self, repo_path: str) -> bool:
        """Build Docker image."""
        cmd = ["docker", "build", "-t", f"{self.image_name}:{self.image_tag}", "."]
        result = self.os.run_command(cmd, cwd=repo_path, timeout=600)
        success = result.exit_code == 0
        logger.info(f"Docker build {'succeeded' if success else 'failed'}")
        return success

    def run_container(self, port: int = 5000, env: Optional[Dict] = None) -> bool:
        """Run Docker container."""
        env_args = []
        if env:
            for k, v in env.items():
                env_args.extend(["-e", f"{k}={v}"])

        cmd = (
            ["docker", "run", "-p", f"{port}:5000", "--rm"]
            + env_args
            + [f"{self.image_name}:{self.image_tag}"]
        )
        result = self.os.run_command(cmd, timeout=30)
        return result.exit_code == 0


class APIService:
    """Manages API server."""

    def __init__(self, os_layer):
        self.os = os_layer
        self.port = 5000
        self.is_running = False

    def health_check(self) -> ServiceHealth:
        """Check API server health."""
        result = self.os.run_command(
            ["curl", "-s", f"http://localhost:{self.port}/health"],
            timeout=5
        )
        if result.exit_code == 0 and "ok" in result.stdout:
            return ServiceHealth(
                name="APIService",
                status=ServiceStatus.HEALTHY,
                message="API server responding",
                details={"port": self.port, "running": True}
            )
        return ServiceHealth(
            name="APIService",
            status=ServiceStatus.UNHEALTHY,
            message="API server not responding",
            details={"port": self.port, "error": result.stderr}
        )


class ValidationService:
    """Manages validation and testing."""

    def __init__(self, os_layer):
        self.os = os_layer

    def validate_environment(self, repo_path: str) -> Dict:
        """Validate environment setup."""
        checks = {
            "openenv_yaml": self.os.file_exists(f"{repo_path}/openenv.yaml"),
            "dockerfile": self.os.file_exists(f"{repo_path}/Dockerfile"),
            "inference_py": self.os.file_exists(f"{repo_path}/inference.py"),
            "readme_md": self.os.file_exists(f"{repo_path}/README.md"),
            "models_py": self.os.file_exists(f"{repo_path}/warehouse_env/models.py"),
            "env_py": self.os.file_exists(f"{repo_path}/warehouse_env/env.py"),
            "graders_py": self.os.file_exists(f"{repo_path}/warehouse_env/graders.py"),
        }
        return checks

    def test_all_tasks(self) -> Dict:
        """Test all warehouse tasks."""
        try:
            from warehouse_env import WarehouseEnv, Action
            from warehouse_env.graders import get_grader

            results = {}
            for task in ["warehouse_easy", "warehouse_medium", "warehouse_hard"]:
                env = WarehouseEnv(task=task)
                obs = env.reset()
                
                # Run 5 steps
                for _ in range(5):
                    action = Action(
                        reorder_quantities=[50.0] * len(obs.warehouse_levels),
                        transfers=[[0.0] * len(obs.warehouse_levels) for _ in range(len(obs.warehouse_levels))]
                    )
                    obs, reward = env.step(action)
                
                # Grade
                grader = get_grader(task)
                grade = grader.grade(env.state, env.episode_rewards)
                results[task] = {
                    "score": grade["score"],
                    "valid": 0.0 <= grade["score"] <= 1.0
                }
            
            return results
        except Exception as e:
            logger.error(f"Task testing failed: {e}")
            return {}
