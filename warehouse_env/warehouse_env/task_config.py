"""
31 Tasks across 5 domains - Complete benchmark system
Warehouse, Data Pipeline, Code Review, Resource Allocation, System Optimization
"""

TASK_VARIANTS = {
    # ===== WAREHOUSE MANAGEMENT (5 tasks) =====
    "warehouse_novice": {
        "name": "Warehouse Novice",
        "description": "1 warehouse, fixed demand, simple inventory management",
        "difficulty": "novice",
        "mode": "normal",
        "num_warehouses": 1,
        "max_steps": 20,
        "domain": "warehouse",
        "version": "1.0",
    },
    "warehouse_easy": {
        "name": "Warehouse Easy",
        "description": "2 warehouses, variable demand, basic distribution",
        "difficulty": "easy",
        "mode": "normal",
        "num_warehouses": 2,
        "max_steps": 30,
        "domain": "warehouse",
        "version": "1.0",
    },
    "warehouse_medium": {
        "name": "Warehouse Medium",
        "description": "3 warehouses, variable demand, basic distribution",
        "difficulty": "medium",
        "mode": "normal",
        "num_warehouses": 3,
        "max_steps": 60,
        "domain": "warehouse",
        "version": "1.0",
    },
    "warehouse_intermediate": {
        "name": "Warehouse Intermediate",
        "description": "3 warehouses, seasonal demand, cross-warehouse transfers",
        "difficulty": "intermediate",
        "mode": "normal",
        "num_warehouses": 3,
        "max_steps": 60,
        "domain": "warehouse",
        "version": "1.0",
    },
    "warehouse_hard": {
        "name": "Warehouse Hard",
        "description": "5 warehouses, complex constraints, optimization required",
        "difficulty": "hard",
        "mode": "normal",
        "num_warehouses": 5,
        "max_steps": 90,
        "domain": "warehouse",
        "version": "1.0",
    },
    "warehouse_extreme": {
        "name": "Warehouse Extreme",
        "description": "8 warehouses, dynamic constraints, multi-objective optimization",
        "difficulty": "extreme",
        "mode": "normal",
        "num_warehouses": 8,
        "max_steps": 120,
        "domain": "warehouse",
        "version": "1.0",
    },

    # ===== DATA PIPELINE (8 tasks) =====
    "data_ingestion_simple": {
        "name": "Data Ingestion Simple",
        "description": "Basic data loading and validation",
        "difficulty": "easy",
        "mode": "data_processing",
        "domain": "data_pipeline",
        "version": "1.0",
        "complexity": "simple",
    },
    "data_ingestion_complex": {
        "name": "Data Ingestion Complex",
        "description": "Streaming data with rate limiting and buffering",
        "difficulty": "hard",
        "mode": "data_processing",
        "domain": "data_pipeline",
        "version": "1.0",
        "complexity": "complex",
    },
    "data_cleaning_basic": {
        "name": "Data Cleaning Basic",
        "description": "Handling missing values and basic outliers",
        "difficulty": "easy",
        "mode": "data_processing",
        "domain": "data_pipeline",
        "version": "1.0",
        "complexity": "simple",
    },
    "data_cleaning_advanced": {
        "name": "Data Cleaning Advanced",
        "description": "Outlier detection, anomaly detection, and deduplication",
        "difficulty": "hard",
        "mode": "data_processing",
        "domain": "data_pipeline",
        "version": "1.0",
        "complexity": "complex",
    },
    "data_validation_schema": {
        "name": "Data Validation Schema",
        "description": "Schema enforcement and type validation",
        "difficulty": "intermediate",
        "mode": "data_processing",
        "domain": "data_pipeline",
        "version": "1.0",
        "complexity": "moderate",
    },
    "data_validation_quality": {
        "name": "Data Validation Quality",
        "description": "Quality checks and statistical validation",
        "difficulty": "hard",
        "mode": "data_processing",
        "domain": "data_pipeline",
        "version": "1.0",
        "complexity": "complex",
    },
    "data_transformation_etl": {
        "name": "Data Transformation ETL",
        "description": "ETL pipeline with complex transformations",
        "difficulty": "hard",
        "mode": "data_processing",
        "domain": "data_pipeline",
        "version": "1.0",
        "complexity": "complex",
    },
    "data_export_format": {
        "name": "Data Export Format",
        "description": "Multi-format export with optimization",
        "difficulty": "intermediate",
        "mode": "data_processing",
        "domain": "data_pipeline",
        "version": "1.0",
        "complexity": "moderate",
    },

    # ===== CODE REVIEW (8 tasks) =====
    "code_style_compliance": {
        "name": "Code Style Compliance",
        "description": "Enforce code style standards and conventions",
        "difficulty": "easy",
        "mode": "code_analysis",
        "domain": "code_review",
        "version": "1.0",
        "complexity": "simple",
    },
    "code_performance_optimization": {
        "name": "Code Performance Optimization",
        "description": "Identify and optimize performance bottlenecks",
        "difficulty": "hard",
        "mode": "code_analysis",
        "domain": "code_review",
        "version": "1.0",
        "complexity": "complex",
    },
    "code_security_vulnerabilities": {
        "name": "Code Security Vulnerabilities",
        "description": "Detect security issues and vulnerabilities",
        "difficulty": "hard",
        "mode": "code_analysis",
        "domain": "code_review",
        "version": "1.0",
        "complexity": "complex",
    },
    "code_maintainability_metrics": {
        "name": "Code Maintainability Metrics",
        "description": "Analyze code quality and maintainability",
        "difficulty": "intermediate",
        "mode": "code_analysis",
        "domain": "code_review",
        "version": "1.0",
        "complexity": "moderate",
    },
    "code_refactoring_simple": {
        "name": "Code Refactoring Simple",
        "description": "Apply simple refactoring patterns",
        "difficulty": "intermediate",
        "mode": "code_analysis",
        "domain": "code_review",
        "version": "1.0",
        "complexity": "moderate",
    },
    "code_refactoring_complex": {
        "name": "Code Refactoring Complex",
        "description": "Complex refactoring with design pattern application",
        "difficulty": "hard",
        "mode": "code_analysis",
        "domain": "code_review",
        "version": "1.0",
        "complexity": "complex",
    },
    "code_testing_coverage": {
        "name": "Code Testing Coverage",
        "description": "Achieve comprehensive unit test coverage",
        "difficulty": "intermediate",
        "mode": "code_analysis",
        "domain": "code_review",
        "version": "1.0",
        "complexity": "moderate",
    },
    "code_integration_testing": {
        "name": "Code Integration Testing",
        "description": "Design and implement integration tests",
        "difficulty": "hard",
        "mode": "code_analysis",
        "domain": "code_review",
        "version": "1.0",
        "complexity": "complex",
    },

    # ===== RESOURCE ALLOCATION (5 tasks) =====
    "resource_budget_simple": {
        "name": "Resource Budget Simple",
        "description": "Basic budget allocation across projects",
        "difficulty": "easy",
        "mode": "resource_planning",
        "domain": "resource_allocation",
        "version": "1.0",
        "complexity": "simple",
    },
    "resource_budget_complex": {
        "name": "Resource Budget Complex",
        "description": "Multi-project budgeting with constraints",
        "difficulty": "hard",
        "mode": "resource_planning",
        "domain": "resource_allocation",
        "version": "1.0",
        "complexity": "complex",
    },
    "resource_scheduling_tasks": {
        "name": "Resource Scheduling Tasks",
        "description": "Optimize task scheduling with dependencies",
        "difficulty": "intermediate",
        "mode": "resource_planning",
        "domain": "resource_allocation",
        "version": "1.0",
        "complexity": "moderate",
    },
    "resource_scheduling_teams": {
        "name": "Resource Scheduling Teams",
        "description": "Allocate team members to projects optimally",
        "difficulty": "hard",
        "mode": "resource_planning",
        "domain": "resource_allocation",
        "version": "1.0",
        "complexity": "complex",
    },
    "resource_capacity_planning": {
        "name": "Resource Capacity Planning",
        "description": "Plan capacity requirements for future needs",
        "difficulty": "hard",
        "mode": "resource_planning",
        "domain": "resource_allocation",
        "version": "1.0",
        "complexity": "complex",
    },

    # ===== SYSTEM OPTIMIZATION (5 tasks) =====
    "optimization_query_basic": {
        "name": "Optimization Query Basic",
        "description": "Basic database query optimization",
        "difficulty": "intermediate",
        "mode": "optimization",
        "domain": "system_optimization",
        "version": "1.0",
        "complexity": "moderate",
    },
    "optimization_query_advanced": {
        "name": "Optimization Query Advanced",
        "description": "Advanced query optimization with indexing",
        "difficulty": "hard",
        "mode": "optimization",
        "domain": "system_optimization",
        "version": "1.0",
        "complexity": "complex",
    },
    "optimization_memory_usage": {
        "name": "Optimization Memory Usage",
        "description": "Optimize memory usage and garbage collection",
        "difficulty": "hard",
        "mode": "optimization",
        "domain": "system_optimization",
        "version": "1.0",
        "complexity": "complex",
    },
    "optimization_throughput": {
        "name": "Optimization Throughput",
        "description": "Maximize system throughput and parallelization",
        "difficulty": "hard",
        "mode": "optimization",
        "domain": "system_optimization",
        "version": "1.0",
        "complexity": "complex",
    },
    "optimization_latency": {
        "name": "Optimization Latency",
        "description": "Minimize latency and response times",
        "difficulty": "hard",
        "mode": "optimization",
        "domain": "system_optimization",
        "version": "1.0",
        "complexity": "complex",
    },
}


def get_task_variants() -> dict:
    """Get all 31 task variants."""
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
