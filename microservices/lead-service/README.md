# Lead Service

Microservice for lead management, scoring, and activity tracking.

## Features

- ✅ Create, read, update, delete leads
- ✅ Lead scoring and prioritization
- ✅ Activity timeline tracking
- ✅ Bulk operations
- ✅ Export functionality
- ✅ Prometheus metrics
- ✅ Health checks (K8s ready)
- ✅ RabbitMQ integration

## API Endpoints

### Lead Management

- `POST /api/leads/` - Create new lead
- `GET /api/leads/` - List leads (paginated, filterable)
- `GET /api/leads/{id}` - Get specific lead
- `PUT /api/leads/{id}` - Update lead
- `DELETE /api/leads/{id}` - Delete lead

### Activity Tracking

- `POST /api/leads/{id}/activities` - Create activity
- `GET /api/leads/{id}/timeline` - Get activity timeline

### Lead Scoring

- `POST /api/leads/scoring/{id}/score` - Score single lead
- `POST /api/leads/scoring/batch-score` - Batch score leads

### Bulk Operations

- `POST /api/leads/bulk-update` - Bulk update multiple leads

### Health & Metrics

- `GET /health` - Full health check
- `GET /health/ready` - Kubernetes readiness probe
- `GET /health/live` - Kubernetes liveness probe
- `GET /metrics` - Prometheus metrics

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/autopro

# Redis
REDIS_URL=redis://redis:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Service Config
PORT=8001
LOG_LEVEL=INFO
CORS_ORIGINS=*

# Supabase (optional)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-key
```

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt
pip install -e ../autopro-common

# Run service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## Running with Docker

```bash
# Build image
docker build -t lead-service:latest -f Dockerfile ../..

# Run container
docker run -p 8001:8001 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host/db \
  -e REDIS_URL=redis://redis:6379/0 \
  lead-service:latest
```

## Testing

```bash
# Run tests
pytest tests/ -v --cov=app

# Run specific test
pytest tests/test_leads.py::test_create_lead -v
```

## Lead Scoring Algorithm

Leads are scored 0-100 based on:

1. **Source Quality** (0-30 points)
   - Referral: 30
   - WhatsApp: 25
   - Instagram/TikTok: 20
   - YouTube/Facebook: 15
   - Landing Page: 10
   - Direct: 5

2. **Contact Completeness** (0-25 points)
   - Phone + Email: 25
   - Phone OR Email: 12

3. **Details Provided** (0-20 points)
   - Comprehensive (>100 chars): 20
   - Adequate (>50 chars): 10
   - Minimal (>0 chars): 5

4. **Estimated Value** (0-15 points)
   - High (≥10000): 15
   - Medium (≥5000): 10
   - Low (>0): 5

5. **Name Provided** (0-10 points)
   - Yes: 10

**Priority Assignment:**
- Score ≥70: 🔴 URGENT
- Score ≥50: 🟠 HIGH
- Score ≥30: 🟡 MEDIUM
- Score <30: 🟢 LOW

## Message Queue Integration

**Consumed Queues:**
- `lead.scoring` - Automatic lead scoring
- `lead.enrichment` - Lead data enrichment

**Published Events:**
- `lead.created` - When new lead is created

## Metrics Exposed

- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `db_queries_total` - Database query count
- `cache_hits_total` / `cache_misses_total` - Cache performance
- `business_events_total{event_type="lead_created"}` - Business events

## Architecture

```
┌─────────────┐
│  API Layer  │ ← FastAPI routes
├─────────────┤
│  Services   │ ← Business logic
├─────────────┤
│   Models    │ ← SQLAlchemy models
├─────────────┤
│  Database   │ ← PostgreSQL connection
└─────────────┘
      ↕
┌─────────────┐
│   Redis     │ ← Caching
└─────────────┘
      ↕
┌─────────────┐
│  RabbitMQ   │ ← Message queue
└─────────────┘
```

## Dependencies

- **Database**: PostgreSQL (via asyncpg)
- **Cache**: Redis
- **Queue**: RabbitMQ
- **Monitoring**: Prometheus
- **Tracing**: OpenTelemetry (optional)

## Production Deployment

See `/workspace/microservices/k8s/lead-service/` for Kubernetes manifests.

## License

Proprietary - AutoPro Daune 2025
