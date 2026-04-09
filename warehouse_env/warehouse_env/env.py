"""Warehouse Inventory Management RL Environment."""

import numpy as np
from typing import Optional, Tuple
import random

from .models import State, Action, Observation, Reward


class WarehouseEnv:
    """Warehouse inventory management environment."""
    
    def __init__(self, task: str = "warehouse_easy"):
        """Initialize environment.
        
        Args:
            task: One of 'warehouse_easy', 'warehouse_medium', 'warehouse_hard'
        """
        self.task = task
        self._setup_task_params()
        self.state: Optional[State] = None
        self.episode_rewards: list = []
        
    def _setup_task_params(self):
        """Configure task parameters."""
        if self.task == "warehouse_easy":
            self.num_warehouses = 1
            self.service_level_target = 0.95
            self.demand_volatility = 0.1
            self.episode_steps = 30
        elif self.task == "warehouse_medium":
            self.num_warehouses = 3
            self.service_level_target = 0.90
            self.demand_volatility = 0.2
            self.episode_steps = 60
        elif self.task == "warehouse_hard":
            self.num_warehouses = 5
            self.service_level_target = 0.85
            self.demand_volatility = 0.3
            self.episode_steps = 90
        else:
            raise ValueError(f"Unknown task: {self.task}")
    
    def reset(self) -> Observation:
        """Reset environment to initial state.
        
        Returns:
            Initial observation
        """
        self.state = State(
            warehouse_levels=[300.0] * self.num_warehouses,
            demand_forecast=[100.0] * self.num_warehouses,
            supplier_status=[1.0] * self.num_warehouses,
            day=0,
            holding_costs=0.0,
            shortage_penalty=0.0,
        )
        self.episode_rewards = []
        return Observation.from_state(self.state)
    
    def step(self, action: Action) -> Tuple[Observation, Reward]:
        """Execute one environment step.
        
        Args:
            action: Agent action
            
        Returns:
            (observation, reward)
        """
        if self.state is None:
            raise RuntimeError("Environment not reset. Call reset() first.")
        
        # Validate and normalize action
        reorder_quantities = list(action.reorder_quantities)
        
        # Auto-expand single value to all warehouses for convenience
        if len(reorder_quantities) == 1 and self.num_warehouses > 1:
            reorder_quantities = reorder_quantities * self.num_warehouses
        
        # Validate total count
        if len(reorder_quantities) != self.num_warehouses:
            error_msg = f"Expected {self.num_warehouses} reorder quantities, got {len(reorder_quantities)}"
            self.state.last_action_error = error_msg
            return Observation.from_state(self.state), Reward(value=0.0, info={"error": error_msg})
        
        # Simulate demand for current step
        demand = self._generate_demand()
        
        # Process reorders (with 2-day lead time, simplified to 1 in this version)
        new_levels = self.state.warehouse_levels.copy()
        for i in range(self.num_warehouses):
            new_levels[i] += reorder_quantities[i]
        
        # Process inter-warehouse transfers
        if len(action.transfers) == self.num_warehouses:
            for i in range(self.num_warehouses):
                if len(action.transfers[i]) == self.num_warehouses:
                    for j in range(self.num_warehouses):
                        if i != j and action.transfers[i][j] > 0:
                            transfer = min(action.transfers[i][j], new_levels[i])
                            new_levels[i] -= transfer
                            new_levels[j] += transfer
        
        # Calculate fulfillment and costs
        fulfilled = []
        shortage = []
        for i in range(self.num_warehouses):
            fill = min(new_levels[i], demand[i])
            fulfilled.append(fill)
            short = max(0, demand[i] - fill)
            shortage.append(short)
            new_levels[i] -= fill
        
        # Calculate costs
        holding_cost = sum(new_levels) * 0.5  # $0.50 per unit held
        shortage_penalty = sum(shortage) * 10.0  # $10 per unit short
        service_level = sum(fulfilled) / (sum(demand) + 1e-6)
        
        self.state.holding_costs += holding_cost
        self.state.shortage_penalty += shortage_penalty
        self.state.warehouse_levels = new_levels
        self.state.day += 1
        self.state.demand_forecast = self._generate_demand()
        self.state.last_action_error = None
        
        # Calculate reward
        reward_value = self._calculate_reward(service_level, holding_cost, shortage_penalty)
        
        done = self.state.day >= self.episode_steps
        
        self.episode_rewards.append(reward_value)
        
        return Observation.from_state(self.state), Reward(
            value=reward_value,
            done=done,
            info={
                "service_level": service_level,
                "holding_cost": holding_cost,
                "shortage_penalty": shortage_penalty,
                "day": self.state.day,
            }
        )
    
    def _generate_demand(self) -> list:
        """Generate stochastic demand."""
        base_demand = 100.0
        noise = np.random.normal(0, base_demand * self.demand_volatility, self.num_warehouses)
        demand = np.maximum(base_demand + noise, 10.0)
        return demand.tolist()
    
    def _calculate_reward(self, service_level: float, holding_cost: float, shortage_penalty: float) -> float:
        """Calculate reward based on service level and costs."""
        # Reward for meeting service level target
        service_reward = max(0, min(1.0, service_level / self.service_level_target))
        
        # Penalize costs
        max_possible_cost = 1000.0
        cost_penalty = (holding_cost + shortage_penalty) / max_possible_cost
        
        # Combined reward: 0.8 * service + 0.2 * (1 - normalized_cost)
        reward = 0.8 * service_reward + 0.2 * max(0, 1.0 - cost_penalty)
        
        return float(np.clip(reward, 0.0, 1.0))
    
    def state_dict(self) -> dict:
        """Get current state as dict."""
        if self.state is None:
            return {}
        return self.state.model_dump()
    
    def render(self) -> str:
        """Render environment state as text."""
        if self.state is None:
            return "Environment not initialized"
        
        lines = [
            f"=== Warehouse Environment (Task: {self.task}) ===",
            f"Day: {self.state.day}/{self.episode_steps}",
            f"Warehouses: {self.num_warehouses}",
            f"Inventory Levels: {[f'{x:.1f}' for x in self.state.warehouse_levels]}",
            f"Demand Forecast: {[f'{x:.1f}' for x in self.state.demand_forecast]}",
            f"Holding Costs: ${self.state.holding_costs:.2f}",
            f"Shortage Penalty: ${self.state.shortage_penalty:.2f}",
            f"Episode Rewards: {[f'{x:.3f}' for x in self.episode_rewards[-5:]]}",
        ]
        return "\n".join(lines)
