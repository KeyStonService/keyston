# SynergyMesh Workflow System - Production Dockerfile
FROM python:3.11-slim as base

LABEL maintainer="SynergyMesh Team"
LABEL description="Production-ready workflow orchestration system"
LABEL version="2.0.0"

# Environment variables
ENV PYTHONUNBUFFERED=1     PYTHONDONTWRITEBYTECODE=1     PIP_NO_CACHE_DIR=1     PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-workflow.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-workflow.txt

# Copy application code
COPY config/ ./config/
COPY core/ ./core/
COPY tools/ ./tools/
COPY automation/ ./automation/

# Create non-root user
RUN useradd -m -u 1000 workflow && \
    chown -R workflow:workflow /app

USER workflow

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose ports
EXPOSE 8080

# Start command
CMD ["python3", "-m", "automation.pipelines.instant_execution_pipeline"]
