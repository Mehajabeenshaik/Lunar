FROM python:3.11-slim

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY setup.py pyproject.toml README.md ./
COPY warehouse_env/ ./warehouse_env/
COPY run_server.py ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel &&  \
    pip install --no-cache-dir -e .

# Health check
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:7860/health || exit 1

# Expose port
ENV PORT=7860
EXPOSE 7860

# Run server
CMD ["python", "-u", "run_server.py"]
