# Social Service

Social media integrations and posting

## Port: 8003

## Features

- tiktok_posting
- instagram_posting
- facebook_posting
- youtube_posting
- scheduler

## Running

```bash
docker build -t social-service:latest .
docker run -p 8003:8003 social-service:latest
```

## API Endpoints

- `GET /` - Service info
- `GET /api/status` - Service status
- `GET /api/info` - Detailed information
- `GET /health` - Health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe
- `GET /metrics` - Prometheus metrics
