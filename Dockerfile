FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=7860
ENV HOST=0.0.0.0

# Copy entire project
COPY . .

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade \
    pip \
    setuptools \
    wheel && \
    pip install --no-cache-dir -r requirements.txt

# Install openai for inference.py
RUN pip install --no-cache-dir openai>=1.3.0

# Verify installation
RUN python -c "import fastapi; import uvicorn; import pydantic; print('✓ All dependencies installed')"

# Test app imports
RUN python -c "from app import app; print('✓ App imports successfully')"

# Health check with proper timeout
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=2 \
    CMD curl -f http://localhost:7860/health || exit 1

# Expose port
EXPOSE 7860

# Run FastAPI app directly
CMD ["python", "app.py"]

