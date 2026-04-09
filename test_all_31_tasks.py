#!/usr/bin/env python3
"""
Comprehensive test suite for all 31 tasks
Validates that all tasks load, execute, and return positive rewards
"""

import sys
from warehouse_env.warehouse_env.task_config import get_task_variants, get_task_count, get_domain_count, get_all_domains
from warehouse_env.warehouse_env.multi_domain_env import MultiDomainEnv
from warehouse_env.warehouse_env.graders_comprehensive import get_grader_for_task
from warehouse_env.warehouse_env.models import State
import numpy as np


def test_all_31_tasks():
    """Test all 31 tasks for functionality."""
    
    tasks = get_task_variants()
    domains = get_all_domains()
    
    print("=" * 100)
    print(f"COMPREHENSIVE TASK TEST - {get_task_count()} Tasks across {get_domain_count()} Domains")
    print("=" * 100)
    
    # Domain breakdown
    print(f"\nDomains ({get_domain_count()}):")
    for domain in domains:
        domain_tasks = [t for t, info in tasks.items() if info.get('domain') == domain]
        print(f"  - {domain}: {len(domain_tasks)} tasks")
    
    results = {
        'passed': [],
        'failed': [],
        'domain_results': {}
    }
    
    # Test each task
    print(f"\n{'Task ID':<35} {'Domain':<20} {'Reward':<10} {'Status':<10}")
    print("-" * 100)
    
    for task_id in sorted(tasks.keys()):
        task_info = tasks[task_id]
        domain = task_info.get('domain', 'unknown')
        
        if domain not in results['domain_results']:
            results['domain_results'][domain] = {'passed': 0, 'failed': 0}
        
        try:
            # Create environment
            env = MultiDomainEnv(task_id)
            
            # Reset
            state = env.reset()
            
            # Get action for domain
            if domain == 'warehouse':
                action = {'reorder_quantities': [100], 'transfers': []}
            elif domain == 'data_pipeline':
                action = {'records': 1000, 'cleaning_level': 0.5, 'validation_threshold': 0.8}
            elif domain == 'code_review':
                action = {'files': 5, 'refactoring': 0.5, 'testing': 0.3}
            elif domain == 'resource_allocation':
                action = {'budget': 5000, 'team_members': 5, 'efficiency': 0.8}
            elif domain == 'system_optimization':
                action = {'indexing': 0.5, 'parallelization': 0.5, 'caching': 0.5}
            else:
                action = {}
            
            # Step
            next_state, reward = env.step(action)
            
            # Check reward
            if reward > 0 and reward <= 1.0:
                status = "✓ PASS"
                results['passed'].append(task_id)
                results['domain_results'][domain]['passed'] += 1
            else:
                status = f"✗ FAIL"
                results['failed'].append(task_id)
                results['domain_results'][domain]['failed'] += 1
                
            print(f"{task_id:<35} {domain:<20} {reward:<10.4f} {status:<10}")
            
        except Exception as e:
            print(f"{task_id:<35} {domain:<20} {'ERROR':<10} ✗ FAIL")
            print(f"  Error: {str(e)[:60]}")
            results['failed'].append(task_id)
            results['domain_results'][domain]['failed'] += 1
    
    # Summary
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    
    print(f"\nOverall Results:")
    print(f"  Passed: {len(results['passed'])}/{get_task_count()}")
    print(f"  Failed: {len(results['failed'])}/{get_task_count()}")
    
    print(f"\nBy Domain:")
    for domain in domains:
        passed = results['domain_results'][domain]['passed']
        failed = results['domain_results'][domain]['failed']
        total = passed + failed
        percentage = (passed / total * 100) if total > 0 else 0
        print(f"  {domain:<25} {passed}/{total} passed ({percentage:.0f}%)")
    
    if results['failed']:
        print(f"\nFailed tasks:")
        for task in results['failed']:
            print(f"  - {task}")
    
    # Final verdict
    print("\n" + "=" * 100)
    if len(results['failed']) == 0:
        print(f"✓ ALL {get_task_count()} TASKS PASSED!")
        print("✓ SYSTEM READY FOR VALIDATOR SUBMISSION")
        return True
    else:
        print(f"✗ {len(results['failed'])} TASKS FAILED - SYSTEM NOT READY")
        return False


