FROM python:3.11-slim

# Install FFmpeg and system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY workers/ ./workers/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8000/health')"

# Start API server and 3 workers
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8000 & \
           python -m workers.video_worker 1 & \
           python -m workers.video_worker 2 & \
           python -m workers.video_worker 3 & \
           wait"
