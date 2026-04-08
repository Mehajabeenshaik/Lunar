"""Task variants with 31 diverse challenges across 5 domains."""

TASK_VARIANTS = {
    # =====================================================================
    # DOMAIN 1: WAREHOUSE MANAGEMENT (10 tasks - EXPANDED)
    # =====================================================================
    
    # Easy Tier - Beginner (3 tasks)
    "warehouse_easy": {
        "name": "Warehouse Easy",
        "description": "1 warehouse, fixed demand, 30 steps",
        "difficulty": "easy",
        "mode": "normal",
        "num_warehouses": 1,
        "max_steps": 30,
        "domain": "warehouse",
    },
    "warehouse_easy_volatile": {
        "name": "Warehouse Easy - Volatile Demand",
        "description": "1 warehouse, variable demand, 30 steps",
        "difficulty": "easy",
        "mode": "volatile",
        "num_warehouses": 1,
        "max_steps": 30,
        "demand_volatility": 0.5,
        "domain": "warehouse",
    },
    "warehouse_easy_seasonal": {
        "name": "Warehouse Easy - Seasonal",
        "description": "1 warehouse, seasonal patterns with 80% predictability, 40 steps",
        "difficulty": "easy",
        "mode": "seasonal",
        "num_warehouses": 1,
        "max_steps": 40,
        "seasonal_period": 10,
        "predictability": 0.8,
        "domain": "warehouse",
    },
    
    # Medium Tier - Intermediate (4 tasks)
    "warehouse_medium": {
        "name": "Warehouse Medium",
        "description": "3 warehouses, variable demand, 60 steps",
        "difficulty": "medium",
        "mode": "normal",
        "num_warehouses": 3,
        "max_steps": 60,
        "domain": "warehouse",
    },
    "warehouse_medium_volatile": {
        "name": "Warehouse Medium - Volatile Demand",
        "description": "3 warehouses, high volatility (70%), 60 steps",
        "difficulty": "medium",
        "mode": "volatile",
        "num_warehouses": 3,
        "max_steps": 60,
        "demand_volatility": 0.7,
        "domain": "warehouse",
    },
    "warehouse_medium_transfers": {
        "name": "Warehouse Medium - Inter-warehouse Transfers",
        "description": "3 warehouses with transfer costs, demand variability, 70 steps",
        "difficulty": "medium",
        "mode": "transfers",
        "num_warehouses": 3,
        "max_steps": 70,
        "transfer_cost": 50,
        "demand_volatility": 0.3,
        "domain": "warehouse",
    },
    "warehouse_medium_sla": {
        "name": "Warehouse Medium - SLA Constraints",
        "description": "3 warehouses with delivery SLAs and penalties, 70 steps",
        "difficulty": "medium",
        "mode": "sla",
        "num_warehouses": 3,
        "max_steps": 70,
        "sla_targets": [0.92, 0.94, 0.90],
        "sla_penalty": 100,
        "domain": "warehouse",
    },
    
    # Hard Tier - Advanced (3 tasks)
    "warehouse_hard": {
        "name": "Warehouse Hard",
        "description": "5 warehouses, seasonal demand, constraints, 90 steps",
        "difficulty": "hard",
        "mode": "normal",
        "num_warehouses": 5,
        "max_steps": 90,
        "domain": "warehouse",
    },
    "warehouse_hard_stress": {
        "name": "Warehouse Hard - Stress Test",
        "description": "5 warehouses, 90% volatility, tight constraints, 90 steps",
        "difficulty": "hard",
        "mode": "stress",
        "num_warehouses": 5,
        "max_steps": 90,
        "demand_volatility": 0.9,
        "supply_constraint": 0.7,
        "domain": "warehouse",
    },
    "warehouse_hard_network": {
        "name": "Warehouse Hard - Network Optimization",
        "description": "7 warehouses with complex supplier network, 120 steps",
        "difficulty": "hard",
        "mode": "network",
        "num_warehouses": 7,
        "max_steps": 120,
        "num_suppliers": 3,
        "transport_cost": 25,
        "lead_time_variance": 0.4,
        "domain": "warehouse",
    },
    
    # =====================================================================
    # DOMAIN 2: SUPPLY CHAIN LOGISTICS (7 tasks - EXPANDED)
    # =====================================================================
    
    "supply_chain_basic": {
        "name": "Supply Chain - Basic",
        "description": "2-tier supplier network with fixed lead times, 40 steps",
        "difficulty": "easy",
        "domain": "supply_chain",
        "num_tiers": 2,
        "max_steps": 40,
        "lead_time": 3,
    },
    "supply_chain_distributor": {
        "name": "Supply Chain - Distributor",
        "description": "2-tier with inventory management and order batching, 50 steps",
        "difficulty": "easy",
        "domain": "supply_chain",
        "num_tiers": 2,
        "max_steps": 50,
        "num_distributors": 2,
        "batch_min": 10,
        "batch_cost": 50,
    },
    "supply_chain_dynamic": {
        "name": "Supply Chain - Dynamic Pricing",
        "description": "3-tier network with dynamic pricing and variable lead times, 60 steps",
        "difficulty": "medium",
        "domain": "supply_chain",
        "num_tiers": 3,
        "max_steps": 60,
        "lead_time_variability": 0.3,
        "price_volatility": 0.5,
    },
    "supply_chain_multiproduct": {
        "name": "Supply Chain - Multi-product",
        "description": "3-tier with multiple SKUs and shared resources, 70 steps",
        "difficulty": "medium",
        "domain": "supply_chain",
        "num_tiers": 3,
        "num_products": 5,
        "max_steps": 70,
        "resource_sharing": True,
    },
    "supply_chain_disruption": {
        "name": "Supply Chain - Disruption",
        "description": "4-tier network with supplier disruptions and recovery, 80 steps",
        "difficulty": "hard",
        "domain": "supply_chain",
        "num_tiers": 4,
        "max_steps": 80,
        "disruption_probability": 0.2,
        "recovery_time": 5,
    },
    "supply_chain_resilience": {
        "name": "Supply Chain - Resilience & Recovery",
        "description": "4-tier with disruptions, dual sourcing, recovery strategies, 90 steps",
        "difficulty": "hard",
        "domain": "supply_chain",
        "num_tiers": 4,
        "max_steps": 90,
        "dual_sourcing": True,
        "disruption_frequency": 0.15,
        "recovery_strategies": 3,
    },
    "supply_chain_optimization": {
        "name": "Supply Chain - Full Optimization",
        "description": "5-tier full network optimization with cost minimization, 120 steps",
        "difficulty": "hard",
        "domain": "supply_chain",
        "num_tiers": 5,
        "max_steps": 120,
        "num_suppliers_per_tier": 3,
        "total_network_cost": 10000,
        "multi_objective": True,
    },
    
    # =====================================================================
    # DOMAIN 3: DEMAND FORECASTING (6 tasks - EXPANDED)
    # =====================================================================
    
    "forecast_stationary": {
        "name": "Forecasting - Stationary",
        "description": "Constant demand with Gaussian noise, 50 steps",
        "difficulty": "easy",
        "domain": "forecasting",
        "pattern": "stationary",
        "base_demand": 1000,
        "noise_std": 100,
        "max_steps": 50,
    },
    "forecast_noisy": {
        "name": "Forecasting - Noisy",
        "description": "High-noise stationary with filtering challenge, 60 steps",
        "difficulty": "easy",
        "domain": "forecasting",
        "pattern": "noisy_stationary",
        "base_demand": 800,
        "noise_std": 250,
        "max_steps": 60,
    },
    "forecast_seasonal": {
        "name": "Forecasting - Seasonal",
        "description": "Seasonal patterns with 80% predictability, 90 steps",
        "difficulty": "medium",
        "domain": "forecasting",
        "pattern": "seasonal",
        "season_period": 30,
        "predictability": 0.8,
        "max_steps": 90,
    },
    "forecast_trend": {
        "name": "Forecasting - Trend",
        "description": "Linear and non-linear trends with noise, 100 steps",
        "difficulty": "medium",
        "domain": "forecasting",
        "pattern": "trend",
        "trend_type": "mixed",
        "trend_rate": 0.5,
        "max_steps": 100,
    },
    "forecast_hybrid": {
        "name": "Forecasting - Hybrid Patterns",
        "description": "Seasonal + trend + anomaly detection required, 110 steps",
        "difficulty": "hard",
        "domain": "forecasting",
        "pattern": "hybrid",
        "has_anomalies": True,
        "anomaly_frequency": 0.05,
        "max_steps": 110,
    },
    "forecast_chaotic": {
        "name": "Forecasting - Chaotic",
        "description": "Chaotic patterns with 50% predictability (adversarial), 120 steps",
        "difficulty": "hard",
        "domain": "forecasting",
        "pattern": "chaotic",
        "predictability": 0.5,
        "chaos_factor": 0.9,
        "max_steps": 120,
    },
    
    # =====================================================================
    # DOMAIN 4: PRODUCTION SCHEDULING (6 tasks - EXPANDED)
    # =====================================================================
    
    "production_simple": {
        "name": "Production - Simple",
        "description": "Single machine, 5 jobs, no precedence constraints, 30 steps",
        "difficulty": "easy",
        "domain": "production",
        "num_machines": 1,
        "num_jobs": 5,
        "has_precedence": False,
        "max_steps": 30,
    },
    "production_batching": {
        "name": "Production - Batching",
        "description": "Single machine with batch processing and setup times, 40 steps",
        "difficulty": "easy",
        "domain": "production",
        "num_machines": 1,
        "num_jobs": 8,
        "batch_processing": True,
        "setup_time": 3,
        "max_steps": 40,
    },
    "production_complex": {
        "name": "Production - Complex",
        "description": "3 machines, 20 jobs with precedence and setup times, 60 steps",
        "difficulty": "medium",
        "domain": "production",
        "num_machines": 3,
        "num_jobs": 20,
        "has_precedence": True,
        "setup_time": 2,
        "max_steps": 60,
    },
    "production_flexible": {
        "name": "Production - Flexible",
        "description": "5 machines, 30 jobs with flexible routing, 90 steps",
        "difficulty": "hard",
        "domain": "production",
        "num_machines": 5,
        "num_jobs": 30,
        "flexible_routing": True,
        "machine_compatibility": 0.7,
        "max_steps": 90,
    },
    "production_parallel": {
        "name": "Production - Parallel Processing",
        "description": "Multi-machine with parallel tasks and resource sharing, 100 steps",
        "difficulty": "hard",
        "domain": "production",
        "num_machines": 6,
        "num_jobs": 35,
        "parallel_tasks": True,
        "shared_resources": 2,
        "max_steps": 100,
    },
    "production_realtime": {
        "name": "Production - Real-time",
        "description": "Real-time job arrivals, dynamic rescheduling, rebid on failures, 120 steps",
        "difficulty": "hard",
        "domain": "production",
        "num_machines": 5,
        "dynamic_arrivals": True,
        "arrival_rate": 0.3,
        "rescheduling_cost": 10,
        "failure_rate": 0.05,
        "max_steps": 120,
    },
    
    # =====================================================================
    # DOMAIN 5: DYNAMIC RESOURCE ALLOCATION (5 tasks - EXPANDED)
    # =====================================================================
    
    "resource_basic": {
        "name": "Resource Allocation - Basic",
        "description": "5 resources, 10 consumers, 50 steps",
        "difficulty": "easy",
        "domain": "resources",
        "num_resources": 5,
        "num_consumers": 10,
        "max_steps": 50,
    },
    "resource_fair": {
        "name": "Resource Allocation - Fair Sharing",
        "description": "10 resources, 20 consumers with fairness constraints, 60 steps",
        "difficulty": "easy",
        "domain": "resources",
        "num_resources": 10,
        "num_consumers": 20,
        "fairness_constraints": True,
        "max_steps": 60,
    },
    "resource_advanced": {
        "name": "Resource Allocation - Advanced",
        "description": "20 resources, 50 consumers with prioritization, 80 steps",
        "difficulty": "medium",
        "domain": "resources",
        "num_resources": 20,
        "num_consumers": 50,
        "has_priorities": True,
        "num_priority_levels": 3,
        "max_steps": 80,
    },
    "resource_heterogeneous": {
        "name": "Resource Allocation - Heterogeneous",
        "description": "30+ resources with different types, 100 consumers, 110 steps",
        "difficulty": "hard",
        "domain": "resources",
        "num_resources": 35,
        "num_consumers": 100,
        "resource_types": 5,
        "type_compatibility": 0.6,
        "max_steps": 110,
    },
    "resource_extreme": {
        "name": "Resource Allocation - Extreme Scale",
        "description": "100+ resources, 200+ consumers with SLA constraints, 150 steps",
        "difficulty": "hard",
        "domain": "resources",
        "num_resources": 120,
        "num_consumers": 250,
        "has_sla": True,
        "sla_violation_penalty": 100,
        "dynamic_demands": True,
        "max_steps": 150,
    },
}


def get_task_variants() -> dict:
    """Get all task variants."""
    return TASK_VARIANTS


def is_valid_task(task_id: str) -> bool:
    """Check if task ID is valid."""
    return task_id in TASK_VARIANTS


def get_task_info(task_id: str) -> dict:
    """Get task information."""
    if not is_valid_task(task_id):
        raise ValueError(f"Unknown task: {task_id}")
    return TASK_VARIANTS[task_id]


def list_tasks_by_difficulty(difficulty: str) -> dict:
    """Get all tasks for a difficulty level."""
    return {
        task_id: info 
        for task_id, info in TASK_VARIANTS.items() 
        if info["difficulty"] == difficulty
    }
