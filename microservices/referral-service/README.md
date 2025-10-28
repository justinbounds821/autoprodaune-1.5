# Referral Service

Referral program management

## Port: 8005

## Features

- referral_creation
- commission_tracking
- reward_management
- analytics

## Running

```bash
docker build -t referral-service:latest .
docker run -p 8005:8005 referral-service:latest
```

## API Endpoints

- `GET /` - Service info
- `GET /api/status` - Service status
- `GET /api/info` - Detailed information
- `GET /health` - Health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe
- `GET /metrics` - Prometheus metrics
