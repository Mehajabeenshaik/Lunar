#!/usr/bin/env python
"""COMPREHENSIVE AUDIT: LUNAR vs APEX - Find ALL Issues"""

import os
import sys

print("\n" + "="*90)
print("COMPREHENSIVE LUNAR vs APEX AUDIT - APRIL 10 DEADLINE")
print("="*90)

issues_found = []
fixes_needed = []

# 1. CHECK FILE STRUCTURE
print("\n[1] PROJECT FILE STRUCTURE")
print("-" * 90)

required_files = {
    "app.py": "Entry point (used by HF Spaces)",
    "models.py": "Pydantic models for API",
    "environment.py": "Core environment logic",
    "graders.py": "Deterministic reward calculators",
    "tasks.py": "Task definitions",
    "inference.py": "Baseline benchmark runner",
    "openenv.yaml": "OpenEnv v1 spec metadata",
    "Dockerfile": "Container definition",
    "requirements.txt": "Python dependencies",
    "README.md": "Complete documentation"
}

missing_files = []
for filename, description in required_files.items():
    if os.path.exists(f"/c/Users/HP/Documents/lunar/{filename}") or \
       os.path.exists(f"/c/Users/HP/Documents/lunar/warehouse_env/warehouse_env/{filename.replace('.py', '_base.py')}"):
        print(f"  ✅ {filename:20} - {description}")
    else:
        print(f"  ❌ {filename:20} - {description}")
        missing_files.append(filename)
        issues_found.append(f"Missing critical file: {filename}")

# 2. CHECK OPENENV.YAML
print("\n[2] openenv.yaml COMPLIANCE")
print("-" * 90)

try:
    import yaml
    with open("/c/Users/HP/Documents/lunar/openenv.yaml", "r") as f:
        spec = yaml.safe_load(f)
    
    required_fields = ["spec_version", "name", "version", "description", "type", "runtime", "app", "port"]
    for field in required_fields:
        if field in spec:
            print(f"  ✅ {field:20} = {str(spec[field])[:40]}")
        else:
            print(f"  ❌ {field:20} - MISSING")
            issues_found.append(f"openenv.yaml missing field: {field}")
    
    # Check app field specifically - APEX uses app.py, not app_gradio.py
    app_file = spec.get("app", "")
    if app_file == "app.py":
        print(f"  ✅ app field correct: app.py")
    else:
        print(f"  ❌ app field incorrect: {app_file} (should be app.py)")
        issues_found.append(f"openenv.yaml app field incorrect: {app_file}")
        
except Exception as e:
    print(f"  ❌ Cannot read openenv.yaml: {e}")
    issues_found.append("Cannot parse openenv.yaml")

# 3. CHECK APP.PY STRUCTURE
print("\n[3] app.py ENTRY POINT")
print("-" * 90)

try:
    with open("/c/Users/HP/Documents/lunar/app.py", "r") as f:
        content = f.read(500)
    
    if "from warehouse_env" in content or "import app" in content:
        print(f"  ✅ app.py exists and imports warehouse_env")
    else:
        print(f"  ⚠️  app.py structure unclear")
        
except Exception as e:
    print(f"  ❌ Cannot read app.py: {e}")
    issues_found.append("Cannot read app.py")

# 4. CHECK DOCKERFILE
print("\n[4] Dockerfile COMPATIBILITY")
print("-" * 90)

try:
    with open("/c/Users/HP/Documents/lunar/Dockerfile", "r") as f:
        dockerfile = f.read()
    
    checks = {
        "FROM python": "Base image defined",
        "WORKDIR": "Working directory set",
        "COPY": "Files copied",
        "RUN pip install": "Dependencies installed",
        "CMD [": "Startup command defined"
    }
    
    for check_str, description in checks.items():
        if check_str in dockerfile:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - MISSING")
            issues_found.append(f"Dockerfile missing: {check_str}")
            
except Exception as e:
    print(f"  ❌ Cannot read Dockerfile: {e}")
    issues_found.append("Cannot read Dockerfile")

# 5. CHECK MANIFEST ENDPOINT
print("\n[5] MANIFEST ENDPOINT SPECIFICATION")
print("-" * 90)

import requests
try:
    r = requests.get("http://localhost:7860/manifest", timeout=3)
    if r.status_code == 200:
        manifest = r.json()
        print(f"  ✅ /manifest returns 200")
        
        # Check for required fields
        required = ["tasks", "graders", "domains", "task_specs"]
        for field in required:
            if field in manifest:
                print(f"  ✅ Field '{field}' present")
            else:
                print(f"  ❌ Field '{field}' MISSING")
                issues_found.append(f"Manifest missing field: {field}")
        
        # Check task count
        tasks = manifest.get("tasks", [])
        graders = manifest.get("graders", [])
        print(f"  ✅ Tasks: {len(tasks)}, Graders: {len(graders)}")
        
        if len(tasks) < 3 or len(graders) < 3:
            issues_found.append(f"Insufficient tasks/graders: {len(tasks)} tasks, {len(graders)} graders")
            
    else:
        print(f"  ❌ /manifest returned {r.status_code}")
        issues_found.append(f"/manifest returned {r.status_code}")
        
except Exception as e:
    print(f"  ❌ Cannot reach /manifest: {e}")
    issues_found.append("Cannot reach /manifest endpoint")

# 6. CHECK INFERENCE.PY FORMAT
print("\n[6] inference.py LOG FORMAT")
print("-" * 90)

try:
    with open("/c/Users/HP/Documents/lunar/inference.py", "r") as f:
        inference = f.read()
    
    checks = {
        "[START]": "START log format",
        "[STEP]": "STEP log format",
        "[END]": "END log format"
    }
    
    for pattern, desc in checks.items():
        if pattern in inference:
            print(f"  ✅ {desc} present")
        else:
            print(f"  ❌ {desc} MISSING")
            issues_found.append(f"inference.py missing {pattern} format")
            
except Exception as e:
    print(f"  ❌ Cannot read inference.py: {e}")
    issues_found.append("Cannot read inference.py")

# 7. CHECK ENVIRONMENT VARIABLES
print("\n[7] ENVIRONMENT VARIABLES SUPPORT")
print("-" * 90)

try:
    with open("/c/Users/HP/Documents/lunar/inference.py", "r") as f:
        inference = f.read()
    
    required_env_vars = {
        "OPENAI_API_KEY": "LLM API key",
        "API_BASE_URL": "LLM proxy endpoint",
        "MODEL_NAME": "Model identifier",
        "HF_TOKEN": "HuggingFace token (optional)"
    }
    
    for var, desc in required_env_vars.items():
        if f'"{var}"' in inference or f"'{var}'" in inference or f".getenv" in inference:
            print(f"  ✅ {var:20} - {desc}")
        else:
            print(f"  ⚠️  {var:20} - May not be supported")
            
except Exception as e:
    print(f"  ⚠️  Cannot verify env vars: {e}")

# SUMMARY
print("\n" + "="*90)
print("ISSUES FOUND:")
print("="*90)

if issues_found:
    for i, issue in enumerate(issues_found, 1):
        print(f"{i}. {issue}")
else:
    print("✅ No critical issues found!")

print("\n" + "="*90)
print(f"TOTAL ISSUES: {len(issues_found)}")
print("="*90 + "\n")
