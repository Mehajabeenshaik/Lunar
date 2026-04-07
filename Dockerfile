FROM python:3.11-slim

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY warehouse_env/ ./warehouse_env/
COPY run_server.py ./

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir fastapi uvicorn pydantic numpy openai python-dotenv

# Health check with longer timeout for startup
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:7860/health || exit 1

# HF Spaces uses port 7860
ENV PORT=7860
ENV HOST=0.0.0.0
EXPOSE 7860

# Start server with production-grade settings
CMD ["python", "-u", "run_server.py"]
