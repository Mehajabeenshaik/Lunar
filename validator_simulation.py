#!/usr/bin/env python3
"""
VALIDATOR SIMULATION - Exact Test of What Competition Uses
Tests boundary compliance exactly as the validator would
"""

import sys
import traceback
from pathlib import Path

def test_direct_grader_import():
    """Test 1: Direct grader import (how validator might call it)"""
    print("\n" + "="*70)
    print("TEST 1: DIRECT GRADER IMPORT")
    print("="*70)
    
    try:
        # This is how the validator likely imports
        from content_moderation_env import ModeratorGrader
        
        grader = ModeratorGrader()
        
        print(f"✓ Grader imported: {grader.__class__.__name__}")
        print(f"✓ Grader module: {grader.__class__.__module__}")
        
        # Test all 30 tasks
        all_safe = True
        boundary_violations = []
        
        for task_id in range(1, 31):
            try:
                # Simple test data
                prediction = {
                    "category": "safe",
                    "severity": 3,
                    "action": "none",
                    "reasoning": "Test",
                    "confidence": 0.5
                }
                ground_truth = {
                    "category": "safe",
                    "severity": 3,
                    "action": "none"
                }
                
                score = grader.grade(task_id, prediction, ground_truth)
                
                # Check if EXACTLY 0.0 or 1.0
                score_str = str(score)
                if score_str in ["0.0", "1.0"]:
                    print(f"❌ Task {task_id}: {score} (STRING RE: exact boundary!)")
                    boundary_violations.append((task_id, score, "exact_string"))
                    all_safe = False
                elif score <= 0.0:
                    print(f"❌ Task {task_id}: {score} (NUMERIC: <= 0.0)")
                    boundary_violations.append((task_id, score, "<= 0.0"))
                    all_safe = False
                elif score >= 1.0:
                    print(f"❌ Task {task_id}: {score} (NUMERIC: >= 1.0)")
                    boundary_violations.append((task_id, score, ">= 1.0"))
                    all_safe = False
                else:
                    print(f"✓ Task {task_id}: {score}")
                    
            except Exception as e:
                print(f"❌ Task {task_id}: ERROR - {e}")
                all_safe = False
        
        if all_safe:
            print(f"\n✅ PASS: All 30 tasks have boundary-safe scores")
            return True
        else:
            print(f"\n❌ FAIL: {len(boundary_violations)} tasks have boundary violations:")
            for tid, score, issue in boundary_violations:
                print(f"    Task {tid}: {score} ({issue})")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        traceback.print_exc()
        return False


def test_grader_via_environment():
    """Test 2: Via environment.step() (API flow)"""
    print("\n" + "="*70)
    print("TEST 2: VIA ENVIRONMENT (API FLOW)")
    print("="*70)
    
    try:
        from content_moderation_env import ContentModerationEnv
        
        all_safe = True
        
        for task_id in [1, 5, 10, 15, 20, 25, 30]:  # Sample tasks
            try:
                env = ContentModerationEnv(task_id=task_id)
                obs = env.reset()
                
                # Make dummy action
                action = {
                    "category": "safe",
                    "severity": 3,
                    "action": "none"
                }
                
                obs, reward, done, info = env.step(action)
                
                if reward <= 0.0 or reward >= 1.0:
                    print(f"❌ Task {task_id}: reward={reward} (out of bounds)")
                    all_safe = False
                else:
                    print(f"✓ Task {task_id}: reward={reward}")
                    
            except Exception as e:
                print(f"❌ Task {task_id}: ERROR - {e}")
                all_safe = False
        
        if all_safe:
            print(f"\n✅ PASS: Environment returns boundary-safe rewards")
            return True
        else:
            print(f"\n❌ FAIL: Environment returned out-of-bounds values")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        traceback.print_exc()
        return False


def test_json_serialization():
    """Test 3: JSON serialization (how API returns values)"""
    print("\n" + "="*70)
    print("TEST 3: JSON SERIALIZATION")
    print("="*70)
    
    try:
        import json
        
        # Test values that might be at boundaries
        test_values = [
            0.0, 0.001, 0.01, 0.5, 0.99, 0.999, 0.9999, 1.0
        ]
        
        all_safe = True
        
        for val in test_values:
            # Simulate JSON round-trip
            json_str = json.dumps({"reward": val})
            parsed = json.loads(json_str)
            parsed_val = parsed["reward"]
            
            # Check if it's still exactly 0.0 or 1.0
            if parsed_val == 0.0 or parsed_val == 1.0:
                print(f"❌ JSON {val} -> {parsed_val} (boundary in JSON!)")
                all_safe = False
            else:
                print(f"✓ JSON {val} -> {parsed_val}")
        
        if all_safe:
            print(f"\n✅ PASS: JSON serialization preserves boundary safety")
            return True
        else:
            print(f"\n❌ FAIL: JSON serialization caused boundary violations")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        traceback.print_exc()
        return False


def test_manifest_vs_reality():
    """Test 4: Manifest claims vs actual behavior"""
    print("\n" + "="*70)
    print("TEST 4: MANIFEST VS REALITY")
    print("="*70)
    
    try:
        from app import get_manifest
        
        manifest = get_manifest()
        print(f"Manifest reward range: {manifest.get('reward_range')}")
        print(f"Manifest tasks: {manifest.get('tasks')}")
        
        # Check if manifest matches actual grader
        from content_moderation_env import ModeratorGrader
        grader = ModeratorGrader()
        
        # The manifest claims 30 tasks
        if manifest.get('tasks') == 30:
            print("✓ Manifest claims 30 tasks")
            
            # Verify all 30 are actually graded
            missing = []
            for task_id in range(1, 31):
                try:
                    score = grader.grade(task_id, {}, {})
                    if score is None:
                        missing.append(task_id)
                except:
                    missing.append(task_id)
            
            if missing:
                print(f"❌ Missing graders for tasks: {missing}")
                return False
            else:
                print("✓ All 30 tasks have graders")
                return True
        else:
            print(f"❌ Manifest claims {manifest.get('tasks')} tasks but should be 30")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*70)
    print("LUNAR VALIDATOR SIMULATION - COMPREHENSIVE BOUNDARY TEST")
    print("="*70)
    
    tests = [
        ("Direct Grader Import", test_direct_grader_import),
        ("Environment Flow", test_grader_via_environment),
        ("JSON Serialization", test_json_serialization),
        ("Manifest vs Reality", test_manifest_vs_reality),
    ]
    
    results = {}
    for test_name, test_func in tests:
        result = test_func()
        results[test_name] = result
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - Code should pass validator")
    else:
        print("\n❌ SOME TESTS FAILED - Code will fail validator")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
