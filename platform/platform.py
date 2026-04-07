"""Main Platform - Complete AI Agent Platform."""

import logging
import json
from typing import Dict, Optional
from pathlib import Path

from platform.core.os_layer import OSLayer
from platform.services.service_layer import (
    EnvironmentService, DockerService, APIService, ValidationService, ServiceStatus
)
from platform.agents.agent_layer import (
    SetupAgent, ValidationAgent, DockerAgent, InferenceAgent, MonitoringAgent
)
from platform.orchestration.orchestrator import Orchestrator, WorkflowStep, PipelineExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class WarehouseEnvPlatform:
    """Main AI Agent Platform for complete task automation."""

    def __init__(self, repo_path: str):
        """Initialize platform."""
        self.repo_path = repo_path
        self.os_layer = OSLayer()
        self.orchestrator = Orchestrator()
        self.pipeline_executor = PipelineExecutor(self.orchestrator)
        self._initialize_services()
        self._register_agents()
        self._define_workflows()
        self._define_pipelines()

    def _initialize_services(self):
        """Initialize service layer."""
        logger.info("Initializing services...")
        
        self.env_service = EnvironmentService()
        self.docker_service = DockerService(self.os_layer)
        self.api_service = APIService(self.os_layer)
        self.validation_service = ValidationService(self.os_layer)
        
        logger.info("Services initialized")

    def _register_agents(self):
        """Register all agents with orchestrator."""
        logger.info("Registering agents...")
        
        self.setup_agent = SetupAgent(self.os_layer, self.repo_path)
        self.validation_agent = ValidationAgent(
            self.os_layer, self.validation_service, self.repo_path
        )
        self.docker_agent = DockerAgent(self.docker_service, self.repo_path)
        self.inference_agent = InferenceAgent(self.os_layer, self.repo_path)
        self.monitoring_agent = MonitoringAgent({
            "environment": self.env_service,
            "docker": self.docker_service,
            "api": self.api_service,
        })
        
        self.orchestrator.register_agent("setup", self.setup_agent)
        self.orchestrator.register_agent("validation", self.validation_agent)
        self.orchestrator.register_agent("docker", self.docker_agent)
        self.orchestrator.register_agent("inference", self.inference_agent)
        self.orchestrator.register_agent("monitoring", self.monitoring_agent)
        
        logger.info("5 agents registered")

    def _define_workflows(self):
        """Define workflows."""
        logger.info("Defining workflows...")
        
        # Setup workflow
        self.orchestrator.define_workflow("setup_workflow", [
            WorkflowStep("Setup environment", "setup", required=True, timeout=300),
            WorkflowStep("Validate setup", "validation", required=True, timeout=120),
        ])
        
        # Docker workflow
        self.orchestrator.define_workflow("docker_workflow", [
            WorkflowStep("Build Docker image", "docker", required=True, timeout=600),
            WorkflowStep("Monitor services", "monitoring", required=False, timeout=60),
        ])
        
        # Testing workflow
        self.orchestrator.define_workflow("testing_workflow", [
            WorkflowStep("Validate all tasks", "validation", required=True, timeout=120),
            WorkflowStep("Run inference", "inference", required=True, timeout=1200),
        ])
        
        # Monitoring workflow
        self.orchestrator.define_workflow("monitoring_workflow", [
            WorkflowStep("Monitor system", "monitoring", required=False, timeout=60),
        ])
        
        logger.info("4 workflows defined")

    def _define_pipelines(self):
        """Define execution pipelines."""
        logger.info("Defining pipelines...")
        
        # Full deployment pipeline
        self.pipeline_executor.define_pipeline("full_deployment", [
            "setup_workflow",
            "docker_workflow",
            "testing_workflow",
            "monitoring_workflow",
        ])
        
        # Quick validation pipeline
        self.pipeline_executor.define_pipeline("quick_validation", [
            "testing_workflow",
        ])
        
        logger.info("2 pipelines defined")

    def execute_full_deployment(self) -> Dict:
        """Execute complete deployment pipeline."""
        logger.info("=" * 60)
        logger.info("STARTING FULL DEPLOYMENT PIPELINE")
        logger.info("=" * 60)
        
        result = self.pipeline_executor.execute_pipeline("full_deployment")
        
        logger.info("=" * 60)
        logger.info(f"DEPLOYMENT {'SUCCEEDED' if result['success'] else 'FAILED'}")
        logger.info("=" * 60)
        
        return result

    def execute_quick_validation(self) -> Dict:
        """Execute quick validation pipeline."""
        logger.info("Starting quick validation...")
        return self.pipeline_executor.execute_pipeline("quick_validation")

    def get_status(self) -> Dict:
        """Get complete platform status."""
        return {
            "services": {
                "environment": self.env_service.health_check().__dict__,
                "docker": self.docker_service.health_check().__dict__,
                "api": self.api_service.health_check().__dict__,
            },
            "agents": {
                "setup": self.setup_agent.get_status(),
                "validation": self.validation_agent.get_status(),
                "docker": self.docker_agent.get_status(),
                "inference": self.inference_agent.get_status(),
                "monitoring": self.monitoring_agent.get_status(),
            },
            "execution_history": [
                {
                    "workflow": result.workflow_name,
                    "success": result.success,
                    "duration": result.total_duration,
                }
                for result in self.orchestrator.get_execution_history()
            ]
        }

    def save_report(self, filepath: str) -> bool:
        """Save platform report to file."""
        try:
            report = {
                "platform": "WarehouseEnvPlatform",
                "repo": self.repo_path,
                "status": self.get_status(),
                "execution_history": self.orchestrator.get_execution_history(),
            }
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Report saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return False


def main():
    """Main entry point."""
    import sys
    
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Initialize platform
    platform = WarehouseEnvPlatform(repo_path)
    
    # Execute full deployment
    result = platform.execute_full_deployment()
    
    # Save report
    platform.save_report(f"{repo_path}/deployment_report.json")
    
    # Print status
    print("\n" + "=" * 60)
    print("FINAL PLATFORM STATUS")
    print("=" * 60)
    status = platform.get_status()
    print(json.dumps(status, indent=2, default=str))
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    exit(main())
