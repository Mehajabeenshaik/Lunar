"""Monitor HF Spaces rebuild status."""

import requests
import time
from datetime import datetime

BASE_URL = "https://mehajabeen-lunar.hf.space"
CHECK_INTERVAL = 5  # seconds
MAX_ATTEMPTS = 240  # 20 minutes

def check_status():
    """Check if HF Spaces is online."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

print("=" * 60)
print("HF Spaces Rebuild Monitor")
print("=" * 60)
print(f"Checking: {BASE_URL}")
print(f"Interval: {CHECK_INTERVAL} seconds")
print(f"Timeout: {MAX_ATTEMPTS * CHECK_INTERVAL / 60:.1f} minutes")
print("=" * 60)

attempt = 0
start_time = time.time()

while attempt < MAX_ATTEMPTS:
    attempt += 1
    elapsed = time.time() - start_time
    
    status = check_status()
    
    if status:
        print(f"\n✅ HF SPACES IS ONLINE!")
        print(f"✅ Status: 200 OK")
        print(f"✅ Time elapsed: {elapsed:.0f} seconds ({elapsed/60:.1f} minutes)")
        print(f"\n🎉 Space ready for submission!")
        print(f"🎉 URL: {BASE_URL}")
        break
    else:
        elapsed_min = elapsed / 60
        print(f"⏳ Attempt {attempt}/{MAX_ATTEMPTS} ({elapsed_min:.1f}m) - Status: Rebuilding... ", end="\r")
        time.sleep(CHECK_INTERVAL)
else:
    print(f"\n❌ Timeout: Space did not come online after {MAX_ATTEMPTS * CHECK_INTERVAL / 60:.0f} minutes")
    print("Check HF Spaces dashboard for errors")
