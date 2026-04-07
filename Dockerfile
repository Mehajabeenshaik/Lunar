FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml setup.py* README.md* ./
COPY warehouse_env/ ./warehouse_env/
COPY run_server.py inference.py ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Health check (check both ports for flexibility)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:7860/health || curl -f http://localhost:5000/health || exit 1

# HF Spaces uses port 7860, but allow override via PORT env var
ENV PORT=7860
EXPOSE 7860

# Default command: start API server
CMD ["python", "run_server.py"]
