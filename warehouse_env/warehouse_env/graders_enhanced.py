"""Enhanced task graders with 0.1-1.0 partial credit scale."""

from typing import Dict, List, Tuple
from warehouse_env.models import State
import numpy as np


class EnhancedGrader:
    """Base enhanced grader with 0.1-1.0 never-binary reward scale."""
    
    def _clip_score(self, score: float) -> float:
        """Ensure score is always in [0.1, 1.0] range (never zero or binary)."""
        return max(0.1, min(1.0, score))
    
    def _get_feedback(self, score: float, metrics: Dict) -> str:
        """Generate human-readable feedback based on score and metrics."""
        if score >= 0.95:
            return "Excellent: Near-optimal performance across all metrics"
        elif score >= 0.85:
            return "Very Good: Strong optimization with minor inefficiencies"
        elif score >= 0.70:
            return "Good: Solid approach with some optimization opportunities"
        elif score >= 0.50:
            return "Adequate: Basic competence, room for improvement"
        elif score >= 0.30:
            return "Partial: Demonstrates understanding but needs refinement"
        else:
            return "Initial: Demonstrates some progress, significant improvements possible"
    
    def grade(self, final_state: State, episode_rewards: List[float], task_params: Dict = None) -> Dict:
        """Grade episode performance.
        
        Returns:
            Dict with 'score' (0.1-1.0, never binary), 'feedback', and domain metrics
        """
        raise NotImplementedError


class WarehouseGrader(EnhancedGrader):
    """Enhanced grader for warehouse management domain."""
    
    def grade(self, final_state: State, episode_rewards: List[float], task_params: Dict = None) -> Dict:
        """Grade warehouse task with detailed partial credit."""
        task_params = task_params or {}
        num_warehouses = task_params.get('num_warehouses', 1)
        
        # === METRIC 1: Service Level (Demand Fulfillment) ===
        max_penalty_threshold = num_warehouses * 3000.0
        shortage_ratio = min(1.0, final_state.shortage_penalty / max_penalty_threshold)
        service_score = 1.0 - (shortage_ratio * 0.6)  # Service worth 0.4-1.0
        service_score = max(0.1, service_score)
        
        # === METRIC 2: Cost Efficiency ===
        total_cost = final_state.holding_costs + (final_state.shortage_penalty / 10.0)
        max_acceptable_cost = 15000.0 * num_warehouses
        cost_ratio = min(1.0, total_cost / max_acceptable_cost)
        cost_efficiency = 1.0 - (cost_ratio * 0.5)  # Cost efficiency worth 0.5-1.0
        cost_efficiency = max(0.1, cost_efficiency)
        
        # === METRIC 3: Reward Consistency ===
        if len(episode_rewards) > 1:
            mean_reward = np.mean(episode_rewards)
            std_reward = np.std(episode_rewards)
            consistency = 1.0 - min(0.4, (std_reward / (mean_reward + 1e-6)))
        else:
            consistency = 0.5
        consistency = max(0.1, consistency)
        
        # === METRIC 4: Network Efficiency (for multi-warehouse) ===
        if num_warehouses > 1 and len(final_state.warehouse_levels) > 1:
            mean_level = np.mean(final_state.warehouse_levels)
            std_level = np.std(final_state.warehouse_levels)
            balance_ratio = std_level / (mean_level + 1e-6)
            network_efficiency = 1.0 - min(0.3, balance_ratio * 0.15)
        else:
            network_efficiency = 0.7
        network_efficiency = max(0.1, network_efficiency)
        
        # === COMPOSITE SCORE with weighted average ===
        # Warehouse: 40% service, 30% cost, 20% consistency, 10% network
        score = (0.40 * service_score + 
                 0.30 * cost_efficiency + 
                 0.20 * consistency +
                 0.10 * network_efficiency)
        
        score = self._clip_score(score)
        
        return {
            "score": float(score),
            "feedback": self._get_feedback(score, {}),
            "service_level": float(self._clip_score(service_score)),
            "cost_efficiency": float(self._clip_score(cost_efficiency)),
            "consistency": float(self._clip_score(consistency)),
            "network_efficiency": float(self._clip_score(network_efficiency)),
            "total_cost": float(total_cost),
            "shortage_penalty": float(final_state.shortage_penalty),
        }


