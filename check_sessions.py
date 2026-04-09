#!/usr/bin/env python3
"""Check sessions endpoint."""

import requests

r = requests.get('http://localhost:7860/sessions')
print(f'Status: {r.status_code}')
print(f'Response text: {r.text[:500]}')
if r.status_code == 200:
    print(f'Data: {r.json()}')
