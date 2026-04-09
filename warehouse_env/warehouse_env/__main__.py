"""Main entry point for comprehensive multi-domain environment."""

import sys
from warehouse_env.server_multi_domain import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
