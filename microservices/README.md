# AutoPro Daune - Microservices Architecture

🚀 **Production-ready microservices ecosystem for AutoPro Daune lead generation and automation platform.**

## 📋 Overview

This repository contains the complete refactored microservices architecture, replacing the legacy monolithic FastAPI application with 10 independent, horizontally scalable services.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Kong API Gateway (8000)                  │
│          JWT Auth • Rate Limiting • CORS • Routing           │
└────┬────────────────────────────────────────────────────┬────┘
     │                                                     │
     ├─ Lead Service (8001)        ├─ Automation Service (8006)
     ├─ Video Service (8002)       ├─ Notification Service (8007)
     ├─ Social Service (8003)      ├─ Analytics Service (8008)
     ├─ Financial Service (8004)   ├─ WhatsApp Service (8009)
     ├─ Referral Service (8005)    └─ MCP Service (8010)
     │
     ├─────────────── PostgreSQL (5432) ──────────────────┤
     ├─────────────── Redis (6379) ────────────────────────┤
     └─────────────── RabbitMQ (5672) ─────────────────────┘
```

## 🎯 Microservices

| Service | Port | Description | Key Features |
|---------|------|-------------|--------------|
| **Lead Service** | 8001 | Lead management & scoring | CRUD, scoring, activities, bulk ops |
| **Video Service** | 8002 | Video generation engine | HeyGen, templates, queue processing |
| **Social Service** | 8003 | Social media integrations | TikTok, Instagram, Facebook, YouTube |
| **Financial Service** | 8004 | Financial tracking | Invoicing, ROI, cost calculation |
| **Referral Service** | 8005 | Referral program | Commission tracking, rewards |
| **Automation Service** | 8006 | Workflow automation | Scheduling, triggers, actions |
| **Notification Service** | 8007 | Multi-channel notifications | Email, SMS, push notifications |
| **Analytics Service** | 8008 | Business metrics | KPIs, dashboards, reports |
| **WhatsApp Service** | 8009 | WhatsApp integration | Webhooks, messaging, bot |
| **MCP Service** | 8010 | MCP orchestration | Linear, GitHub, Supabase integration |

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Git

### Local Development

```bash
# Clone repository
git clone <repo-url>
cd microservices

# Copy environment variables
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start all services
docker-compose up --build

# Verify services are running
curl http://localhost:8001/health  # Lead Service
curl http://localhost:8002/health  # Video Service
...

# View logs
docker-compose logs -f lead-service

# Stop all services
docker-compose down
```

### Access Points

- **Kong Gateway**: http://localhost:8000
- **Kong Admin**: http://localhost:8001
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Jaeger UI**: http://localhost:16686
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

## 📦 Shared Library (autopro-common)

All services use the `autopro-common` shared library for:

- ✅ Structured JSON logging with OpenTelemetry
- ✅ Async SQLAlchemy database connections
- ✅ Redis cache utilities
- ✅ RabbitMQ messaging (aio-pika)
- ✅ Prometheus metrics & health checks
- ✅ Kubernetes readiness/liveness probes

### Installation

```bash
cd autopro-common
pip install -e .
```

### Usage Example

```python
from autopro_common import (
    setup_logging,
    init_database,
    init_redis,
    setup_metrics,
    create_health_router,
)

# Setup logging
setup_logging("my-service", level="INFO")

# Initialize database
db = init_database()

# Initialize Redis
cache = init_redis()

# Setup Prometheus metrics
metrics = setup_metrics(app, "my-service")

# Add health checks
health = init_health_check("my-service")
app.include_router(create_health_router(health))
```

## 🐳 Docker Deployment

### Build Individual Service

```bash
docker build -t lead-service:latest -f lead-service/Dockerfile .
docker run -p 8001:8001 lead-service:latest
```

### Build All Services

```bash
docker-compose build
```

### Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## ☸️ Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (EKS, GKE, AKS, or local)
- kubectl configured
- Helm (optional)

### Deploy to K8s

```bash
# Create namespace
kubectl apply -f k8s/base/namespace.yaml

# Create config & secrets
kubectl apply -f k8s/base/configmap.yaml
kubectl create secret generic autopro-secrets --from-env-file=.env -n autopro

# Deploy infrastructure
kubectl apply -f k8s/base/postgres.yaml
kubectl apply -f k8s/base/redis.yaml
kubectl apply -f k8s/base/rabbitmq.yaml

# Deploy services
kubectl apply -f k8s/base/lead-service.yaml
kubectl apply -f k8s/base/video-service.yaml
kubectl apply -f k8s/base/social-service.yaml
kubectl apply -f k8s/base/financial-service.yaml
kubectl apply -f k8s/base/referral-service.yaml
kubectl apply -f k8s/base/automation-service.yaml
kubectl apply -f k8s/base/notification-service.yaml
kubectl apply -f k8s/base/analytics-service.yaml
kubectl apply -f k8s/base/whatsapp-service.yaml
kubectl apply -f k8s/base/mcp-service.yaml

# Deploy ingress (Kong)
kubectl apply -f k8s/base/ingress.yaml

# Verify deployment
kubectl get pods -n autopro
kubectl get services -n autopro
```

### Horizontal Pod Autoscaling

Each service has HPA configured:
- **Min replicas**: 2
- **Max replicas**: 10
- **CPU target**: 70%
- **Memory target**: 80%

```bash
# Check HPA status
kubectl get hpa -n autopro

