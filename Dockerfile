# MyImpact API - Production Dockerfile
# 
# Performance Efficiency:
# - Multi-stage build (smaller image, ~200MB)
# - Slim base image (minimal footprint)
# - Non-root user (security + performance)
# - Layer caching for dependencies
# - Cache headers: 1h for metadata (P95 ≤ 1s)
# 
# Reliability:
# - Health check (liveness probe)
# - Graceful shutdown handling (SIGTERM)
# - Timeout configuration (5s keep-alive)
# - Dependency versioning pinned

# ============================================================================
# Build stage: Install dependencies + build wheel
# ============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Performance: Install build dependencies in separate layer (cached)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Performance: Copy dependency files AND source code for package build
# (setuptools needs 'api/' and 'myimpact/' to exist when building wheel)
COPY pyproject.toml ./
COPY api/ ./api/
COPY myimpact/ ./myimpact/

# Performance: Build wheel (not editable install)
# Reliability: Pin versions via pyproject.toml
RUN pip install --no-cache-dir --user --upgrade pip && \
    pip install --no-cache-dir --user ".[api,dev]"


# ============================================================================
# Runtime stage: Minimal production image
# ============================================================================
FROM python:3.11-slim

WORKDIR /app

# Security: Run as non-root user (appuser:1000)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Performance: Copy only installed packages from builder (smaller image)
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Performance: Copy application files
COPY --chown=appuser:appuser api/ ./api/
COPY --chown=appuser:appuser myimpact/ ./myimpact/

# Performance: Copy sample data files (metadata for dropdowns)
# Cache headers: 1h for metadata endpoints (P95 ≤ 1s)
COPY --chown=appuser:appuser data/ ./data/
COPY --chown=appuser:appuser prompts/ ./prompts/
# Security: Switch to non-root user
USER appuser

# Performance: Set Python path to use local packages
# Performance: Disable bytecode generation (faster startup)
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Reliability: Health check (liveness probe at /api/health)
# Performance: 30s interval, 10s timeout, 40s startup grace period
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health').read()"

# Performance: Expose port
EXPOSE 8000

# Reliability: Graceful shutdown handling (wait for requests to complete)
STOPSIGNAL SIGTERM

# Performance: Single worker for demo (tune on real metrics: concurrentRequests, CPU)
# Performance: 5s timeout-keep-alive (avoid blocking event loop)
# Reliability: Async I/O for all endpoints
CMD ["uvicorn", "api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--timeout-keep-alive", "5", \
     "--access-log"]
