"""Run warehouse environment server."""

import os
import sys
import uvicorn

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "7860"))  # HF Spaces uses 7860
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    uvicorn.run(
        "warehouse_env.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )
