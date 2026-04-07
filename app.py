"""FastAPI app wrapper for HF Spaces deployment."""

import os
import sys
from pathlib import Path

# Add warehouse_env to path
sys.path.insert(0, str(Path(__file__).parent / "warehouse_env"))

# Import app
from warehouse_env.server import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
