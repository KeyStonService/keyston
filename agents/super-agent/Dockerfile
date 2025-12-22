# SuperAgent Dockerfile
# Multi-stage build for optimized production image

# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim AS production

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code with proper structure
COPY main.py .
COPY config.py .
COPY models/ ./models/
COPY services/ ./services/
COPY utils/ ./utils/

# Create directories for data persistence
RUN mkdir -p /app/data /app/logs

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 app \
    && chown -R app:app /app
USER app

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SUPERAGENT_ENV=production \
    SUPERAGENT_LOG_LEVEL=INFO \
    SUPERAGENT_EVENT_STORE_BACKEND=sqlite \
    SUPERAGENT_EVENT_STORE_PATH=/app/data/events.db \
    SUPERAGENT_AUDIT_PATH=/app/data/audit.db

# Expose port
EXPOSE 8080

# Health check (using Python instead of curl for smaller image)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys, urllib.request; \
try: \
    resp = urllib.request.urlopen('http://localhost:8080/health', timeout=5); \
    sys.exit(0 if 200 <= resp.getcode() < 400 else 1); \
except Exception: \
    sys.exit(1)"
# Health check using Python (curl not available in slim image)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health', timeout=5)" || exit 1

# Run the application with production settings
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]

# Stage 3: Development (optional)
FROM production AS development

USER root

# Install dev dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir pytest pytest-asyncio pytest-cov httpx mypy black ruff

# Copy test files
COPY tests/ ./tests/
COPY pytest.ini .

USER app

# Override CMD for development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]