# Scale manually
kubectl scale deployment lead-service --replicas=5 -n autopro
```

## 📊 Monitoring & Observability

### Prometheus Metrics

All services expose Prometheus metrics at `/metrics`:

- `http_requests_total` - Total requests by method, endpoint, status
- `http_request_duration_seconds` - Request latency histograms
- `db_queries_total` - Database query count
- `cache_hits_total` / `cache_misses_total` - Cache performance
- `queue_messages_published` / `consumed` - Message queue metrics
- `business_events_total` - Custom business metrics

### Grafana Dashboards

Pre-configured dashboards:
- **Overview**: System-wide metrics
- **Service Health**: Per-service health metrics
- **Database**: Connection pool, query performance
- **Queue**: RabbitMQ metrics
- **Business KPIs**: Lead conversion, video generation, ROI

### Distributed Tracing (Jaeger)

OpenTelemetry integration for request tracing across services.

```python
from autopro_common.logging import set_trace_context

# Propagate trace context
set_trace_context(trace_id="...", span_id="...")
```

## 🧪 Testing

### Unit Tests

```bash
cd lead-service
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=html
```

### Integration Tests

```bash
# Start test infrastructure
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
pytest tests/integration/ -v

# Cleanup
docker-compose -f docker-compose.test.yml down
```

### Load Tests

```bash
# Install k6
brew install k6  # macOS
# or
sudo apt install k6  # Ubuntu

# Run load test
k6 run tests/load/lead-service.js
```

Example k6 test:

```javascript
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 100 },
    { duration: '3m', target: 100 },
    { duration: '1m', target: 0 },
  ],
};

export default function() {
  let res = http.get('http://localhost:8000/api/leads');
  check(res, { 'status 200': (r) => r.status === 200 });
}
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

Each service has an automated CI/CD pipeline:

1. **Lint**: Black, Flake8, isort, MyPy
2. **Test**: Pytest with coverage (>85%)
3. **Build**: Docker image build & push to GHCR
4. **Deploy**: 
   - `develop` → Staging environment
   - `main` → Production environment

### Deployment Strategy

- **Blue-Green**: Zero-downtime deployments
- **Rollback**: Automated rollback on health check failure
- **Canary**: Gradual traffic shift (10% → 50% → 100%)

### Branch Strategy

- `main` - Production (protected)
- `develop` - Staging
- `feature/*` - Feature branches
- `hotfix/*` - Critical fixes

## 🔒 Security

### Authentication & Authorization

- **Kong JWT Plugin**: Token-based authentication
- **API Key**: Service-to-service communication
- **RBAC**: Role-based access control

### Rate Limiting

- **Default**: 100 requests/minute per IP
- **Video Generation**: 10 requests/minute
- **File Upload**: 5 requests/minute

### Secrets Management

- **Kubernetes Secrets**: Encrypted at rest
- **Environment Variables**: Never committed to git
- **Vault Integration**: (Optional) HashiCorp Vault

## 📈 Performance Benchmarks

| Service | Avg Latency (p95) | Throughput | Error Rate |
|---------|-------------------|------------|------------|
| Lead Service | <100ms | 1000 req/s | <0.1% |
| Video Service | <500ms | 50 req/s | <0.5% |
| Social Service | <200ms | 200 req/s | <0.2% |
| Financial Service | <150ms | 500 req/s | <0.1% |

**Target SLAs:**
- **Availability**: 99.9% uptime
- **Latency**: p95 < 200ms
- **Error Rate**: < 0.5%

## 🛠️ Development

### Adding a New Service

```bash
# Create service structure
mkdir -p new-service/{app/{api,services,models,queue},tests}

# Copy template
cp -r lead-service/app/main.py new-service/app/
cp lead-service/Dockerfile new-service/
cp lead-service/requirements.txt new-service/

# Update docker-compose.yml
# Update k8s manifests
# Create CI/CD workflow
```

### Code Style

- **Formatter**: Black (line length: 120)
- **Import Sort**: isort
- **Linter**: Flake8
- **Type Checking**: MyPy

```bash
# Format code
black app/
isort app/

# Lint
flake8 app/ --max-line-length=120

# Type check
mypy app/ --ignore-missing-imports
```

## 📚 Documentation

- [Architecture Diagram](./docs/architecture.md)
- [API Documentation](./docs/api.md)
- [Deployment Guide](./docs/deployment.md)
- [Monitoring Guide](./docs/monitoring.md)
- [Troubleshooting](./docs/troubleshooting.md)

### API Documentation

Each service exposes OpenAPI documentation:

- http://localhost:8001/docs (Lead Service)
- http://localhost:8002/docs (Video Service)
- ...

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs lead-service

# Check health
curl http://localhost:8001/health

# Check dependencies
docker-compose ps
```

### Database Connection Issues

```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U postgres -d autopro -c "SELECT 1;"

# Check connection pool
curl http://localhost:8001/metrics | grep db_connections
```

### High Memory Usage

```bash
# Check metrics
docker stats

# Adjust resource limits in docker-compose.yml
# or K8s manifests
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

Proprietary - AutoPro Daune 2025

## 🆘 Support

- **Slack**: #autopro-microservices
- **Email**: tech@autopro.ro
- **Issues**: GitHub Issues

---

**Built with ❤️ by the AutoPro Engineering Team**

**Tech Stack**: Python 3.11, FastAPI, PostgreSQL, Redis, RabbitMQ, Docker, Kubernetes, Kong, Prometheus, Grafana, Jaeger
