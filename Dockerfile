# ============================================================================
# TerraEdge — Type B Edge Gateway Dockerfile (Phase 8 Production Hardened)
# ============================================================================

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GATEWAY_HOST=0.0.0.0 \
    GATEWAY_PORT=8000 \
    TERRAEDGE_ENV=production \
    BACKHAUL_QUEUE_DB_PATH=/app/gateway/data/backhaul_queue.db

WORKDIR /app

# Install system utilities for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source tree
COPY . .

# Create persistent data directory for SQLite store-and-forward queue
RUN mkdir -p /app/gateway/data /app/gateway/data/backups

# Expose Gateway REST API port
EXPOSE 8000

# Health check probe against liveness endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Launch Type B Edge Gateway server
CMD ["python", "-m", "gateway.app"]
