"""Run LUNAR environment server with production settings."""

import os
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "7860"))  # HF Spaces uses 7860
    reload = os.getenv("RELOAD", "false").lower() == "true"
    workers = int(os.getenv("WORKERS", "1"))
    
    logger.info(f"Starting LUNAR server on {host}:{port}")
    logger.info(f"Environment: {'Development (reload=True)' if reload else 'Production'}")
    logger.info(f"Workers: {workers}")
    
    # Production settings for HF Spaces
    uvicorn.run(
        "warehouse_env.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True,
        timeout_keep_alive=30,
        timeout_notify=30,
    )

