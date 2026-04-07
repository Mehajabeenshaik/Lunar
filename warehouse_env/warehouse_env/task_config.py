"""Task variants with different modes and difficulties."""

TASK_VARIANTS = {
    # Easy Difficulty - Basic warehouse management
    "warehouse_easy": {
        "name": "Warehouse Easy",
        "description": "1 warehouse, fixed demand, 30 steps",
        "difficulty": "easy",
        "mode": "normal",
        "num_warehouses": 1,
        "max_steps": 30,
    },
    "warehouse_easy_volatile": {
        "name": "Warehouse Easy - Volatile Demand",
        "description": "1 warehouse, variable demand, 30 steps",
        "difficulty": "easy",
        "mode": "volatile",
        "num_warehouses": 1,
        "max_steps": 30,
        "demand_volatility": 0.5,
    },
    
    # Medium Difficulty - Multi-warehouse, balanced challenge
    "warehouse_medium": {
        "name": "Warehouse Medium",
        "description": "3 warehouses, variable demand, 60 steps",
        "difficulty": "medium",
        "mode": "normal",
        "num_warehouses": 3,
        "max_steps": 60,
    },
    "warehouse_medium_volatile": {
        "name": "Warehouse Medium - Volatile Demand",
        "description": "3 warehouses, high volatility, 60 steps",
        "difficulty": "medium",
        "mode": "volatile",
        "num_warehouses": 3,
        "max_steps": 60,
        "demand_volatility": 0.7,
    },
    
    # Hard Difficulty - Complex multi-warehouse system
    "warehouse_hard": {
        "name": "Warehouse Hard",
        "description": "5 warehouses, seasonal demand, constraints, 90 steps",
        "difficulty": "hard",
        "mode": "normal",
        "num_warehouses": 5,
        "max_steps": 90,
    },
    "warehouse_hard_stress": {
        "name": "Warehouse Hard - Stress Test",
        "description": "5 warehouses, extreme volatility, tight constraints, 90 steps",
        "difficulty": "hard",
        "mode": "stress",
        "num_warehouses": 5,
        "max_steps": 90,
        "demand_volatility": 0.9,
        "supply_constraint": 0.7,  # Reduced supply availability
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
