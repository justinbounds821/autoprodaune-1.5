# Whatsapp Service

WhatsApp integration and bot

## Port: 8009

## Features

- webhook_handling
- message_sending
- group_management
- bot_responses

## Running

```bash
docker build -t whatsapp-service:latest .
docker run -p 8009:8009 whatsapp-service:latest
```

## API Endpoints

- `GET /` - Service info
- `GET /api/status` - Service status
- `GET /api/info` - Detailed information
- `GET /health` - Health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe
- `GET /metrics` - Prometheus metrics
