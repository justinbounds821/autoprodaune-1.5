# Video Service

Video generation and processing engine

## Port: 8002

## Features

- video_generation
- template_management
- heygen_integration
- video_queue

## Running

```bash
docker build -t video-service:latest .
docker run -p 8002:8002 video-service:latest
```

## API Endpoints

- `GET /` - Service info
- `GET /api/status` - Service status
- `GET /api/info` - Detailed information
- `GET /health` - Health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe
- `GET /metrics` - Prometheus metrics
