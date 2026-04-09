"""
Comprehensive graders for all 31 tasks across 5 domains
Deterministic reward calculation for warehouse, data pipeline, code review,
resource allocation, and system optimization domains
"""

import hashlib
import numpy as np
from typing import Dict, Any, List


class ComprehensiveGrader:
    """Base grader for all 31 tasks with domain-specific logic."""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.domain = self._extract_domain(task_id)

    def _extract_domain(self, task_id: str) -> str:
        """Extract domain from task_id."""
        if task_id.startswith("warehouse_"):
            return "warehouse"
        elif task_id.startswith("data_"):
            return "data_pipeline"
        elif task_id.startswith("code_"):
            return "code_review"
        elif task_id.startswith("resource_"):
            return "resource_allocation"
        elif task_id.startswith("optimization_"):
            return "system_optimization"
        return "unknown"

    def _deterministic_hash(self, value: Any) -> float:
        """Generate deterministic score using hash."""
        h = hashlib.sha256(str(value).encode()).hexdigest()
        return float(int(h[:8], 16)) % 1000 / 1000

    def grade(self, state: Any, episode_rewards: List[float]) -> Dict[str, float]:
        """Grade task based on domain."""
        if self.domain == "warehouse":
            return self._grade_warehouse(state, episode_rewards)
        elif self.domain == "data_pipeline":
            return self._grade_data_pipeline(state, episode_rewards)
        elif self.domain == "code_review":
            return self._grade_code_review(state, episode_rewards)
        elif self.domain == "resource_allocation":
            return self._grade_resource_allocation(state, episode_rewards)
        elif self.domain == "system_optimization":
            return self._grade_system_optimization(state, episode_rewards)
        else:
            return {"score": 0.5}

    def _grade_warehouse(self, state: Any, episode_rewards: List[float]) -> Dict[str, float]:
        """Grade warehouse tasks based on inventory management."""
        if not episode_rewards or len(episode_rewards) == 0:
            return {"score": 0.2}

        # Average reward from episode
        avg_reward = np.mean(episode_rewards)

        # Normalize to [0, 1]
        score = max(0.0, min(1.0, avg_reward))

        # Ensure minimum positive reward
        score = max(0.15, score)

        return {"score": max(0.20, min(0.95, score))}

    def _grade_data_pipeline(self, state: Any, episode_rewards: List[float]) -> Dict[str, float]:
        """Grade data pipeline tasks based on processing efficiency."""
        if not episode_rewards or len(episode_rewards) == 0:
            return {"score": 0.25}

        # Data pipeline score based on quality metrics
        avg_reward = np.mean(episode_rewards)
        quality_factor = 0.7 + (0.3 * min(1.0, avg_reward))

        score = max(0.20, min(0.95, quality_factor))

        return {"score": score}

    def _grade_code_review(self, state: Any, episode_rewards: List[float]) -> Dict[str, float]:
        """Grade code review tasks based on quality improvements."""
        if not episode_rewards or len(episode_rewards) == 0:
            return {"score": 0.3}

        # Code review score reflects quality improvement
        episode_count = len(episode_rewards)
        base_score = 0.6 + (0.35 * min(1.0, np.mean(episode_rewards)))

        score = max(0.20, min(0.95, base_score))

        return {"score": score}

    def _grade_resource_allocation(self, state: Any, episode_rewards: List[float]) -> Dict[str, float]:
        """Grade resource allocation tasks based on optimization."""
        if not episode_rewards or len(episode_rewards) == 0:
            return {"score": 0.35}

        # Resource allocation score based on allocation efficiency
        avg_reward = np.mean(episode_rewards)
        optimization_score = 0.65 + (0.3 * min(1.0, avg_reward))

        score = max(0.20, min(0.95, optimization_score))

        return {"score": score}

    def _grade_system_optimization(self, state: Any, episode_rewards: List[float]) -> Dict[str, float]:
        """Grade system optimization tasks based on performance."""
        if not episode_rewards or len(episode_rewards) == 0:
            return {"score": 0.4}

        # System optimization score based on performance improvements
        avg_reward = np.mean(episode_rewards)
        performance_score = 0.70 + (0.25 * min(1.0, avg_reward))

        score = max(0.20, min(0.95, performance_score))

        return {"score": score}


# Task-specific graders
class WarehouseNoviceGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("warehouse_novice")


class WarehouseEasyGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("warehouse_easy")


class WarehouseMediumGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("warehouse_medium")


class WarehouseIntermediateGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("warehouse_intermediate")


class WarehouseHardGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("warehouse_hard")


class WarehouseExtremeGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("warehouse_extreme")


class DataIngestionSimpleGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("data_ingestion_simple")


class DataIngestionComplexGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("data_ingestion_complex")


class DataCleaningBasicGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("data_cleaning_basic")


class DataCleaningAdvancedGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("data_cleaning_advanced")


class DataValidationSchemaGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("data_validation_schema")


class DataValidationQualityGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("data_validation_quality")


class DataTransformationETLGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("data_transformation_etl")


class DataExportFormatGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("data_export_format")


class CodeStyleComplianceGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("code_style_compliance")


class CodePerformanceOptimizationGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("code_performance_optimization")


class CodeSecurityVulnerabilitiesGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("code_security_vulnerabilities")


class CodeMaintainabilityMetricsGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("code_maintainability_metrics")


class CodeRefactoringSimpleGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("code_refactoring_simple")


class CodeRefactoringComplexGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("code_refactoring_complex")


class CodeTestingCoverageGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("code_testing_coverage")


class CodeIntegrationTestingGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("code_integration_testing")


class ResourceBudgetSimpleGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("resource_budget_simple")


class ResourceBudgetComplexGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("resource_budget_complex")


class ResourceSchedulingTasksGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("resource_scheduling_tasks")


class ResourceSchedulingTeamsGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("resource_scheduling_teams")


class ResourceCapacityPlanningGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("resource_capacity_planning")


class OptimizationQueryBasicGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("optimization_query_basic")


class OptimizationQueryAdvancedGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("optimization_query_advanced")


class OptimizationMemoryUsageGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("optimization_memory_usage")


class OptimizationThroughputGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("optimization_throughput")


class OptimizationLatencyGrader(ComprehensiveGrader):
    def __init__(self):
        super().__init__("optimization_latency")


# Grader registry mapping task_id to grader class
GRADER_REGISTRY = {
    "warehouse_novice": WarehouseNoviceGrader,
    "warehouse_easy": WarehouseEasyGrader,
    "warehouse_medium": WarehouseMediumGrader,
    "warehouse_intermediate": WarehouseIntermediateGrader,
    "warehouse_hard": WarehouseHardGrader,
    "warehouse_extreme": WarehouseExtremeGrader,
    "data_ingestion_simple": DataIngestionSimpleGrader,
    "data_ingestion_complex": DataIngestionComplexGrader,
    "data_cleaning_basic": DataCleaningBasicGrader,
    "data_cleaning_advanced": DataCleaningAdvancedGrader,
    "data_validation_schema": DataValidationSchemaGrader,
    "data_validation_quality": DataValidationQualityGrader,
    "data_transformation_etl": DataTransformationETLGrader,
    "data_export_format": DataExportFormatGrader,
    "code_style_compliance": CodeStyleComplianceGrader,
    "code_performance_optimization": CodePerformanceOptimizationGrader,
    "code_security_vulnerabilities": CodeSecurityVulnerabilitiesGrader,
    "code_maintainability_metrics": CodeMaintainabilityMetricsGrader,
    "code_refactoring_simple": CodeRefactoringSimpleGrader,
    "code_refactoring_complex": CodeRefactoringComplexGrader,
    "code_testing_coverage": CodeTestingCoverageGrader,
    "code_integration_testing": CodeIntegrationTestingGrader,
    "resource_budget_simple": ResourceBudgetSimpleGrader,
    "resource_budget_complex": ResourceBudgetComplexGrader,
    "resource_scheduling_tasks": ResourceSchedulingTasksGrader,
    "resource_scheduling_teams": ResourceSchedulingTeamsGrader,
    "resource_capacity_planning": ResourceCapacityPlanningGrader,
    "optimization_query_basic": OptimizationQueryBasicGrader,
    "optimization_query_advanced": OptimizationQueryAdvancedGrader,
    "optimization_memory_usage": OptimizationMemoryUsageGrader,
    "optimization_throughput": OptimizationThroughputGrader,
    "optimization_latency": OptimizationLatencyGrader,
}


def get_grader_for_task(task_id: str) -> ComprehensiveGrader:
    """Get grader instance for a specific task."""
    if task_id not in GRADER_REGISTRY:
        raise ValueError(f"Unknown task: {task_id}")
    return GRADER_REGISTRY[task_id]()
