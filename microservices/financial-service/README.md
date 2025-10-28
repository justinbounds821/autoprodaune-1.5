# Financial Service

Financial tracking and invoicing

## Port: 8004

## Features

- cost_calculation
- roi_tracking
- invoicing
- expense_management

## Running

```bash
docker build -t financial-service:latest .
docker run -p 8004:8004 financial-service:latest
```

## API Endpoints

- `GET /` - Service info
- `GET /api/status` - Service status
- `GET /api/info` - Detailed information
- `GET /health` - Health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe
- `GET /metrics` - Prometheus metrics
