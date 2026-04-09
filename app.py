"""FastAPI app wrapper for HF Spaces deployment."""

import os
import sys
import traceback
from pathlib import Path

# Add project root to path for proper imports
sys.path.insert(0, str(Path(__file__).parent))

print("[DEBUG] Starting app.py...")
print(f"[DEBUG] Python path: {sys.path[:2]}")

try:
    print("[DEBUG] Importing FastAPI app from server_multi_domain...")
    from warehouse_env.warehouse_env.server_multi_domain import app as fastapi_app
    app = fastapi_app  # Export as module-level variable for uvicorn
    print("[DEBUG] App imported successfully!")
except Exception as e:
    print(f"[ERROR] Failed to import app: {e}")
    print(f"[ERROR] Traceback:")
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"[DEBUG] Starting uvicorn on {host}:{port}...")
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"[ERROR] Failed to start uvicorn: {e}")
        traceback.print_exc()
        sys.exit(1)
