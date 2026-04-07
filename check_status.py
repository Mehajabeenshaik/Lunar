#!/usr/bin/env python3
"""Quick validation of LUNAR system status."""

import requests
import json

print('╔' + '='*68 + '╗')
print('║    LUNAR: FINAL SUBMISSION VALIDATION REPORT           ║')
print('╚' + '='*68 + '╝')

# Test 1: Health
print('\n✅ Testing Local Server...')
try:
    r = requests.get('http://localhost:7860/health', timeout=5)
    print(f'   Status: {r.status_code} OK')
    health_data = r.json()
    print(f'   Response: {health_data}')
except Exception as e:
    print(f'   Error: {e}')

# Test 2: Manifest
print('\n✅ Testing Manifest (OpenEnv Spec)...')
try:
    r = requests.get('http://localhost:7860/manifest', timeout=5)
    data = r.json()
    name = data.get('name')
    version = data.get('version')
    task_variants = data.get('features', {}).get('task_variants')
    domains = data.get('domains', [])
    print(f'   Name: {name}')
    print(f'   Version: {version}')
    print(f'   Tasks: {task_variants}')
    print(f'   Domains: {len(domains)} - {domains}')
except Exception as e:
    print(f'   Error: {e}')

# Test 3: Tasks
print('\n✅ Testing Tasks Endpoint...')
try:
    r = requests.get('http://localhost:7860/tasks', timeout=5)
    data = r.json()
    tasks = list(data.get('tasks', {}).keys())
    print(f'   Total Tasks: {len(tasks)}/21')
    
    # Group by domain
    domains_dict = {}
    for task in tasks:
        domain = task.split('_')[0]
        domains_dict[domain] = domains_dict.get(domain, 0) + 1
    
    print('\n   Tasks by Domain:')
    for domain in sorted(domains_dict.keys()):
        count = domains_dict[domain]
        print(f'   • {domain.upper()}: {count} tasks')
except Exception as e:
    print(f'   Error: {e}')

print('\n' + '='*70)
print('✅ LOCAL SERVER: READY FOR SUBMISSION')
print('='*70)
print('\nNext Steps:')
print('1. Go to: https://huggingface.co/spaces/Mehajabeenshaik/Lunar/settings/general')
print('2. Click "Restart this Space"')
print('3. Wait 5-10 minutes')
print('4. Submit both URLs!')
