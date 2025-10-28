# Multi-stage build for lead-service
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy shared library
COPY microservices/autopro-common /build/autopro-common

# Install shared library
RUN cd /build/autopro-common && pip install --user -e .

# Copy service requirements
COPY microservices/lead-service/requirements.txt /build/
RUN pip install --user -r /build/requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Ensure Python binaries are in PATH
ENV PATH=/root/.local/bin:$PATH

# Copy autopro-common
COPY microservices/autopro-common /workspace/microservices/autopro-common

# Copy service code
COPY microservices/lead-service/app /app/app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health/live')"

# Run service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "info"]
