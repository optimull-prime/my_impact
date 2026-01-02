# Multi-stage build for MyImpact FastAPI backend

# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /build

# Copy requirements
COPY pyproject.toml setup.py ./
COPY myimpact/ ./myimpact/
COPY data/ ./data/
COPY prompts/ ./prompts/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -e .

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Install only runtime dependencies
RUN pip install --no-cache-dir --upgrade pip

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY api/ ./api/
COPY myimpact/ ./myimpact/
COPY data/ ./data/
COPY prompts/ ./prompts/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Start Uvicorn server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
