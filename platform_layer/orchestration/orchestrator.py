"""Orchestration Layer - Workflow and task orchestration."""

import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """Single step in a workflow."""
    name: str
    agent_type: str
    required: bool
    timeout: int


@dataclass
class WorkflowResult:
    """Result from workflow execution."""
    workflow_name: str
    success: bool
    total_duration: float
    steps_completed: int
    steps_total: int
    results: List[Dict]
    errors: List[str]


class Orchestrator:
    """Orchestrates workflow execution across agents."""

    def __init__(self):
        self.agents: Dict = {}
        self.workflows: Dict[str, List[WorkflowStep]] = {}
        self.execution_history: List[WorkflowResult] = []

    def register_agent(self, name: str, agent) -> None:
        """Register an agent."""
        self.agents[name] = agent
        logger.info(f"Agent registered: {name}")

    def define_workflow(self, name: str, steps: List[WorkflowStep]) -> None:
        """Define a workflow."""
        self.workflows[name] = steps
        logger.info(f"Workflow defined: {name} ({len(steps)} steps)")

    def execute_workflow(self, workflow_name: str) -> WorkflowResult:
        """Execute a complete workflow."""
        if workflow_name not in self.workflows:
            raise ValueError(f"Unknown workflow: {workflow_name}")

        steps = self.workflows[workflow_name]
        start_time = time.time()
        results = []
        errors = []
        steps_completed = 0

        logger.info(f"Starting workflow: {workflow_name}")

        for step in steps:
            try:
                if step.agent_type not in self.agents:
                    error_msg = f"Agent not found: {step.agent_type}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    if step.required:
                        break
                    continue

                logger.info(f"Executing step: {step.name}")
                agent = self.agents[step.agent_type]
                
                # Execute agent
                result = agent.execute()
                results.append(asdict(result))
                
                logger.info(
                    f"Step completed: {step.name} "
                    f"({result.duration_seconds:.2f}s) - "
                    f"{'SUCCESS' if result.success else 'FAILED'}"
                )
                
                if result.success:
                    steps_completed += 1
                elif step.required:
                    error_msg = f"Required step failed: {step.name} - {result.status_message}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    break

            except Exception as e:
                error_msg = f"Step execution error: {step.name} - {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                if step.required:
                    break

        total_duration = time.time() - start_time
        success = len(errors) == 0 and steps_completed == len(steps)

        workflow_result = WorkflowResult(
            workflow_name=workflow_name,
            success=success,
            total_duration=total_duration,
            steps_completed=steps_completed,
            steps_total=len(steps),
            results=results,
            errors=errors,
        )

        self.execution_history.append(workflow_result)
        logger.info(
            f"Workflow completed: {workflow_name} - "
            f"{'SUCCESS' if success else 'FAILED'} "
            f"({total_duration:.2f}s)"
        )

        return workflow_result

    def get_execution_history(self) -> List[WorkflowResult]:
        """Get all workflow execution history."""
        return self.execution_history

    def get_last_result(self, workflow_name: str) -> Optional[WorkflowResult]:
        """Get last execution result for workflow."""
        matching = [r for r in self.execution_history if r.workflow_name == workflow_name]
        return matching[-1] if matching else None


class PipelineExecutor:
    """Executes sequential pipelines with dependency management."""

    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator
        self.pipelines: Dict[str, List[str]] = {}

    def define_pipeline(self, name: str, workflow_sequence: List[str]) -> None:
        """Define a pipeline of workflows."""
        self.pipelines[name] = workflow_sequence
        logger.info(f"Pipeline defined: {name}")

    def execute_pipeline(self, pipeline_name: str) -> Dict:
        """Execute complete pipeline."""
        if pipeline_name not in self.pipelines:
            raise ValueError(f"Unknown pipeline: {pipeline_name}")

        workflow_sequence = self.pipelines[pipeline_name]
        start_time = time.time()
        results = {}
        failed_at = None

        logger.info(f"Starting pipeline: {pipeline_name}")

        for workflow_name in workflow_sequence:
            try:
                logger.info(f"Executing workflow: {workflow_name}")
                result = self.orchestrator.execute_workflow(workflow_name)
                results[workflow_name] = asdict(result)

                if not result.success:
                    failed_at = workflow_name
                    logger.error(f"Pipeline halted at workflow: {workflow_name}")
                    break

            except Exception as e:
                failed_at = workflow_name
                logger.error(f"Pipeline execution error at {workflow_name}: {e}")
                results[workflow_name] = {
                    "error": str(e),
                    "success": False
                }
                break

        total_duration = time.time() - start_time
        success = failed_at is None

        pipeline_result = {
            "pipeline_name": pipeline_name,
            "success": success,
            "total_duration": total_duration,
            "workflows_executed": len(results),
            "workflows_total": len(workflow_sequence),
            "failed_at": failed_at,
            "results": results,
        }

        logger.info(
            f"Pipeline completed: {pipeline_name} - "
            f"{'SUCCESS' if success else 'FAILED'} "
            f"({total_duration:.2f}s)"
        )

        return pipeline_result
