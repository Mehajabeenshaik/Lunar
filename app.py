"""FastAPI app wrapper for HF Spaces deployment."""

import os
import sys
from warehouse_env.warehouse_env.server import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