class SupplyChainGrader(EnhancedGrader):
    """Enhanced grader for supply chain domain."""
    
    def grade(self, final_state: State, episode_rewards: List[float], task_params: Dict = None) -> Dict:
        """Grade supply chain task with multi-tier optimization reward."""
        task_params = task_params or {}
        num_tiers = task_params.get('num_tiers', 2)
        
        # === METRIC 1: Network Resilience ===
        avg_reward = np.mean(episode_rewards) if episode_rewards else 0.1
        avg_reward = max(0.1, min(1.0, avg_reward))
        resilience = 0.6 + (0.4 * avg_reward)  # 0.6-1.0 range
        resilience = max(0.1, resilience)
        
        # === METRIC 2: Cost Minimization ===
        total_cost = final_state.holding_costs + (final_state.shortage_penalty / 10.0)
        cost_threshold = 20000.0 * num_tiers
        cost_ratio = min(1.0, total_cost / cost_threshold)
        cost_optimization = 1.0 - (cost_ratio * 0.7)  # 0.3-1.0 range
        cost_optimization = max(0.1, cost_optimization)
        
        # === METRIC 3: Demand Fulfillment ===
        shortage_ratio = final_state.shortage_penalty / (5000.0 * num_tiers)
        demand_fulfillment = max(0.1, 1.0 - (shortage_ratio * 0.5))  # 0.5-1.0
        
        # === METRIC 4: Supplier Coordination ===
        if len(episode_rewards) > 1:
            reward_stability = 1.0 - min(0.3, np.std(episode_rewards) / (np.mean(episode_rewards) + 1e-6))
        else:
            reward_stability = 0.6
        coordination = max(0.1, 0.5 + (0.5 * reward_stability))
        
        # === COMPOSITE SCORE ===
        # Supply Chain: 30% resilience, 30% cost, 25% fulfillment, 15% coordination
        score = (0.30 * resilience +
                 0.30 * cost_optimization +
                 0.25 * demand_fulfillment +
                 0.15 * coordination)
        
        score = self._clip_score(score)
        
        return {
            "score": float(score),
            "feedback": self._get_feedback(score, {}),
            "resilience": float(self._clip_score(resilience)),
            "cost_optimization": float(self._clip_score(cost_optimization)),
            "demand_fulfillment": float(self._clip_score(demand_fulfillment)),
            "coordination": float(self._clip_score(coordination)),
            "network_tiers": num_tiers,
        }


