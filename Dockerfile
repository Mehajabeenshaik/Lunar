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
COPY inference.py .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose API port
EXPOSE 5000

# Default command: start API server with uvicorn
CMD ["python", "-m", "uvicorn", "warehouse_env.server:app", "--host", "0.0.0.0", "--port", "5000"]
