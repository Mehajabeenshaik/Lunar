"""Task graders for warehouse environment."""

from typing import Dict, List
from warehouse_env.models import State, Observation
import numpy as np


class TaskGrader:
    """Base grader for tasks."""
    
    def grade(self, final_state: State, episode_rewards: List[float]) -> Dict[str, float]:
        """Grade episode performance.
        
        Returns:
            Dict with 'score' (0-1), 'service_level', 'cost_efficiency'
        """
        raise NotImplementedError


class EasyTaskGrader(TaskGrader):
    """Grader for single-warehouse easy task."""
    
    def grade(self, final_state: State, episode_rewards: List[float]) -> Dict[str, float]:
        """Grade easy task: single warehouse, fixed demand.
        
        Criteria:
        - Maintain 95% service level
        - Minimize holding costs
        - Reward consistency
        """
        avg_reward = np.mean(episode_rewards) if episode_rewards else 0.0
        
        # Simple service level proxy: inverse of shortage penalty
        max_penalty = 1000.0
        shortage_ratio = final_state.shortage_penalty / max_penalty
        service_score = max(0.0, 1.0 - shortage_ratio)
        
        # Cost efficiency
        total_cost = final_state.holding_costs + final_state.shortage_penalty / 10.0
        cost_efficiency = max(0.0, 1.0 - (total_cost / 5000.0))
        
        # Reward consistency (penalize high variance)
        if len(episode_rewards) > 1:
            reward_consistency = 1.0 - min(1.0, np.std(episode_rewards) / (np.mean(episode_rewards) + 1e-6))
        else:
            reward_consistency = 0.5
        
        # Composite score
        score = 0.5 * avg_reward + 0.25 * service_score + 0.25 * cost_efficiency
        
        return {
            "score": float(np.clip(score, 0.0, 1.0)),
            "avg_reward": float(avg_reward),
            "service_score": float(service_score),
            "cost_efficiency": float(cost_efficiency),
            "reward_consistency": float(reward_consistency),
        }


class MediumTaskGrader(TaskGrader):
    """Grader for 3-warehouse medium task."""
    
    def grade(self, final_state: State, episode_rewards: List[float]) -> Dict[str, float]:
        """Grade medium task: 3 warehouses, variable demand, transfers.
        
        Criteria:
        - Maintain 90% service level
        - Optimize transfer costs
        - Handle demand variability
        """
        avg_reward = np.mean(episode_rewards) if episode_rewards else 0.0
        
        # Service level from shortage penalty
        shortage_ratio = final_state.shortage_penalty / 2000.0
        service_score = max(0.0, 1.0 - shortage_ratio)
        
        # Cost efficiency (transfers + holding)
        total_cost = final_state.holding_costs + final_state.shortage_penalty / 10.0
        cost_efficiency = max(0.0, 1.0 - (total_cost / 10000.0))
        
        # Reward consistency
        if len(episode_rewards) > 1:
            reward_consistency = 1.0 - min(1.0, np.std(episode_rewards) / (np.mean(episode_rewards) + 1e-6))
        else:
            reward_consistency = 0.5
        
        # Network efficiency: reward balanced inventory
        inventory_balance = 1.0 - np.std(final_state.warehouse_levels) / (np.mean(final_state.warehouse_levels) + 1e-6)
        
        # Composite score
        score = (0.4 * avg_reward + 
                 0.25 * service_score + 
                 0.2 * cost_efficiency + 
                 0.15 * inventory_balance)
        
        return {
            "score": float(np.clip(score, 0.0, 1.0)),
            "avg_reward": float(avg_reward),
            "service_score": float(service_score),
            "cost_efficiency": float(cost_efficiency),
            "inventory_balance": float(inventory_balance),
        }


class HardTaskGrader(TaskGrader):
    """Grader for 5-warehouse hard task."""
    
    def grade(self, final_state: State, episode_rewards: List[float]) -> Dict[str, float]:
        """Grade hard task: 5 warehouses, seasonal demand, constraints.
        
        Criteria:
        - Maintain 85% service level
        - Complex multi-warehouse optimization
        - Handle seasonal spikes
        - Respect capacity constraints
        """
        avg_reward = np.mean(episode_rewards) if episode_rewards else 0.0
        
        # Service level from shortage penalty
        shortage_ratio = final_state.shortage_penalty / 3000.0
        service_score = max(0.0, 1.0 - shortage_ratio)
        
        # Cost efficiency (high bar for hard task)
        total_cost = final_state.holding_costs + final_state.shortage_penalty / 10.0
        cost_efficiency = max(0.0, 1.0 - (total_cost / 15000.0))
        
        # Reward consistency
        if len(episode_rewards) > 1:
            reward_consistency = 1.0 - min(1.0, np.std(episode_rewards) / (np.mean(episode_rewards) + 1e-6))
        else:
            reward_consistency = 0.5
        
        # Network efficiency: reward balanced inventory
        if len(final_state.warehouse_levels) > 0:
            inventory_std = np.std(final_state.warehouse_levels)
            inventory_mean = np.mean(final_state.warehouse_levels) + 1e-6
            network_efficiency = max(0.0, 1.0 - (inventory_std / inventory_mean) / 2.0)
        else:
            network_efficiency = 0.5
        
        # Capacity utilization (penalize over-capacity)
        over_capacity = sum(max(0, x - 1000.0) for x in final_state.warehouse_levels)
        capacity_score = max(0.0, 1.0 - (over_capacity / 5000.0))
        
        # Composite score (hard task weighted differently)
        score = (0.35 * avg_reward + 
                 0.25 * service_score + 
                 0.15 * cost_efficiency + 
                 0.15 * network_efficiency +
                 0.10 * capacity_score)
        
        return {
            "score": float(np.clip(score, 0.0, 1.0)),
            "avg_reward": float(avg_reward),
            "service_score": float(service_score),
            "cost_efficiency": float(cost_efficiency),
            "network_efficiency": float(network_efficiency),
            "capacity_score": float(capacity_score),
        }


def get_grader(task_name: str) -> TaskGrader:
    """Get appropriate grader for task."""
    if task_name == "warehouse_easy":
        return EasyTaskGrader()
    elif task_name == "warehouse_medium":
        return MediumTaskGrader()
    elif task_name == "warehouse_hard":
        return HardTaskGrader()
    else:
        raise ValueError(f"Unknown task: {task_name}")