class ForecastingGrader(EnhancedGrader):
    """Enhanced grader for demand forecasting domain."""
    
    def grade(self, final_state: State, episode_rewards: List[float], task_params: Dict = None) -> Dict:
        """Grade forecasting task with accuracy and adaptability reward."""
        task_params = task_params or {}
        pattern = task_params.get('pattern', 'stationary')
        
        # === METRIC 1: Prediction Accuracy ===
        if len(episode_rewards) > 2:
            # Lower variance in rewards = better predictions
            reward_std = np.std(episode_rewards)
            reward_mean = np.mean(episode_rewards)
            accuracy = max(0.1, 1.0 - min(0.6, (reward_std / (reward_mean + 1e-6)) * 0.3))
        else:
            accuracy = np.mean(episode_rewards) if episode_rewards else 0.1
        accuracy = self._clip_score(accuracy)
        
        # === METRIC 2: Adaptability to Pattern ===
        patterns_difficulty = {
            'stationary': 0.2,      # Easy to adapt
            'noisy_stationary': 0.3,
            'seasonal': 0.4,
            'trend': 0.5,
            'hybrid': 0.6,
            'chaotic': 0.8,         # Hard to adapt
        }
        base_difficulty = patterns_difficulty.get(pattern, 0.5)
        # More difficult patterns = higher credit for adaptation
        adaptability = 0.3 + (0.7 * (1.0 - base_difficulty))
        adaptability = max(0.1, adaptability)
        
        # === METRIC 3: Forecast Consistency ===
        if len(episode_rewards) > 1:
            consistency_penalty = np.std(episode_rewards) / (np.mean(np.abs(episode_rewards)) + 1e-6)
            consistency = max(0.1, 1.0 - min(0.5, consistency_penalty * 0.2))
        else:
            consistency = 0.5
        consistency = max(0.1, consistency)
        
        # === METRIC 4: Error Recovery ===
        if len(episode_rewards) > 3:
            # Check if rewards improve over time (error recovery)
            early_rewards = np.mean(episode_rewards[:len(episode_rewards)//2])
            late_rewards = np.mean(episode_rewards[len(episode_rewards)//2:])
            recovery = 0.5 + (0.5 * (late_rewards / (early_rewards + 1e-6) - 0.5))
        else:
            recovery = 0.5
        recovery = self._clip_score(recovery)
        
        # === COMPOSITE SCORE ===
        # Forecasting: 35% accuracy, 25% adaptability, 25% consistency, 15% recovery
        score = (0.35 * accuracy +
                 0.25 * adaptability +
                 0.25 * consistency +
                 0.15 * recovery)
        
        score = self._clip_score(score)
        
        return {
            "score": float(score),
            "feedback": self._get_feedback(score, {}),
            "prediction_accuracy": float(accuracy),
            "adaptability": float(self._clip_score(adaptability)),
            "consistency": float(consistency),
            "error_recovery": float(recovery),
            "pattern_type": pattern,
        }


class ProductionGrader(EnhancedGrader):
    """Enhanced grader for production scheduling domain."""
    
    def grade(self, final_state: State, episode_rewards: List[float], task_params: Dict = None) -> Dict:
        """Grade production task with schedule quality and resource utilization."""
        task_params = task_params or {}
        num_machines = task_params.get('num_machines', 1)
        num_jobs = task_params.get('num_jobs', 5)
        
        # === METRIC 1: Schedule Quality ===
        avg_reward = np.mean(episode_rewards) if episode_rewards else 0.1
        schedule_quality = 0.3 + (0.7 * max(0.1, min(1.0, avg_reward)))  # 0.3-1.0
        schedule_quality = max(0.1, schedule_quality)
        
        # === METRIC 2: Resource Utilization ===
        # Lower holding costs = better utilization
        utilization_efficiency = max(0.1, 1.0 - (final_state.holding_costs / (5000.0 * num_machines)))
        utilization_efficiency = self._clip_score(utilization_efficiency)
        
        # === METRIC 3: Time Compliance ===
        # Absence of shortage penalty = on-time completion
        shortage_ratio = final_state.shortage_penalty / (2000.0 * num_jobs)
        time_compliance = max(0.1, 1.0 - (shortage_ratio * 0.5))  # 0.5-1.0
        time_compliance = max(0.1, time_compliance)
        
        # === METRIC 4: Solution Stability ===
        if len(episode_rewards) > 1:
            stability = 1.0 - min(0.4, np.std(episode_rewards) / (np.mean(episode_rewards) + 1e-6) * 0.2)
        else:
            stability = 0.5
        stability = self._clip_score(stability)
        
        # === COMPOSITE SCORE ===
        # Production: 35% schedule, 30% utilization, 20% compliance, 15% stability
        score = (0.35 * schedule_quality +
                 0.30 * utilization_efficiency +
                 0.20 * time_compliance +
                 0.15 * stability)
        
        score = self._clip_score(score)
        
        return {
            "score": float(score),
            "feedback": self._get_feedback(score, {}),
            "schedule_quality": float(self._clip_score(schedule_quality)),
            "resource_utilization": float(utilization_efficiency),
            "time_compliance": float(time_compliance),
            "solution_stability": float(stability),
            "machines": num_machines,
            "jobs": num_jobs,
        }


class ResourceAllocationGrader(EnhancedGrader):
    """Enhanced grader for dynamic resource allocation domain."""
    
    def grade(self, final_state: State, episode_rewards: List[float], task_params: Dict = None) -> Dict:
        """Grade resource allocation task with fairness and efficiency."""
        task_params = task_params or {}
        num_resources = task_params.get('num_resources', 5)
        num_consumers = task_params.get('num_consumers', 10)
        
        # === METRIC 1: Allocation Efficiency ===
        avg_reward = np.mean(episode_rewards) if episode_rewards else 0.1
        efficiency = 0.4 + (0.6 * max(0.1, min(1.0, avg_reward)))  # 0.4-1.0
        efficiency = max(0.1, efficiency)
        
        # === METRIC 2: Fair Distribution ===
        if len(final_state.warehouse_levels) > 1:
            # Measure coefficient of variation (lower = fairer)
            cv = np.std(final_state.warehouse_levels) / (np.mean(final_state.warehouse_levels) + 1e-6)
            fairness = max(0.1, 1.0 - min(0.5, cv * 0.3))  # 0.5-1.0
        else:
            fairness = 0.7
        fairness = max(0.1, fairness)
        
        # === METRIC 3: Demand Satisfaction ===
        shortage_ratio = final_state.shortage_penalty / (5000.0 * num_consumers)
        satisfaction = max(0.1, 1.0 - (shortage_ratio * 0.6))  # 0.4-1.0
        satisfaction = max(0.1, satisfaction)
        
        # === METRIC 4: SLA Compliance (if applicable) ===
        has_sla = task_params.get('has_sla', False)
        if has_sla:
            # Use shortage penalty as proxy for SLA violations
            sla_score = max(0.1, 1.0 - (final_state.shortage_penalty / 10000.0))
        else:
            # Still reward low waste
            sla_score = max(0.1, 1.0 - (final_state.holding_costs / 10000.0))
        sla_score = self._clip_score(sla_score)
        
        # === COMPOSITE SCORE ===
        # Resources: 30% efficiency, 25% fairness, 25% satisfaction, 20% SLA
        score = (0.30 * efficiency +
                 0.25 * fairness +
                 0.25 * satisfaction +
                 0.20 * sla_score)
        
        score = self._clip_score(score)
        
        return {
            "score": float(score),
            "feedback": self._get_feedback(score, {}),
            "allocation_efficiency": float(efficiency),
            "fair_distribution": float(fairness),
            "demand_satisfaction": float(satisfaction),
            "sla_compliance": float(sla_score),
            "resources": num_resources,
            "consumers": num_consumers,
        }


def get_grader(domain: str) -> EnhancedGrader:
    """Get appropriate grader for domain."""
    graders = {
        'warehouse': WarehouseGrader,
        'supply_chain': SupplyChainGrader,
        'forecasting': ForecastingGrader,
        'production': ProductionGrader,
        'resources': ResourceAllocationGrader,
    }
    grader_class = graders.get(domain, WarehouseGrader)
    return grader_class()
