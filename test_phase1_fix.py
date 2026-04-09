#!/usr/bin/env python3
"""Quick test that Phase 1 checks pass"""

import requests
import subprocess
import time
import sys
from threading import Thread

BASE_URL = "http://localhost:7860"

def start_server():
    """Start server in background"""
    subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "warehouse_env.warehouse_env.server:app",
        "--host", "0.0.0.0",
        "--port", "7860",
        "--log-level", "error"
    ])
    time.sleep(2)

def test_phase1():
    """Test Phase 1 checks"""
    
    print("\n" + "=" * 80)
    print("PHASE 1 TEST - OpenEnv Reset Check")
    print("=" * 80)
    
    try:
        # Test 1: Health
        print("\n[1] Health Check...")
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code == 200:
            print("    ✓ /health: OK")
        else:
            print(f"    ✗ /health failed: {r.status_code}")
            return False
        
        # Test 2: Manifest
        print("\n[2] Manifest Check...")
        r = requests.get(f"{BASE_URL}/manifest", timeout=5)
        if r.status_code == 200:
            m = r.json()
            print(f"    ✓ /manifest: OK")
            print(f"      - Tasks: {len(m.get('tasks', []))}")
            print(f"      - Graders: {len(m.get('graders', []))}")
        else:
            print(f"    ✗ /manifest failed: {r.status_code}")
            return False
        
        # Test 3: Reset warehouse_easy
        print("\n[3] Reset warehouse_easy...")
        r = requests.post(
            f"{BASE_URL}/reset",
            json={"task": "warehouse_easy"},
            timeout=5
        )
        if r.status_code == 200:
            data = r.json()
            print(f"    ✓ /reset warehouse_easy: OK")
            print(f"      - Session ID: {data.get('session_id', 'N/A')[:8]}...")
            print(f"      - Observation keys: {list(data.get('observation', {}).keys())}")
            session1 = data.get('session_id')
        else:
            print(f"    ✗ /reset warehouse_easy failed: {r.status_code}")
            print(f"    Response: {r.text}")
            return False
        
        # Test 4: Reset warehouse_medium
        print("\n[4] Reset warehouse_medium...")
        r = requests.post(
            f"{BASE_URL}/reset",
            json={"task": "warehouse_medium"},
            timeout=5
        )
        if r.status_code == 200:
            print(f"    ✓ /reset warehouse_medium: OK")
            session2 = r.json().get('session_id')
        else:
            print(f"    ✗ /reset warehouse_medium failed: {r.status_code}")
            print(f"    Response: {r.text}")
            return False
        
        # Test 5: Reset warehouse_hard
        print("\n[5] Reset warehouse_hard...")
        r = requests.post(
            f"{BASE_URL}/reset",
            json={"task": "warehouse_hard"},
            timeout=5
        )
        if r.status_code == 200:
            print(f"    ✓ /reset warehouse_hard: OK")
            session3 = r.json().get('session_id')
        else:
            print(f"    ✗ /reset warehouse_hard failed: {r.status_code}")
            print(f"    Response: {r.text}")
            return False
        
        # Test 6: Step on session1
        print("\n[6] Step on warehouse_easy session...")
        r = requests.post(
            f"{BASE_URL}/step?session_id={session1}",
            json={"reorder_quantities": [100], "transfers": []},
            timeout=5
        )
        if r.status_code == 200:
            step_data = r.json()
            reward = step_data.get('reward', -1)
            print(f"    ✓ /step: OK (reward={reward:.4f})")
        else:
            print(f"    ✗ /step failed: {r.status_code}")
            print(f"    Response: {r.text}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("    ✗ Could not connect to server")
        return False
    except Exception as e:
        print(f"    ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting Phase 1 test...")
    print("Launching server...")
    
    start_server()
    success = test_phase1()
    
    print("\n" + "=" * 80)
    if success:
        print("✓ PHASE 1 CHECKS SHOULD PASS")
    else:
        print("✗ PHASE 1 CHECKS WILL FAIL")
    print("=" * 80 + "\n")
    
    sys.exit(0 if success else 1)
