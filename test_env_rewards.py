#!/usr/bin/env python
"""Test that environment rewards are strictly within (0, 1)."""

from warehouse_env.warehouse_env.multi_domain_env import MultiDomainEnv

print("Testing MultiDomainEnv episode reward validation:")

# Test all domains
domains = [
    ("warehouse", "warehouse_novice"),
    ("data_pipeline", "data_ingestion_simple"),
    ("code_review", "code_style_compliance"),
    ("resource_allocation", "resource_budget_simple"),
    ("system_optimization", "optimization_query_basic"),
]

all_valid = True
for domain_name, task_name in domains:
    try:
        env = MultiDomainEnv(task_name)
        state = env.reset()
        
        # Run a few steps (or just one)
        for step_i in range(3):
            if env.is_done():
                break
            # Dummy action
            action = {"placeholder": 1}
            next_state, reward = env.step(action)
        
        # Get final episode reward
        final_reward = env.get_episode_reward()
        
        # Check if valid
        valid = 0 < final_reward < 1
        status = "✓" if valid else "✗"
        print(f"{status} {task_name}: {final_reward:.4f} - {'Valid' if valid else 'INVALID'}")
        
        if not valid:
            all_valid = False
    except Exception as e:
        print(f"✗ {task_name}: ERROR - {str(e)}")
        all_valid = False

print()
print("=" * 60)
if all_valid:
    print("✓ All environment episode rewards are strictly within (0, 1)")
else:
    print("✗ FAILURE: Some rewards are out of range")
