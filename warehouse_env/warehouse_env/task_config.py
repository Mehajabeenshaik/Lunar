"""Task variants - Only 3 warehouse management tasks are implemented."""

TASK_VARIANTS = {
    "warehouse_easy": {
        "name": "Warehouse Easy",
        "description": "1 warehouse, fixed demand, 30 steps",
        "difficulty": "easy",
        "mode": "normal",
        "num_warehouses": 1,
        "max_steps": 30,
        "domain": "warehouse",
    },
    
    "warehouse_medium": {
        "name": "Warehouse Medium",
        "description": "3 warehouses, variable demand, 60 steps",
        "difficulty": "medium",
        "mode": "normal",
        "num_warehouses": 3,
        "max_steps": 60,
        "domain": "warehouse",
    },
    
    "warehouse_hard": {
        "name": "Warehouse Hard",
        "description": "5 warehouses, seasonal demand, constraints, 90 steps",
        "difficulty": "hard",
        "mode": "normal",
        "num_warehouses": 5,
        "max_steps": 90,
        "domain": "warehouse",
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
