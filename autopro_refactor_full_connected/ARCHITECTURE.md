# Architecture Documentation

## System Overview

AutoPro Daune is built as a microservices architecture with the following components:

### Core Services

1. **Lead Service** - Manages customer leads and tracking
2. **Video Service** - Generates marketing videos using HeyGen API
3. **Social Service** - Handles social media posting (TikTok, Instagram, YouTube)
4. **Financial Service** - Tracks revenue and financial metrics
5. **Referral Service** - Manages referral program

### Infrastructure Services

6. **Automation Service** - Runs scheduled tasks via Celery
7. **Notification Service** - Sends emails, SMS, push notifications
8. **Analytics Service** - Aggregates data for reporting
9. **WhatsApp Service** - WhatsApp bot integration
10. **MCP Service** - Dispatcher for GitHub, Linear, Supabase

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy (async)
- **Database**: PostgreSQL (via Supabase)
- **Cache**: Redis
- **Queue**: Celery with Redis broker

### Observability
- **Metrics**: Prometheus + prometheus-fastapi-instrumentator
- **Tracing**: OpenTelemetry
- **Visualization**: Grafana
- **Logging**: Structured logging with Python logging

### Authentication
- **JWT**: For service-to-service auth
- **Supabase Auth**: For user authentication
- **OAuth**: For social media integrations

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose (dev), Kubernetes (prod ready)
- **CI/CD**: GitHub Actions
- **Registry**: GitHub Container Registry (GHCR)

## Data Flow

1. **Lead Creation**:
   - Client → Lead Service → PostgreSQL
   - Lead Service → Notification Service (async via Celery)

2. **Video Generation**:
   - Client → Video Service
   - Video Service → HeyGen API
   - Video Service → Storage (Supabase/R2)

3. **Social Posting**:
   - Automation Service (Celery) → Social Service
   - Social Service → TikTok/Instagram/YouTube APIs

4. **MCP Dispatch**:
   - Client → MCP Service
   - MCP Service → GitHub/Linear/Supabase APIs

## Security

- All services require JWT authentication
- Secrets managed via environment variables
- HTTPS in production
- Rate limiting on all endpoints
- Security scans in CI/CD (Trivy)

## Scalability

- Horizontal scaling of services via container orchestration
- Redis for distributed caching
- Celery for async task processing
- Database connection pooling
- Read replicas for PostgreSQL (production)

## Monitoring Strategy

- Health checks on all services
- Prometheus metrics collection every 15s
- Grafana dashboards for visualization
- Alert rules for critical metrics
- Distributed tracing with OpenTelemetry
