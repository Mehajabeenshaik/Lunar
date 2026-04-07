"""FastAPI ASGI app for OpenEnv multi-mode deployment."""

import os
import sys
from pathlib import Path

# Add warehouse_env to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "warehouse_env"))

# Import and expose the FastAPI app
from warehouse_env.server import app


def main():
    """Main entry point for server execution."""
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)


# Ensure this is the ASGI application
__all__ = ["app", "main"]

if __name__ == "__main__":
    main()
