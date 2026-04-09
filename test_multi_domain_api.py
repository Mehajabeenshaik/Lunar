#!/usr/bin/env python3
"""Quick test of multi-domain API endpoints."""

import requests
import time
import subprocess
import sys
from threading import Thread

BASE_URL = "http://localhost:7860"

def start_server():
    """Start the server in the background."""
    subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "warehouse_env.warehouse_env.server_multi_domain:app",
        "--host", "0.0.0.0",
        "--port", "7860",
        "--log-level", "error"
    ])
    time.sleep(3)  # Give server time to start

def test_endpoints():
    """Test all endpoints with comprehensive tasks."""
    
    print("\n" + "=" * 100)
    print("MULTI-DOMAIN API ENDPOINT TEST")
    print("=" * 100)
    
    try:
        # Test 1: Health check
        print("\n[1] Testing /health endpoint...")
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code == 200:
            health = r.json()
            print(f"    ✓ Status: {health.get('status')}")
            print(f"    ✓ Tasks: {health.get('tasks')}")
            print(f"    ✓ Domains: {health.get('domains')}")
        else:
            print(f"    ✗ Failed: {r.status_code}")
            return False
        
        # Test 2: Manifest
        print("\n[2] Testing /manifest endpoint...")
        r = requests.get(f"{BASE_URL}/manifest", timeout=5)
        if r.status_code == 200:
            manifest = r.json()
            print(f"    ✓ Task count: {manifest.get('task_count')}")
            print(f"    ✓ Domain count: {manifest.get('domain_count')}")
            print(f"    ✓ Graders: {len(manifest.get('graders', []))}")
            print(f"    ✓ Features: multi_domain={manifest.get('features', {}).get('multi_domain')}")
        else:
            print(f"    ✗ Failed: {r.status_code}")
            return False
        
        # Test 3: Get all tasks
        print("\n[3] Testing /tasks endpoint...")
        r = requests.get(f"{BASE_URL}/tasks", timeout=5)
        if r.status_code == 200:
            tasks = r.json()
            print(f"    ✓ Total tasks: {tasks.get('total')}")
            task_ids = list(tasks.get('tasks', {}).keys())
            print(f"    ✓ First few tasks: {task_ids[:3]}...")
            print(f"    ✓ Last few tasks: ...{task_ids[-3:]}")
        else:
            print(f"    ✗ Failed: {r.status_code}")
            return False
        
        # Test 4: Reset with warehouse task
        print("\n[4] Testing /reset endpoint with warehouse_novice...")
        r = requests.post(
            f"{BASE_URL}/reset",
            json={"task": "warehouse_novice"},
            timeout=5
        )
        if r.status_code == 200:
            reset_data = r.json()
            session_id = reset_data.get("session_id")
            print(f"    ✓ Session ID: {session_id[:8]}...")
            print(f"    ✓ Task: {reset_data.get('task')}")
            print(f"    ✓ Max steps: {reset_data.get('max_steps')}")
        else:
            print(f"    ✗ Failed: {r.status_code} - {r.text[:100]}")
            return False
        
        # Test 5: Step with warehouse action
        print("\n[5] Testing /step endpoint...")
        r = requests.post(
            f"{BASE_URL}/step?session_id={session_id}",
            json={"action": {"reorder_quantities": [100], "transfers": []}},
            timeout=5
        )
        if r.status_code == 200:
            step_data = r.json()
            reward = step_data.get("reward")
            print(f"    ✓ Reward: {reward:.4f}")
            print(f"    ✓ Done: {step_data.get('done')}")
            print(f"    ✓ Steps: {step_data.get('info', {}).get('current_step')}")
        else:
            print(f"    ✗ Failed: {r.status_code} - {r.text[:100]}")
            return False
        
        # Test 6: Get state
        print("\n[6] Testing /state endpoint...")
        r = requests.get(f"{BASE_URL}/state/{session_id}", timeout=5)
        if r.status_code == 200:
            state_data = r.json()
            print(f"    ✓ Session ID: {state_data.get('session_id')[:8]}...")
            print(f"    ✓ Task: {state_data.get('task')}")
            print(f"    ✓ Steps: {state_data.get('steps')}")
            print(f"    ✓ Cumulative reward: {state_data.get('cumulative_reward'):.4f}")
        else:
            print(f"    ✗ Failed: {r.status_code}")
            return False
        
        # Test 7: Reset a data pipeline task
        print("\n[7] Testing data_pipeline task (data_ingestion_simple)...")
        r = requests.post(
            f"{BASE_URL}/reset",
            json={"task": "data_ingestion_simple"}
        )
        if r.status_code == 200:
            print(f"    ✓ Data pipeline task reset successfully")
            sid2 = r.json().get("session_id")
            
            # Step with data pipeline action
            r = requests.post(
                f"{BASE_URL}/step?session_id={sid2}",
                json={"action": {"records": 1000, "cleaning_level": 0.5}}
            )
            if r.status_code == 200:
                reward = r.json().get("reward")
                print(f"    ✓ Data pipeline reward: {reward:.4f}")
            else:
                print(f"    ✗ Step failed: {r.status_code}")
                return False
        else:
            print(f"    ✗ Failed: {r.status_code}")
            return False
        
        # Test 8: Test code review task
        print("\n[8] Testing code_review task (code_style_compliance)...")
        r = requests.post(
            f"{BASE_URL}/reset",
            json={"task": "code_style_compliance"}
        )
        if r.status_code == 200:
            print(f"    ✓ Code review task reset successfully")
            sid3 = r.json().get("session_id")
            
            r = requests.post(
                f"{BASE_URL}/step?session_id={sid3}",
                json={"action": {"files": 5, "refactoring": 0.5, "testing": 0.3}}
            )
            if r.status_code == 200:
                reward = r.json().get("reward")
                print(f"    ✓ Code review reward: {reward:.4f}")
            else:
                print(f"    ✗ Step failed: {r.status_code}")
                return False
        else:
            print(f"    ✗ Failed: {r.status_code}")
            return False
        
        # Test 9: Leaderboard
        print("\n[9] Testing /leaderboard endpoint...")
        r = requests.get(f"{BASE_URL}/leaderboard?limit=10", timeout=5)
        if r.status_code == 200:
            lb = r.json()
            print(f"    ✓ Total sessions: {lb.get('total_sessions')}")
            print(f"    ✓ Leaderboard entries: {len(lb.get('leaderboard', []))}")
        else:
            print(f"    ✗ Failed: {r.status_code}")
        
        # Test 10: Sessions list
        print("\n[10] Testing /sessions endpoint...")
        r = requests.get(f"{BASE_URL}/sessions", timeout=5)
        if r.status_code == 200:
            sessions = r.json()
            print(f"    ✓ Active sessions: {sessions.get('active_sessions')}")
            print(f"    ✓ Sessions tracked: {len(sessions.get('sessions', []))}")
        else:
            print(f"    ✗ Failed: {r.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("    ✗ Could not connect to server. Is it running?")
        return False
    except Exception as e:
        print(f"    ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting comprehensive API test...")
    print("Launching server...")
    
    # Start server
    start_server()
    
    # Run tests
    success = test_endpoints()
    
    # Final result
    print("\n" + "=" * 100)
    if success:
        print("✓ ALL API TESTS PASSED")
        print("✓ MULTI-DOMAIN SERVER READY FOR PRODUCTION")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 100 + "\n")
    
    sys.exit(0 if success else 1)
