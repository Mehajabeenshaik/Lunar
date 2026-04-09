#!/usr/bin/env python3
"""Test the new server with 32 tasks."""

import requests
import time
import json
import sys

BASE_URL = "http://localhost:7860"

def test_manifest():
    """Test manifest endpoint."""
    print("[1] Testing /manifest endpoint...")
    try:
        resp = requests.get(f"{BASE_URL}/manifest", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        print(f"  ✓ Tasks: {data['task_count']}")
        print(f"  ✓ Domains: {data['domain_count']}")
        print(f"  ✓ Sample tasks: {data['tasks'][:3]}")
        return data['tasks']
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return None

def test_reset_and_step(task_id):
    """Test reset and step endpoints."""
    print(f"\n[2] Testing reset for {task_id}...")
    try:
        # Reset
        reset_resp = requests.post(
            f"{BASE_URL}/reset",
            json={"task": task_id},
            timeout=5
        )
        reset_resp.raise_for_status()
        reset_data = reset_resp.json()
        session_id = reset_data['session_id']
        print(f"  ✓ Session created: {session_id[:8]}...")
        
        # Step
        print(f"[3] Testing step for {task_id}...")
        if "warehouse" in task_id:
            action = {"warehouse_id": 0, "amount": 10}
        elif "data_" in task_id:
            action = {"source_id": 0, "batch_size": 100}
        elif "code_" in task_id:
            action = {"file_id": 0, "fix_type": "style"}
        elif "resource_" in task_id:
            action = {"resource_id": 0, "allocation": 50}
        elif "optimization_" in task_id:
            action = {"query_id": 0, "optimization_type": "index"}
        else:
            action = {"action": "default"}
            
        step_resp = requests.post(
            f"{BASE_URL}/step",
            json={"action": action},
            params={"session_id": session_id},
            timeout=5
        )
        step_resp.raise_for_status()
        step_data = step_resp.json()
        print(f"  ✓ Reward: {step_data['reward']}")
        print(f"  ✓ Done: {step_data['done']}")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("TESTING NEW SERVER WITH 32 TASKS")
    print("=" * 60)
    
    # Test manifest
    tasks = test_manifest()
    if not tasks:
        print("\nFAILED: Could not get manifest")
        sys.exit(1)
    
    if len(tasks) != 32:
        print(f"\nFAILED: Expected 32 tasks, got {len(tasks)}")
        sys.exit(1)
    
    # Test sample tasks from each domain
    sample_tasks = [
        "warehouse_novice",
        "data_ingestion_simple",
        "code_style_compliance",
        "resource_budget_simple",
        "optimization_query_basic"
    ]
    
    results = []
    for task in sample_tasks:
        success = test_reset_and_step(task)
        results.append((task, success))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tasks loaded: {len(tasks)}/32 ✓")
    for task, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {task}")
    
    passed = sum(1 for _, s in results if s)
    print(f"\nEndpoint tests: {passed}/{len(results)} PASSED")
    
    if passed == len(results) and len(tasks) == 32:
        print("\n✓ ALL CHECKS PASSED!")
        return 0
    else:
        print("\n✗ SOME CHECKS FAILED!")
        return 1

if __name__ == "__main__":
    time.sleep(2)  # Wait for server to start
    sys.exit(main())
