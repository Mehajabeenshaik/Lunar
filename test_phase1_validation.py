#!/usr/bin/env python3
"""Comprehensive Phase 1 validation test - simulates validator behavior."""

import requests
import time
import json
import sys

BASE_URL = "http://localhost:7860"

def log_step(level, message):
    """Print formatted log message."""
    symbols = {"OK": "✓", "ERROR": "✗", "INFO": "ℹ"}
    print(f"  [{symbols.get(level, '•')}] {message}")

def test_health():
    """Test /health endpoint."""
    print("\n[HEALTH CHECK]")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        resp.raise_for_status()
        log_step("OK", "Health check passed")
        return True
    except Exception as e:
        log_step("ERROR", f"Health check failed: {e}")
        return False

def test_manifest():
    """Test /manifest endpoint."""
    print("\n[MANIFEST CHECK]")
    try:
        resp = requests.get(f"{BASE_URL}/manifest", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        
        # Basic validation
        assert data['task_count'] >= 3, f"Expected at least 3 tasks, got {data['task_count']}"
        assert data['domain_count'] >= 1, f"Expected at least 1 domain, got {data['domain_count']}"
        assert len(data['tasks']) == data['task_count'], "Task list count mismatch"
        
        log_step("OK", f"Manifest valid: {data['task_count']} tasks across {data['domain_count']} domains")
        log_step("OK", f"Available tasks: {', '.join(data['tasks'][:5])}...")
        
        return data['tasks'], True
    except AssertionError as e:
        log_step("ERROR", str(e))
        return None, False
    except Exception as e:
        log_step("ERROR", f"Manifest check failed: {e}")
        return None, False

def test_reset_all_tasks(tasks):
    """Test reset endpoint for all tasks."""
    print("\n[RESET CHECK - All Tasks]")
    results = {"success": 0, "failed": 0, "tasks": []}
    
    for task_id in tasks:
        try:
            resp = requests.post(
                f"{BASE_URL}/reset",
                json={"task": task_id},
                timeout=5
            )
            resp.raise_for_status()
            data = resp.json()
            
            # Validate reset response
            assert 'session_id' in data, "Missing session_id"
            assert 'task' in data, "Missing task"
            assert 'state' in data, "Missing state"
            assert 'max_steps' in data, "Missing max_steps"
            
            results["success"] += 1
            results["tasks"].append({
                "task_id": task_id,
                "session_id": data['session_id'],
                "max_steps": data['max_steps'],
                "status": "OK"
            })
        except Exception as e:
            results["failed"] += 1
            results["tasks"].append({
                "task_id": task_id,
                "status": "FAILED",
                "error": str(e)
            })
    
    # Log results
    for task_info in results["tasks"]:
        if task_info["status"] == "OK":
            log_step("OK", f"{task_info['task_id']}: session created")
        else:
            log_step("ERROR", f"{task_info['task_id']}: {task_info.get('error', 'Unknown error')}")
    
    log_step("INFO", f"Reset tests: {results['success']}/{len(tasks)} PASSED")
    return results

def test_step_actions(task_results):
    """Test step endpoint with sample actions."""
    print("\n[STEP CHECK - Sample Actions]")
    results = {"success": 0, "failed": 0}
    
    # Test first successful reset for each domain
    tested_domains = set()
    for task_info in task_results["tasks"]:
        if task_info["status"] != "OK":
            continue
        
        task_id = task_info["task_id"]
        domain = task_id.split("_")[0]
        
        if domain in tested_domains:
            continue
        tested_domains.add(domain)
        
        try:
            session_id = task_info["session_id"]
            
            # Prepare domain-specific action
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
            
            resp = requests.post(
                f"{BASE_URL}/step",
                json={"action": action},
                params={"session_id": session_id},
                timeout=5
            )
            resp.raise_for_status()
            data = resp.json()
            
            # Validate step response
            assert 'reward' in data, "Missing reward"
            assert 0 <= data['reward'] <= 1, f"Reward out of range: {data['reward']}"
            assert 'done' in data, "Missing done flag"
            
            results["success"] += 1
            log_step("OK", f"{task_id}: step executed, reward={data['reward']:.4f}")
        except Exception as e:
            results["failed"] += 1
            log_step("ERROR", f"{task_id}: {str(e)}")
    
    log_step("INFO", f"Step tests: {results['success']}/{len(tested_domains)} PASSED")
    return results

def main():
    """Run all validation tests."""
    print("=" * 70)
    print("PHASE 1 VALIDATOR SIMULATION")
    print("=" * 70)
    
    # Ensure server is ready
    for i in range(5):
        try:
            resp = requests.get(f"{BASE_URL}/health", timeout=2)
            if resp.status_code == 200:
                break
        except:
            if i < 4:
                time.sleep(1)
            else:
                print("[✗] SERVER NOT RESPONDING - Startup failed")
                return 1
    
    # Run validation checks
    checks = []
    
    # 1. Health check
    checks.append(("Health", test_health()))
    
    # 2. Manifest check
    tasks, manifest_ok = test_manifest()
    checks.append(("Manifest", manifest_ok))
    
    if not manifest_ok or not tasks:
        print("\n" + "=" * 70)
        print("VALIDATION FAILED - Cannot proceed without valid manifest")
        return 1
    
    # 3. Reset check for all tasks
    reset_results = test_reset_all_tasks(tasks)
    checks.append(("Reset All", reset_results["failed"] == 0))
    
    # 4. Step check  
    step_results = test_step_actions(reset_results)
    checks.append(("Step Actions", step_results["failed"] == 0))
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    for check_name, status in checks:
        symbol = "✓" if status else "✗"
        print(f"{symbol} {check_name}")
    
    total_passed = sum(1 for _, status in checks if status)
    print(f"\nResult: {total_passed}/{len(checks)} checks passed")
    
    if total_passed == len(checks):
        print("\n✓ PHASE 1 VALIDATION PASSED!")
        print("System is ready for deployment")
        return 0
    else:
        print("\n✗ PHASE 1 VALIDATION FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
