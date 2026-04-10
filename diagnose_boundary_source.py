#!/usr/bin/env python3
"""
EXHAUSTIVE SEARCH for any remaining 0.0 or 1.0 hardcoded values
This will check the actual Python files for any boundary values
"""

import os
import re
from pathlib import Path

def search_boundaries(filepath):
    """Search file for any 0.0 or 1.0 that are NOT in comments/strings"""
    violations = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        return violations
    
    for line_num, line in enumerate(lines, 1):
        # Skip comments
        if line.strip().startswith('#'):
            continue
        
        # Remove inline comments for cleaner analysis
        code_part = line.split('#')[0]
        
        # Look for problematic patterns:
        # 1. return 0.0 (with word boundary)
        # 2. return 1.0 (with word boundary)
        # 3. = 0.0 (assignment)
        # 4. = 1.0 (assignment)
        
        patterns = [
            (r'\breturn\s+0\.0\b', 'return 0.0'),
            (r'\breturn\s+1\.0\b', 'return 1.0'),
            (r'[=:]\s*0\.0\b', '= 0.0 (assignment)'),
            (r'[=:]\s*1\.0\b', '= 1.0 (assignment)'),
            # Also check for division that results in exact 0 or 1
            (r'\/\s*\d+\.0\b', 'division by X.0'),
        ]
        
        for pattern, description in patterns:
            if re.search(pattern, code_part):
                violations.append({
                    'file': filepath,
                    'line': line_num,
                    'code': line.rstrip(),
                    'pattern': description
                })
    
    return violations

# Search all Python files
print("="*80)
print("EXHAUSTIVE BOUNDARY VALUE SEARCH")
print("="*80)

all_violations = []

for root, dirs, files in os.walk(Path('c:\\Users\\HP\\Documents\\lunar')):
    # Skip .git, __pycache__, etc.
    dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules']]
    
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            violations = search_boundaries(filepath)
            all_violations.extend(violations)

# Print results
if all_violations:
    print(f"\n❌ FOUND {len(all_violations)} POTENTIAL BOUNDARY VIOLATIONS:\n")
    
    # Group by file
    by_file = {}
    for v in all_violations:
        if v['file'] not in by_file:
            by_file[v['file']] = []
        by_file[v['file']].append(v)
    
    for filepath in sorted(by_file.keys()):
        violations = by_file[filepath]
        print(f"\n{filepath}:")
        for v in violations:
            print(f"  Line {v['line']:3d}: {v['pattern']}")
            print(f"           {v['code'][:100]}")
else:
    print("\n✅ NO OBVIOUS BOUNDARY VIOLATIONS FOUND IN CODE")

# Extra check: import and test graders directly
print("\n" + "="*80)
print("TESTING GRADERS DIRECTLY FOR BOUNDARY OUTPUTS")
print("="*80)

import sys
sys.path.insert(0, 'c:\\Users\\HP\\Documents\\lunar')

try:
    from content_moderation_env.graders import ModeratorGrader
    
    grader = ModeratorGrader()
    boundary_outputs = []
    
    test_cases = [
        (1, {'category': 'safe'}, {'category': 'safe'}, "task1_match"),
        (1, {'category': 'hate'}, {'category': 'safe'}, "task1_mismatch"),
        (10, {'safety': 'safe'}, {'safety': 'safe'}, "task10_match"),
        (10, {'safety': 'explicit'}, {'safety': 'safe'}, "task10_mismatch"),
        (14, {'workplace': True, 'home': True, 'public': True}, 
             {'workplace': True, 'home': True, 'public': True}, "task14_perfect"),
        (14, {'workplace': False, 'home': False, 'public': False},
             {'workplace': True, 'home': True, 'public': True}, "task14_none"),
    ]
    
    print("\nTesting sample tasks:")
    for task_id, pred, gt, desc in test_cases:
        try:
            score = grader.grade(task_id, pred, gt)
            is_boundary = (score == 0.0 or score == 1.0)
            status = "❌ BOUNDARY!" if is_boundary else "✓"
            print(f"  Task {task_id:2d} {desc:25s}: {score:.6f} {status}")
            
            if is_boundary:
                boundary_outputs.append({
                    'task': task_id,
                    'test': desc,
                    'score': score
                })
        except Exception as e:
            print(f"  Task {task_id:2d} {desc:25s}: ERROR - {e}")
    
    if boundary_outputs:
        print(f"\n⚠️  Found {len(boundary_outputs)} boundary outputs from grader!")
        for b in boundary_outputs:
            print(f"    Task {b['task']}: {b['score']} ({b['test']})")
    else:
        print("\n✅ Grader outputs all safe (no exact 0.0 or 1.0)")
        
except Exception as e:
    print(f"❌ Error testing graders: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
