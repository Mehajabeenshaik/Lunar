"""FastAPI app wrapper for HF Spaces deployment."""

import os
import sys

# Try different import paths for compatibility
try:
    from warehouse_env.warehouse_env.server import app
except ImportError:
    try:
        from warehouse_env.server import app
    except ImportError:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "warehouse_env"))
        from warehouse_env.server import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
