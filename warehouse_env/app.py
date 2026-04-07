#!/usr/bin/env bash
# app.py - Simple wrapper for HF Spaces

import os
import sys
from warehouse_env.server import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
