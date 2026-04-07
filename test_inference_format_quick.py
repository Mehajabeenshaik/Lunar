#!/usr/bin/env python
"""Quick inference format test."""
import sys
sys.path.insert(0, '.')
from warehouse_env import WarehouseEnv, Action
from warehouse_env.graders import get_grader

print('Testing inference format...')

task = 'warehouse_easy'
env = WarehouseEnv(task=task)
obs = env.reset()

print(f'[START] task={task} env=warehouse_env model=test-model')

for step in range(3):
    action = Action(
        reorder_quantities=[50.0]*len(obs.warehouse_levels),
        transfers=[[0.0]*len(obs.warehouse_levels) for _ in range(len(obs.warehouse_levels))]
    )
    obs, reward = env.step(action)
    print(f'[STEP] step={step+1} action=reorder([50.0]) reward={reward.value:.2f} done={str(reward.done).lower()} error=null')

grader = get_grader(task)
grade = grader.grade(env.state, env.episode_rewards)
rewards = ','.join(f'{r:.2f}' for r in env.episode_rewards)
print(f'[END] success=true steps={len(env.episode_rewards)} score={grade["score"]:.2f} rewards={rewards}')

print('\nInference format test PASSED!')