def test_graders():
    """Test all 31 graders for instantiation and basic functionality."""
    
    print("\n" + "=" * 100)
    print("GRADER FUNCTIONALITY TEST")
    print("=" * 100)
    
    tasks = get_task_variants()
    results = {'graders_ok': 0, 'graders_fail': 0}
    
    print(f"\n{'Grader':<35} {'Status':<10}")
    print("-" * 60)
    
    for task_id in sorted(tasks.keys()):
        try:
            grader = get_grader_for_task(task_id)
            
            # Mock state and rewards
            mock_state = {'some_value': 1.0}
            mock_rewards = [0.5, 0.6, 0.7]
            
            # Grade
            result = grader.grade(mock_state, mock_rewards)
            
            if 'score' in result and 0 <= result['score'] <= 1.0:
                print(f"{task_id:<35} ✓ OK")
                results['graders_ok'] += 1
            else:
                print(f"{task_id:<35} ✗ FAIL (bad score format)")
                results['graders_fail'] += 1
                
        except Exception as e:
            print(f"{task_id:<35} ✗ FAIL ({str(e)[:30]})")
            results['graders_fail'] += 1
    
    print("\n" + "-" * 60)
    print(f"Graders OK: {results['graders_ok']}/{get_task_count()}")
    print(f"Graders FAIL: {results['graders_fail']}/{get_task_count()}")
    
    return results['graders_fail'] == 0


def test_task_variants():
    """Test task variant configuration."""
    
    print("\n" + "=" * 100)
    print("TASK CONFIGURATION TEST")
    print("=" * 100)
    
    tasks = get_task_variants()
    
    print(f"\nTotal Tasks: {len(tasks)}")
    print(f"Total Domains: {len(get_all_domains())}")
    
    # Count by difficulty
    difficulties = {}
    for task in tasks.values():
        diff = task.get('difficulty', 'unknown')
        difficulties[diff] = difficulties.get(diff, 0) + 1
    
    print(f"\nBy Difficulty:")
    for diff in ['novice', 'easy', 'intermediate', 'hard', 'extreme']:
        count = difficulties.get(diff, 0)
        if count > 0:
            print(f"  {diff}: {count}")
    
    # Verify all have required fields
    required_fields = ['name', 'description', 'difficulty', 'domain', 'version']
    missing_count = 0
    
    for task_id, task in tasks.items():
        for field in required_fields:
            if field not in task:
                print(f"  Missing field '{field}' in {task_id}")
                missing_count += 1
    
    if missing_count == 0:
        print(f"\n✓ All {len(tasks)} tasks have required fields")
        return True
    else:
        print(f"\n✗ {missing_count} missing fields found")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 100)
    print("COMPREHENSIVE LUNAR TEST SUITE")
    print("Testing 31 tasks across 5 domains")
    print("=" * 100 + "\n")
    
    # Run tests
    config_ok = test_task_variants()
    graders_ok = test_graders()
    tasks_ok = test_all_31_tasks()
    
    # Final result
    print("\n" + "=" * 100)
    print("FINAL RESULT")
    print("=" * 100)
    
    all_ok = config_ok and graders_ok and tasks_ok
    
    print(f"Configuration: {'✓ OK' if config_ok else '✗ FAIL'}")
    print(f"Graders:       {'✓ OK' if graders_ok else '✗ FAIL'}")
    print(f"Tasks:         {'✓ OK' if tasks_ok else '✗ FAIL'}")
    
    print("\n" + "=" * 100)
    if all_ok:
        print("✓✓✓ ALL TESTS PASSED - SYSTEM READY ✓✓✓")
        print("=" * 100)
        sys.exit(0)
    else:
        print("✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("=" * 100)
        sys.exit(1)
