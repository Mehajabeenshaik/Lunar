#!/usr/bin/env python3
"""
COMPREHENSIVE LUNAR BOUNDARY AUDIT
Scans all Python files for boundary violations (0.0, 1.0 returns)
Compares with APEX to find architectural differences
"""

import os
import re
import sys
from pathlib import Path

def scan_file_for_boundaries(filepath):
    """Scan file for boundary violations"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except:
        return []
    
    violations = []
    lines = content.split('\n')
    
    # Look for direct 0.0 or 1.0 returns/assignments
    patterns = [
        (r'return\s+0\.0\b', 'direct return 0.0'),
        (r'return\s+1\.0\b', 'direct return 1.0'),
        (r'\s=\s+0\.0\b', 'assignment 0.0'),
        (r'\s=\s+1\.0\b', 'assignment 1.0'),
        (r'elif.*else\s+0\.0', 'conditional 0.0'),
        (r'elif.*else\s+1\.0', 'conditional 1.0'),
        (r'min\(1\.0,', 'min(1.0, ...) - can produce 1.0'),
        (r'max\(0\.0,', 'max(0.0, ...) - can produce 0.0'),
    ]
    
    for i, line in enumerate(lines, 1):
        for pattern, issue in patterns:
            if re.search(pattern, line):
                violations.append({
                    'line': i,
                    'code': line.strip(),
                    'issue': issue,
                    'file': filepath
                })
    
    return violations

def check_grader_returns():
    """Import and test actual grader functions"""
    print("\n" + "="*70)
    print("TESTING ACTUAL GRADER RETURNS")
    print("="*70)
    
    try:
        from content_moderation_env.graders import ModeratorGrader as OptimizedGrader
        
        # Test data
        test_cases = [
            ({"category": "safe"}, {"category": "safe"}, "Task 1: Match"),
            ({"category": "violent"}, {"category": "safe"}, "Task 1: Mismatch"),
        ]
        
        grader = OptimizedGrader()
        all_safe = True
        
        for i in range(1, 31):
            try:
                # Create dummy prediction and ground truth
                pred = {"category": "safe", "severity": 3, "action": "none", "reasoning": "This is safe content"}
                gt = {"category": "safe", "severity": 3, "action": "none", "reasoning": "This is safe content"}
                
                # Call grader
                score = grader.grade(i, pred, gt)
                
                # Check bounds
                if score <= 0.0 or score >= 1.0:
                    print(f"❌ Task {i}: score={score} (OUT OF BOUNDS!)")
                    all_safe = False
                else:
                    print(f"✓ Task {i}: score={score}")
                    
            except Exception as e:
                print(f"❌ Task {i}: ERROR - {e}")
                all_safe = False
        
        if all_safe:
            print("\n✅ ALL GRADER RETURNS ARE BOUNDARY-SAFE")
        else:
            print("\n⚠️  SOME GRADER RETURNS ARE OUT OF BOUNDS")
            
        return all_safe
        
    except Exception as e:
        print(f"ERROR: Could not test graders: {e}")
        return False

def analyze_python_files():
    """Scan all Python files in project"""
    print("\n" + "="*70)
    print("SCANNING ALL PYTHON FILES FOR BOUNDARY VIOLATIONS")
    print("="*70)
    
    root = Path("c:\\Users\\HP\\Documents\\lunar")
    py_files = list(root.rglob("*.py"))
    
    all_violations = []
    
    for pyfile in sorted(py_files):
        # Skip test/debug files
        if any(x in str(pyfile) for x in ['__pycache__', 'test_', 'debug_', 'diagnose_']):
            continue
            
        violations = scan_file_for_boundaries(str(pyfile))
        if violations:
            all_violations.extend(violations)
            relpath = pyfile.relative_to(root)
            print(f"\n{relpath}:")
            for v in violations:
                print(f"  Line {v['line']}: {v['issue']}")
                print(f"    {v['code']}")
    
    return all_violations

def check_environment_step():
    """Check environment.py step function for reward clamping"""
    print("\n" + "="*70)
    print("CHECKING ENVIRONMENT.PY STEP FUNCTION")
    print("="*70)
    
    env_file = "c:\\Users\\HP\\Documents\\lunar\\content_moderation_env\\environment.py"
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Check if step function clamps reward
        if 'def step(' in content:
            print("✓ step() function found")
            
            # Look for clamping logic
            if 'min(' in content and 'max(' in content:
                print("✓ Clamping logic found (min/max)")
            else:
                print("⚠️  No obvious clamping logic in step()")
            
            # Check for exact boundaries
            if 'reward <= 0' in content or 'reward <= 0.0' in content:
                print("✓ Checks for <= 0 boundary")
            if 'reward >= 1' in content or 'reward >= 1.0' in content:
                print("✓ Checks for >= 1 boundary")
                
    except Exception as e:
        print(f"ERROR: Could not check environment: {e}")

def main():
    print("\n" + "="*70)
    print("LUNAR BOUNDARY VIOLATION AUDIT - COMPREHENSIVE SCAN")
    print("="*70)
    
    # 1. Scan all Python files
    violations = analyze_python_files()
    
    # 2. Test actual graders
    graders_safe = check_grader_returns()
    
    # 3. Check environment clamping
    check_environment_step()
    
    # 4. Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total violations found: {len(violations)}")
    print(f"Graders boundary-safe: {graders_safe}")
    
    if violations:
        print("\n⚠️  VIOLATIONS DETECTED:")
        for v in violations:
            print(f"  {Path(v['file']).name}:{v['line']} - {v['issue']}")
    
    print("\n" + "="*70)
    print("APEX COMPARISON")
    print("="*70)
    print("""
APEX uses:
  - max(0.0, min(1.0, reward)) in _make_reward()
  - Multiple task domains with graders
  - Step returns (obs, reward, done, info)
  - SQLite session storage

LUNAR uses:
  - Similar clamping in graders.py
  - 30 tasks across 7 domains
  - Step returns (observation, reward, done, info)
  - In-memory session storage

KEY DIFFERENCE TO CHECK:
  Is the validator calling graders directly (would be affected by any 0.0/1.0 in code)
  OR going through the API (would receive JSON which we clamp)?
""")

if __name__ == "__main__":
    main()
