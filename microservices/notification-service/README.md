# Notification Service

Multi-channel notification delivery

## Port: 8007

## Features

- email_sending
- sms_sending
- push_notifications
- template_management

## Running

```bash
docker build -t notification-service:latest .
docker run -p 8007:8007 notification-service:latest
```

## API Endpoints

- `GET /` - Service info
- `GET /api/status` - Service status
- `GET /api/info` - Detailed information
- `GET /health` - Health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe
- `GET /metrics` - Prometheus metrics
