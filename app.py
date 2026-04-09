"""FastAPI app wrapper for HF Spaces deployment."""

import os
import sys
from pathlib import Path

# Add project root to path for proper imports
sys.path.insert(0, str(Path(__file__).parent))

# Import app from the multi-domain server (32 tasks)
from warehouse_env.warehouse_env.server_multi_domain import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Run with uvicorn (production-grade ASGI server)
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
