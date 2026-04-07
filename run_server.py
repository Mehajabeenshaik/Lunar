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
    
    logger.info(f"Starting LUNAR server on {host}:{port}")
    logger.info(f"Environment: {'Development (reload=True)' if reload else 'Production'}")
    
    # Production settings for HF Spaces - simplified for stability
    try:
        uvicorn.run(
            "warehouse_env.server:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info",
            access_log=True,
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

