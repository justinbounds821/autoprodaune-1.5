# Automation Service

Workflow automation and scheduling

## Port: 8006

## Features

- workflow_execution
- scheduling
- trigger_management
- action_execution

## Running

```bash
docker build -t automation-service:latest .
docker run -p 8006:8006 automation-service:latest
```

## API Endpoints

- `GET /` - Service info
- `GET /api/status` - Service status
- `GET /api/info` - Detailed information
- `GET /health` - Health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe
- `GET /metrics` - Prometheus metrics
