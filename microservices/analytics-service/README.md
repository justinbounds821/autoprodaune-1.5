# Analytics Service

Business metrics and analytics

## Port: 8008

## Features

- metrics_collection
- reporting
- dashboard_data
- kpi_calculation

## Running

```bash
docker build -t analytics-service:latest .
docker run -p 8008:8008 analytics-service:latest
```

## API Endpoints

- `GET /` - Service info
- `GET /api/status` - Service status
- `GET /api/info` - Detailed information
- `GET /health` - Health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe
- `GET /metrics` - Prometheus metrics
