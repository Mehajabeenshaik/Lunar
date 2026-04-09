"""Task variants - 32 tasks across 5 domains with comprehensive graders."""

TASK_VARIANTS = {
    # Warehouse Domain (6 tasks: novice to extreme)
    "warehouse_novice": {
        "name": "Warehouse Novice",
        "description": "1 warehouse, fixed demand, 30 steps - perfect for learning",
        "difficulty": "novice",
        "mode": "normal",
        "num_warehouses": 1,
        "max_steps": 30,
        "domain": "warehouse",
    },
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
    "warehouse_intermediate": {
        "name": "Warehouse Intermediate",
        "description": "4 warehouses, complex demand, seasonal patterns, 75 steps",
        "difficulty": "intermediate",
        "mode": "normal",
        "num_warehouses": 4,
        "max_steps": 75,
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
    "warehouse_extreme": {
        "name": "Warehouse Extreme",
        "description": "7 warehouses, adversarial demand, multiple constraints, 120 steps",
        "difficulty": "extreme",
        "mode": "hard",
        "num_warehouses": 7,
        "max_steps": 120,
        "domain": "warehouse",
    },
    
    # Data Pipeline Domain (8 tasks)
    "data_ingestion_simple": {
        "name": "Data Ingestion Simple",
        "description": "Ingest data from single source with basic validation",
        "difficulty": "easy",
        "mode": "normal",
        "max_steps": 50,
        "domain": "data_pipeline",
        "source_count": 1,
    },
    "data_ingestion_complex": {
        "name": "Data Ingestion Complex",
        "description": "Ingest data from multiple heterogeneous sources with conflict resolution",
        "difficulty": "hard",
        "mode": "normal",
        "max_steps": 100,
        "domain": "data_pipeline",
        "source_count": 5,
    },
    "data_cleaning_basic": {
        "name": "Data Cleaning Basic",
        "description": "Clean data with simple operations (remove nulls, duplicates)",
        "difficulty": "easy",
        "mode": "normal",
        "max_steps": 50,
        "domain": "data_pipeline",
    },
    "data_cleaning_advanced": {
        "name": "Data Cleaning Advanced",
        "description": "Advanced cleaning: outlier detection, complex transformations, handling missing patterns",
        "difficulty": "hard",
        "mode": "normal",
        "max_steps": 100,
        "domain": "data_pipeline",
    },
    "data_validation_schema": {
        "name": "Data Validation Schema",
        "description": "Validate data against schema constraints",
        "difficulty": "medium",
        "mode": "normal",
        "max_steps": 60,
        "domain": "data_pipeline",
    },
    "data_validation_quality": {
        "name": "Data Validation Quality",
        "description": "Validate data quality: completeness, consistency, accuracy",
        "difficulty": "hard",
        "mode": "normal",
        "max_steps": 80,
        "domain": "data_pipeline",
    },
    "data_transformation_etl": {
        "name": "Data Transformation ETL",
        "description": "Extract, transform, and load data with complex business rules",
        "difficulty": "hard",
        "mode": "normal",
        "max_steps": 100,
        "domain": "data_pipeline",
    },
    "data_export_format": {
        "name": "Data Export Format",
        "description": "Export data to various formats (CSV, JSON, Parquet) with optimization",
        "difficulty": "medium",
        "mode": "normal",
        "max_steps": 60,
        "domain": "data_pipeline",
    },
    
    # Code Review Domain (8 tasks)
    "code_style_compliance": {
        "name": "Code Style Compliance",
        "description": "Ensure code follows style guidelines (PEP8, conventions)",
        "difficulty": "easy",
        "mode": "normal",
        "max_steps": 40,
        "domain": "code_review",
    },
    "code_performance_optimization": {
        "name": "Code Performance Optimization",
        "description": "Optimize code for time and space complexity",
        "difficulty": "hard",
        "mode": "normal",
        "max_steps": 80,
        "domain": "code_review",
    },
    "code_security_vulnerabilities": {
        "name": "Code Security Vulnerabilities",
        "description": "Identify and fix security vulnerabilities",
        "difficulty": "hard",
        "mode": "normal",
        "max_steps": 80,
        "domain": "code_review",
    },
    "code_maintainability_metrics": {
        "name": "Code Maintainability Metrics",
        "description": "Improve code maintainability: reduce cyclomatic complexity, improve clarity",
        "difficulty": "medium",
        "mode": "normal",
        "max_steps": 60,
        "domain": "code_review",
    },
    "code_refactoring_simple": {
        "name": "Code Refactoring Simple",
        "description": "Simple refactoring to extract methods and reduce duplication",
        "difficulty": "medium",
        "mode": "normal",
        "max_steps": 60,
        "domain": "code_review",
    },
    "code_refactoring_complex": {
        "name": "Code Refactoring Complex",
        "description": "Complex refactoring: architectural changes, design pattern application",
        "difficulty": "hard",
        "mode": "normal",
        "max_steps": 100,
        "domain": "code_review",
    },
    "code_testing_coverage": {
        "name": "Code Testing Coverage",
        "description": "Increase unit test coverage for existing code",
        "difficulty": "medium",
        "mode": "normal",
        "max_steps": 60,
        "domain": "code_review",
    },
    "code_integration_testing": {
        "name": "Code Integration Testing",
        "description": "Design and implement integration tests for system components",
        "difficulty": "hard",
        "mode": "normal",
        "max_steps": 80,
        "domain": "code_review",
    },
    
    # Resource Allocation Domain (5 tasks)
    "resource_budget_simple": {
        "name": "Resource Budget Simple",
        "description": "Allocate budget across simple resource categories",
        "difficulty": "easy",
        "mode": "normal",
        "max_steps": 40,
        "domain": "resource_allocation",
    },
    "resource_budget_complex": {
        "name": "Resource Budget Complex",
        "description": "Complex budget allocation with constraints, dependencies, and optimization",
        "difficulty": "hard",
        "mode": "normal",
        "max_steps": 100,
        "domain": "resource_allocation",
    },
    "resource_scheduling_tasks": {
        "name": "Resource Scheduling Tasks",
        "description": "Schedule tasks to resources while minimizing completion time",
        "difficulty": "hard",
        "mode": "normal",
        "max_steps": 80,
        "domain": "resource_allocation",
    },
    "resource_scheduling_teams": {
        "name": "Resource Scheduling Teams",
        "description": "Schedule team members to projects with skill matching",
        "difficulty": "hard",
        "mode": "normal",
        "max_steps": 80,
        "domain": "resource_allocation",
    },
    "resource_capacity_planning": {
        "name": "Resource Capacity Planning",
        "description": "Plan capacity across teams, identifying bottlenecks and optimizing utilization",
        "difficulty": "hard",
        "mode": "normal",
        "max_steps": 100,
        "domain": "resource_allocation",
    },
    
    # System Optimization Domain (5 tasks)
    "optimization_query_basic": {
        "name": "Optimization Query Basic",
        "description": "Optimize basic database queries with simple index strategies",
        "difficulty": "easy",
        "mode": "normal",
        "max_steps": 40,
        "domain": "system_optimization",
    },
    "optimization_query_advanced": {
        "name": "Optimization Query Advanced",
        "description": "Advanced query optimization: join strategies, execution plans",
        "difficulty": "hard",
        "mode": "normal",
        "max_steps": 80,
        "domain": "system_optimization",
    },
    "optimization_memory_usage": {
        "name": "Optimization Memory Usage",
        "description": "Optimize memory usage in systems with large datasets",
        "difficulty": "hard",
        "mode": "normal",
        "max_steps": 80,
        "domain": "system_optimization",
    },
    "optimization_throughput": {
        "name": "Optimization Throughput",
        "description": "Maximize system throughput with parallel processing and batching",
        "difficulty": "hard",
        "mode": "normal",
        "max_steps": 100,
        "domain": "system_optimization",
    },
    "optimization_latency": {
        "name": "Optimization Latency",
        "description": "Minimize system latency through caching, async operations, and load distribution",
        "difficulty": "hard",
        "mode": "normal",
        "max_steps": 100,
        "domain": "system_optimization",
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


def list_tasks_by_domain(domain: str) -> dict:
    """Get all tasks for a domain."""
    return {
        task_id: info 
        for task_id, info in TASK_VARIANTS.items() 
        if info["domain"] == domain
    }


def get_all_domains() -> list:
    """Get list of all domains."""
    return list(set(info["domain"] for info in TASK_VARIANTS.values()))


def get_task_count() -> int:
    """Total number of tasks."""
    return len(TASK_VARIANTS)


def get_domain_count() -> int:
    """Total number of domains."""
    return len(get_all_domains())
