# Mcp Service

MCP orchestration (Python-only)

## Port: 8010

## Features

- linear_integration
- github_integration
- supabase_integration
- task_orchestration

## Running

```bash
docker build -t mcp-service:latest .
docker run -p 8010:8010 mcp-service:latest
```

## API Endpoints

- `GET /` - Service info
- `GET /api/status` - Service status
- `GET /api/info` - Detailed information
- `GET /health` - Health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe
- `GET /metrics` - Prometheus metrics
