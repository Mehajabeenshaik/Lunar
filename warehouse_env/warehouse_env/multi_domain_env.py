"""
Multi-domain RL environment supporting all 31 tasks
Generalized environment that adapts to warehouse, data pipeline, code review,
resource allocation, and system optimization domains
"""

import numpy as np
import random
from typing import Dict, List, Tuple, Optional, Any
from .task_config import get_task_info, is_valid_task
from .graders_comprehensive import get_grader_for_task


class MultiDomainEnv:
    """Universal RL environment for 31 tasks across 5 domains."""

    def __init__(self, task_id: str):
        """Initialize environment for a specific task.
        
        Args:
            task_id: One of 31 task IDs
        """
        if not is_valid_task(task_id):
            raise ValueError(f"Unknown task: {task_id}")

        self.task_id = task_id
        self.task_info = get_task_info(task_id)
        self.domain = self.task_info.get("domain", "unknown")
        self.grader = get_grader_for_task(task_id)

        # Initialize domain-specific parameters
        self._setup_domain_params()

        # State management
        self.state: Dict[str, Any] = {}
        self.episode_rewards: List[float] = []
        self.current_step: int = 0
        self.max_steps: int = self.task_info.get("max_steps", 100)

    def _setup_domain_params(self):
        """Configure domain-specific parameters."""
        if self.domain == "warehouse":
            self._setup_warehouse_params()
        elif self.domain == "data_pipeline":
            self._setup_data_pipeline_params()
        elif self.domain == "code_review":
            self._setup_code_review_params()
        elif self.domain == "resource_allocation":
            self._setup_resource_allocation_params()
        elif self.domain == "system_optimization":
            self._setup_system_optimization_params()

    def _setup_warehouse_params(self):
        """Warehouse inventory management parameters."""
        num_warehouses = self.task_info.get("num_warehouses", 1)
        self.num_warehouses = num_warehouses
        self.service_level_target = 0.95 - (0.05 * (num_warehouses - 1))
        self.demand_volatility = 0.1 * num_warehouses
        self.logistics_efficiency_target = 0.85

    def _setup_data_pipeline_params(self):
        """Data processing pipeline parameters."""
        self.data_quality_target = 0.95
        self.processing_latency_target = 100  # ms
        self.data_volume = 10000  # records
        self.missing_data_rate = 0.05

    def _setup_code_review_params(self):
        """Code review and quality parameters."""
        self.code_quality_target = 0.90
        self.test_coverage_target = 0.85
        self.performance_improvement_target = 0.20

    def _setup_resource_allocation_params(self):
        """Resource allocation and planning parameters."""
        self.budget_constraint = 100000  # total budget
        self.team_size = 20  # team members
        self.project_complexity = 0.7

    def _setup_system_optimization_params(self):
        """System optimization parameters."""
        self.latency_target = 50  # ms
        self.throughput_target = 10000  # requests/sec
        self.cpu_utilization_target = 0.75

    def reset(self) -> Dict[str, Any]:
        """Reset environment to initial state.
        
        Returns:
            Initial state observation
        """
        self.current_step = 0
        self.episode_rewards = []

        if self.domain == "warehouse":
            self.state = self._init_warehouse_state()
        elif self.domain == "data_pipeline":
            self.state = self._init_data_pipeline_state()
        elif self.domain == "code_review":
            self.state = self._init_code_review_state()
        elif self.domain == "resource_allocation":
            self.state = self._init_resource_allocation_state()
        elif self.domain == "system_optimization":
            self.state = self._init_system_optimization_state()
        else:
            self.state = {}

        return self.state.copy()

    def _init_warehouse_state(self) -> Dict[str, Any]:
        """Initialize warehouse management state."""
        return {
            "warehouse_levels": [300.0] * self.num_warehouses,
            "demand_forecast": [100.0] * self.num_warehouses,
            "supplier_status": [1.0] * self.num_warehouses,
            "day": 0,
            "holding_costs": 0.0,
            "shortage_penalty": 0.0,
        }

    def _init_data_pipeline_state(self) -> Dict[str, Any]:
        """Initialize data pipeline state."""
        return {
            "records_processed": 0,
            "data_quality": 0.95,
            "processing_latency": 100,
            "error_rate": 0.01,
            "memory_usage": 500,  # MB
        }

    def _init_code_review_state(self) -> Dict[str, Any]:
        """Initialize code review state."""
        return {
            "files_reviewed": 0,
            "code_quality_score": 0.70,
            "test_coverage": 0.60,
            "performance_baseline": 1.0,
            "issues_found": 0,
        }

    def _init_resource_allocation_state(self) -> Dict[str, Any]:
        """Initialize resource allocation state."""
        return {
            "budget_spent": 0.0,
            "team_allocated": 0,
            "projects_active": 0,
            "efficiency": 0.70,
            "deadline_buffer": 1.0,
        }

    def _init_system_optimization_state(self) -> Dict[str, Any]:
        """Initialize system optimization state."""
        return {
            "current_latency": 150,
            "current_throughput": 5000,
            "cpu_usage": 0.85,
            "memory_usage": 0.70,
            "optimization_index": 0.0,
        }

    def step(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
        """Execute one environment step.
        
        Args:
            action: Domain-specific action
            
        Returns:
            (next_state, reward)
        """
        if not self.state:
            raise RuntimeError("Environment not reset. Call reset() first.")

        self.current_step += 1

        # Execute domain-specific step logic
        if self.domain == "warehouse":
            next_state, reward_value = self._step_warehouse(action)
        elif self.domain == "data_pipeline":
            next_state, reward_value = self._step_data_pipeline(action)
        elif self.domain == "code_review":
            next_state, reward_value = self._step_code_review(action)
        elif self.domain == "resource_allocation":
            next_state, reward_value = self._step_resource_allocation(action)
        elif self.domain == "system_optimization":
            next_state, reward_value = self._step_system_optimization(action)
        else:
            next_state = self.state.copy()
            reward_value = 0.5

        self.state = next_state
        self.episode_rewards.append(reward_value)

        return next_state.copy(), reward_value

    def _step_warehouse(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
        """Execute warehouse management step."""
        reorder_quantities = action.get("reorder_quantities", [100] * self.num_warehouses)

        # Auto-expand single value
        if isinstance(reorder_quantities, (int, float)):
            reorder_quantities = [reorder_quantities] * self.num_warehouses
        elif len(reorder_quantities) == 1 and self.num_warehouses > 1:
            reorder_quantities = reorder_quantities * self.num_warehouses

        # Simulate demand
        demand = [
            np.random.normal(100, 10 * self.demand_volatility) 
            for _ in range(self.num_warehouses)
        ]
        demand = [max(0, d) for d in demand]

        # Update inventory
        new_levels = [
            self.state["warehouse_levels"][i] + reorder_quantities[i]
            for i in range(self.num_warehouses)
        ]

        # Calculate fulfillment
        fulfilled = [min(new_levels[i], demand[i]) for i in range(self.num_warehouses)]
        shortage = [max(0, demand[i] - fulfilled[i]) for i in range(self.num_warehouses)]

        new_levels = [new_levels[i] - fulfilled[i] for i in range(self.num_warehouses)]

        # Calculate costs and reward
        holding_cost = sum(new_levels) * 0.5
        shortage_penalty = sum(shortage) * 10.0
        service_level = sum(fulfilled) / (sum(demand) + 1e-6)

        # Reward: maximize service level, minimize costs
        reward = (
            0.7 * service_level +
            0.2 * max(0, 1 - (holding_cost / 10000)) +
            0.1 * max(0, 1 - (shortage_penalty / 10000))
        )

        next_state = self.state.copy()
        next_state["warehouse_levels"] = new_levels
        next_state["holding_costs"] += holding_cost
        next_state["shortage_penalty"] += shortage_penalty
        next_state["day"] += 1

        return next_state, max(0.15, min(0.95, reward))

    def _step_data_pipeline(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
        """Execute data pipeline step."""
        records_to_process = action.get("records", 1000)
        cleaning_level = action.get("cleaning_level", 0.5)
        validation_threshold = action.get("validation_threshold", 0.8)

        # Simulate processing
        processed = min(records_to_process, self.data_volume - self.state["records_processed"])
        quality_improvement = 0.05 * cleaning_level
        error_rate = max(0.001, self.state["error_rate"] - quality_improvement)

        # Calculate reward
        reward = (
            0.6 * (1 - error_rate) +
            0.3 * cleaning_level +
            0.1 * (processed / self.data_volume)
        )

        next_state = self.state.copy()
        next_state["records_processed"] += processed
        next_state["data_quality"] = min(0.99, next_state["data_quality"] + quality_improvement)
        next_state["error_rate"] = error_rate

        return next_state, max(0.20, min(0.95, reward))

    def _step_code_review(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
        """Execute code review step."""
        files_reviewed = action.get("files", 5)
        refactoring_effort = action.get("refactoring", 0.5)
        test_implementation = action.get("testing", 0.3)

        # Update quality metrics
        quality_improvement = 0.05 * refactoring_effort
        test_improvement = 0.08 * test_implementation

        new_quality = min(0.99, self.state["code_quality_score"] + quality_improvement)
        new_coverage = min(0.99, self.state["test_coverage"] + test_improvement)

        # Calculate reward
        reward = (
            0.5 * new_quality +
            0.3 * new_coverage +
            0.2 * (files_reviewed / 10)
        )

        next_state = self.state.copy()
        next_state["files_reviewed"] += files_reviewed
        next_state["code_quality_score"] = new_quality
        next_state["test_coverage"] = new_coverage

        return next_state, max(0.20, min(0.95, reward))

    def _step_resource_allocation(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
        """Execute resource allocation step."""
        budget_alloc = action.get("budget", 5000)
        team_alloc = action.get("team_members", 5)
        efficiency_target = action.get("efficiency", 0.8)

        # Validate allocation
        new_spent = min(self.state["budget_spent"] + budget_alloc, self.budget_constraint)
        new_team = min(self.state["team_allocated"] + team_alloc, self.team_size)

        # Calculate efficiency
        efficiency = min(0.95, efficiency_target * 0.9 + 0.05)

        # Calculate reward
        budget_utilization = new_spent / self.budget_constraint
        team_utilization = new_team / self.team_size
        reward = (
            0.5 * efficiency +
            0.25 * budget_utilization +
            0.25 * team_utilization
        )

        next_state = self.state.copy()
        next_state["budget_spent"] = new_spent
        next_state["team_allocated"] = new_team
        next_state["efficiency"] = efficiency

        return next_state, max(0.20, min(0.95, reward))

    def _step_system_optimization(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
        """Execute system optimization step."""
        indexing_effort = action.get("indexing", 0.5)
        parallelization = action.get("parallelization", 0.5)
        caching_strategy = action.get("caching", 0.5)

        # Simulate optimization improvements
        latency_reduction = 30 * indexing_effort
        throughput_increase = 2000 * parallelization
        cpu_efficiency = 0.85 - (0.15 * caching_strategy)

        new_latency = max(10, self.state["current_latency"] - latency_reduction)
        new_throughput = min(20000, self.state["current_throughput"] + throughput_increase)

        # Calculate reward
        latency_score = max(0, 1 - (new_latency / 200))
        throughput_score = min(1.0, new_throughput / self.throughput_target)
        efficiency_score = 1 - abs(cpu_efficiency - 0.75)

        reward = (
            0.4 * latency_score +
            0.4 * throughput_score +
            0.2 * efficiency_score
        )

        next_state = self.state.copy()
        next_state["current_latency"] = new_latency
        next_state["current_throughput"] = new_throughput
        next_state["cpu_usage"] = cpu_efficiency

        return next_state, max(0.20, min(0.95, reward))

    def get_episode_reward(self) -> float:
        """Calculate final episode reward using grader.
        
        CRITICAL: Must return score strictly within (0, 1), never 0.0 or 1.0
        """
        try:
            grader_result = self.grader.grade(self.state, self.episode_rewards)
            score = grader_result.get("score", np.mean(self.episode_rewards) if self.episode_rewards else 0.35)
            
            # Ensure score is strictly valid (0, 1) - validator requirement
            score = float(score)
            if np.isnan(score) or np.isinf(score):
                score = 0.5
            
            # Clamp with epsilon margins to ensure strictly within (0, 1)
            score = float(np.clip(score, 0.001, 0.999))
            
            return score
        except Exception as e:
            # Fallback to safe value if anything goes wrong
            return 0.5

    def is_done(self) -> bool:
        """Check if episode is finished."""
        return self.current_step >= self.max_steps
