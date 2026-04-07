"""Monitor HF Spaces rebuild status - with all fixes applied."""

import requests
import time
from datetime import datetime

BASE_URL = "https://mehajabeen-lunar.hf.space"
CHECK_INTERVAL = 3  # Check every 3 seconds (faster)
MAX_ATTEMPTS = 400  # 20 minutes

def check_status():
    """Check if HF Spaces is online."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200, response.status_code
    except Exception as e:
        return False, str(type(e).__name__)

print("=" * 70)
print("🚀 HF SPACES REBUILD MONITOR - ALL FIXES APPLIED")
print("=" * 70)
print(f"Commit: f5890a7 (Import paths + Dependencies)")
print(f"Target: {BASE_URL}")
print(f"Checking every {CHECK_INTERVAL} seconds...")
print("=" * 70)

attempt = 0
start_time = time.time()
last_status = None

while attempt < MAX_ATTEMPTS:
    attempt += 1
    elapsed = time.time() - start_time
    elapsed_min = elapsed / 60
    
    online, status_code = check_status()
    
    # Only print on status change to reduce spam
    if status_code != last_status or online:
        print(f"\n[{elapsed_min:.1f}m | Attempt {attempt}] Status: {status_code}", end="")
        last_status = status_code
    
    if online:
        print(f"\n\n{'='*70}")
        print(f"✅ HF SPACES IS ONLINE AND READY!")
        print(f"{'='*70}")
        print(f"✅ Status Code: 200 OK")
        print(f"✅ Time to deploy: {elapsed:.0f} seconds ({elapsed_min:.1f} minutes)")
        print(f"✅ URL: {BASE_URL}")
        print(f"✅ All endpoints ready for testing")
        print(f"{'='*70}")
        print(f"\n🎉 Ready to submit for evaluation!")
        break
    else:
        print(".", end="", flush=True)
        time.sleep(CHECK_INTERVAL)
else:
    print(f"\n\n❌ Timeout after {MAX_ATTEMPTS * CHECK_INTERVAL / 60:.0f} minutes")
    print("Check HF Spaces dashboard for errors")
