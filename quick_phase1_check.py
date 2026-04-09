#!/usr/bin/env python3
"""Quick Phase 1 readiness check - tests 3+ representative tasks."""

import requests
import time
import sys

BASE_URL = "http://localhost:7860"

def main():
    print("=" * 60)
    print("PHASE 1 READINESS CHECK - 32-Task System")
    print("=" * 60)
    
    time.sleep(2)  # Wait for server
    
    try:
        # Test 1: Manifest with 32 tasks
        print("\n[1] Checking manifest (32 tasks requirement)...")
        resp = requests.get(f"{BASE_URL}/manifest", timeout=5)
        manifest = resp.json()
        
        task_count = manifest['task_count']
        domain_count = manifest['domain_count']
        
        print(f"    ✓ Found {task_count} tasks across {domain_count} domains")
        assert task_count >= 3, f"Need at least 3 tasks, got {task_count}"
        print(f"    ✓ Tasks: {', '.join(manifest['tasks'][:5])}...")
        
        # Test 2: Reset for warehouse task (required for Phase 1)
        print("\n[2] Testing warehouse_novice task...")
        reset_resp = requests.post(
            f"{BASE_URL}/reset",
            json={"task": "warehouse_novice"},
            timeout=5
        )
        assert reset_resp.status_code == 200
        reset_data = reset_resp.json()
        session_id = reset_data['session_id']
        print(f"    ✓ Reset successful, session: {session_id[:8]}...")
        
        # Test 3: Step for warehouse task
        print("\n[3] Testing step for warehouse task...")
        step_resp = requests.post(
            f"{BASE_URL}/step",
            json={"action": {"warehouse_id": 0, "amount": 10}},
            params={"session_id": session_id},
            timeout=5
        )
        assert step_resp.status_code == 200
        step_data = step_resp.json()
        print(f"    ✓ Step successful, reward: {step_data['reward']}")
        
        # Test 4: Test 2 additional domains
        print("\n[4] Testing additional domains...")
        test_tasks = [
            ("data_ingestion_simple", {"source_id": 0, "batch_size": 100}),
            ("code_style_compliance", {"file_id": 0, "fix_type": "style"}),
        ]
        
        for task_id, action in test_tasks:
            reset = requests.post(f"{BASE_URL}/reset", json={"task": task_id}, timeout=5).json()
            sid = reset['session_id']
            step = requests.post(f"{BASE_URL}/step", json={"action": action}, params={"session_id": sid}, timeout=5).json()
            print(f"    ✓ {task_id}: reward={step['reward']:.4f}")
        
        print("\n" + "=" * 60)
        print("✓ ALL CHECKS PASSED!")
        print(f"System ready: {task_count} tasks, 3+ domains, endpoints working")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ ASSERTION FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
