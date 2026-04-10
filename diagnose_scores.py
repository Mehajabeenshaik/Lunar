#!/usr/bin/env python3
"""
Diagnostic script to identify EXACTLY what score values reach the API
Simulates validator behavior of parsing [STEP] logs and checking for boundaries
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import re
import subprocess
import json

print("="*80)
print("DIAGNOSTIC: Simulating Validator Score Extraction")
print("="*80)

# Run a test with explicit logging capture
print("\n1. Starting test environment...")
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

print("2. Capturing raw environment responses for all 30 tasks...")
print("-" * 80)

all_responses = []
violations = []

for task_id in range(1, 31):
    # Start session
    start_response = client.post("/session/start", json={"task_id": task_id})
    if start_response.status_code != 200:
        continue
    
    session_id = start_response.json().get("session_id")
    
    # Take 3 steps
    for step in range(3):
        step_response = client.post(
            f"/session/{session_id}/step",
            json={"session_id": session_id, "action": {"category": "safe"}}
        )
        if step_response.status_code == 200:
            raw_data = step_response.json()
            reward_value = raw_data.get('reward')
            
            # Record everything
            all_responses.append({
                'task_id': task_id,
                'step': step + 1,
                'raw_value': reward_value,
                'type': str(type(reward_value).__name__),
                'repr': repr(reward_value),
                'str': str(reward_value),
                'formatted_3f': f"{float(reward_value):.3f}" if reward_value is not None else "None"
            })
            
            # Check if boundary
            if reward_value is not None:
                rf = float(reward_value)
                if rf <= 0.0 or rf >= 1.0:
                    violations.append({
                        'task_id': task_id,
                        'step': step + 1,
                        'value': rf,
                        'reason': 'exact_boundary'
                    })
                
                # Check if string representation might look like boundary
                formatted = f"{rf:.3f}"
                if formatted in ["0.000", "1.000"]:
                    violations.append({
                        'task_id': task_id,
                        'step': step + 1,
                        'value': rf,
                        'formatted': formatted,
                        'reason': 'formatted_boundary'
                    })

print("\n3. ANALYSIS OF RAW RESPONSES:")
print("-" * 80)

# Group by task
task_summaries = {}
for resp in all_responses:
    tid = resp['task_id']
    if tid not in task_summaries:
        task_summaries[tid] = []
    task_summaries[tid].append(resp)

for task_id in range(1, 31):
    if task_id in task_summaries:
        responses = task_summaries[task_id]
        values = [float(r['raw_value']) for r in responses if r['raw_value'] is not None]
        if values:
            print(f"Task {task_id:2d}: min={min(values):.6f}, max={max(values):.6f}, avg={sum(values)/len(values):.6f}")
            print(f"           Raw values: {values}")
            
            # Show formatting
            for v in values:
                print(f"             {v:.6f} → .3f={v:.3f}, .0f={v:.0f}")

print("\n4. BOUNDARY VIOLATIONS FOUND:")
print("-" * 80)

if violations:
    print(f"⚠️  {len(violations)} POTENTIAL VIOLATIONS DETECTED:")
    for v in violations[:10]:
        print(f"  Task {v['task_id']}, Step {v['step']}: {v['value']} ({v['reason']})")
        if 'formatted' in v:
            print(f"    When formatted to 3 decimals: {v['formatted']}")
else:
    print("✓ No boundary violations detected")

print("\n5. HARDCODED VALUE CHECK:")
print("-" * 80)

# Check if any exact 0.0 or 1.0 values appear
exact_zeros = [r for r in all_responses if r['raw_value'] == 0.0]
exact_ones = [r for r in all_responses if r['raw_value'] == 1.0]

if exact_zeros:
    print(f"⚠️  Found {len(exact_zeros)} exact 0.0 values!")
    for r in exact_zeros[:3]:
        print(f"  Task {r['task_id']}, Step {r['step']}")

if exact_ones:
    print(f"⚠️  Found {len(exact_ones)} exact 1.0 values!")
    for r in exact_ones[:3]:
        print(f"  Task {r['task_id']}, Step {r['step']}")

if not exact_zeros and not exact_ones:
    print("✓ No exact 0.0 or 1.0 values in API responses")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

if violations:
    print("❌ ISSUES DETECTED - Validator would likely reject")
    print(f"\n   {len(violations)} violations found in score range")
else:
    print("✅ ALL CHECKS PASSED - API responses should be valid")
    print("\n   If still failing, issue is likely:")
    print("   - Validator not calling /session API")
    print("   - Validator calling different code path")
    print("   - Docker/deployment caching issue")

print("="*80)
