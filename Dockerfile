# ==============================================================================
# IPL Analytics Platform - Production API Dockerfile
# Hardened Python 3.11-slim container with FastAPI & ML Inference
# ==============================================================================

FROM python:3.11-slim

WORKDIR /app

# System dependencies & health check curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root unprivileged service user
RUN groupadd -g 10003 iplgroup && \
    useradd -u 10003 -g iplgroup -s /bin/bash -m ipluser && \
    mkdir -p /app/models /app/model && \
    chown -R ipluser:iplgroup /app

# Copy application artifacts
COPY --chown=ipluser:iplgroup main.py /app/main.py
COPY --chown=ipluser:iplgroup models /app/models
COPY --chown=ipluser:iplgroup model /app/model

USER ipluser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
