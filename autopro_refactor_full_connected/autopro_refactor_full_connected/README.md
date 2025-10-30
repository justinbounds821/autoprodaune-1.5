# AutoPro Daune - Refactored Microservices Architecture

Complete microservices ecosystem for AutoPro Daune with 10 services, observability, and CI/CD.

## Architecture

- **10 Microservices**: Lead, Video, Social, Financial, Referral, Automation, Notification, Analytics, WhatsApp, MCP
- **Database**: PostgreSQL (via Supabase)
- **Cache & Queue**: Redis + Celery
- **Auth**: JWT + Supabase Auth
- **Observability**: Prometheus + Grafana + OpenTelemetry
- **CI/CD**: GitHub Actions with GHCR push

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Git

### Local Development

1. Clone and setup:
```bash
git clone <repo>
cd autopro_refactor_full_connected
cp .env.example .env
# Edit .env with your configuration
```

2. Start all services:
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build
```

3. Access services:
- Lead Service: http://localhost:8001
- MCP Service: http://localhost:8010
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov --cov-report=html

# Run integration tests only
pytest tests/integration/
```

## Services Overview

| Service | Port | Description |
|---------|------|-------------|
| lead-service | 8001 | Lead management and tracking |
| video-service | 8002 | Video generation with HeyGen |
| social-service | 8003 | Social media integrations |
| financial-service | 8004 | Revenue tracking and analytics |
| referral-service | 8005 | Referral program management |
| automation-service | 8006 | Celery tasks and automation |
| notification-service | 8007 | Email/SMS/Push notifications |
| analytics-service | 8008 | Data analytics and reporting |
| whatsapp-service | 8009 | WhatsApp bot and webhooks |
| mcp-service | 8010 | MCP dispatcher for GitHub/Linear/Supabase |

## Development

### Adding a New Service

1. Create service directory in `microservices/`
2. Add to `docker-compose.override.yml`
3. Update Prometheus config
4. Add tests

### Running Individual Services

```bash
cd microservices/lead-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

## Deployment

CI/CD pipeline automatically builds and pushes Docker images to GHCR on push to `main`.

### Manual Deployment

```bash
docker-compose -f docker-compose.yml up -d
```

## Monitoring

- **Prometheus**: Metrics collection at `:9090`
- **Grafana**: Dashboards at `:3000`
- **Health Checks**: Each service exposes `/health`
- **Metrics**: Each service exposes `/metrics`

## License

Proprietary - AutoPro Daune
