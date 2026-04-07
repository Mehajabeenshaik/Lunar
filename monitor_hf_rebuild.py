#!/usr/bin/env python
"""Monitor HF Spaces rebuild and test deployment."""

import time
import requests
import json

print("=" * 60)
print("Monitoring HF Spaces Rebuild")
print("=" * 60)
print("Waiting for HF Spaces to rebuild...")
print("This may take 5-10 minutes\n")

base_url = "https://mehajabeen-lunar.hf.space"
max_attempts = 60  # 10 minutes with 10-second intervals
attempt = 0

while attempt < max_attempts:
    attempt += 1
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        
        if response.status_code == 200:
            print(f"✅ HF Spaces is ONLINE! (Attempt {attempt})")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}\n")
            
            # Test other endpoints
            try:
                tasks = requests.get(f"{base_url}/tasks", timeout=5).json()
                print(f"✅ Tasks endpoint working - {tasks.get('total', 0)} task variants")
            except:
                pass
                
            try:
                manifest = requests.get(f"{base_url}/manifest", timeout=5).json()
                print(f"✅ Manifest loaded - {manifest.get('name', 'Unknown')} v{manifest.get('version', '?')}")
            except:
                pass
            
            break
        else:
            print(f"⏳ Attempt {attempt}: Status {response.status_code} (rebuilding...)")
            
    except requests.exceptions.ConnectionError:
        print(f"⏳ Attempt {attempt}: Connection refused (rebuilding...)")
    except Exception as e:
        print(f"⏳ Attempt {attempt}: {str(e)[:50]}...")
    
    if attempt < max_attempts:
        time.sleep(10)

print()
if attempt >= max_attempts:
    print("❌ Timeout - HF Spaces did not come online")
else:
    print(f"✅ Deployment successful in {attempt * 10} seconds")
    print("=" * 60)
    print("All systems operational!")
    print("=" * 60)
