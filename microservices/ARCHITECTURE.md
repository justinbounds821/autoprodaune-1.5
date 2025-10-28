# AutoPro Microservices Architecture

## System Architecture Diagram

```
                                 ┌─────────────────────────┐
                                 │                         │
                                 │    Client Applications  │
                                 │  (Web, Mobile, API)     │
                                 │                         │
                                 └───────────┬─────────────┘
                                             │
                                             │ HTTPS
                                             ▼
                     ┌───────────────────────────────────────────────┐
                     │                                               │
                     │          Kong API Gateway (8000)              │
                     │  • JWT Authentication                         │
                     │  • Rate Limiting (100/min default)            │
                     │  • CORS Headers                               │
                     │  • Request/Response Transformation            │
                     │  • Circuit Breaker                            │
                     │  • API Versioning                             │
                     │                                               │
                     └─────┬───────────────────────────────┬─────────┘
                           │                               │
        ┌──────────────────┼───────────────┬───────────────┼──────────────────┐
        │                  │               │               │                  │
        ▼                  ▼               ▼               ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│              │  │              │  │              │  │              │  │              │
│    Lead      │  │    Video     │  │   Social     │  │  Financial   │  │   Referral   │
│   Service    │  │   Service    │  │   Service    │  │   Service    │  │   Service    │
│   :8001      │  │   :8002      │  │   :8003      │  │   :8004      │  │   :8005      │
│              │  │              │  │              │  │              │  │              │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                  │                 │                  │
       └─────────────────┼──────────────────┼─────────────────┼──────────────────┘
                         │                  │                 │
        ┌────────────────┼──────────────────┼─────────────────┼──────────────────┐
        │                │                  │                 │                  │
        ▼                ▼                  ▼                 ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│              │  │              │  │              │  │              │  │              │
│  Automation  │  │ Notification │  │  Analytics   │  │  WhatsApp    │  │     MCP      │
│   Service    │  │   Service    │  │   Service    │  │   Service    │  │   Service    │
│   :8006      │  │   :8007      │  │   :8008      │  │   :8009      │  │   :8010      │
│              │  │              │  │              │  │              │  │              │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                  │                 │                  │
       └─────────────────┴──────────────────┴─────────────────┴──────────────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
        ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
        │                  │    │                  │    │                  │
        │   PostgreSQL     │    │      Redis       │    │    RabbitMQ      │
        │    Database      │    │   Cache Layer    │    │  Message Queue   │
        │     :5432        │    │     :6379        │    │     :5672        │
        │                  │    │                  │    │                  │
        │ • Connection     │    │ • Rate Limiting  │    │ • Async Jobs     │
        │   Pooling        │    │ • Session Store  │    │ • Event Bus      │
        │ • Replication    │    │ • Caching        │    │ • Dead Letter    │
        │ • Backups        │    │ • Pub/Sub        │    │ • Retries        │
        │                  │    │                  │    │                  │
        └──────────────────┘    └──────────────────┘    └──────────────────┘
                    │                        │                        │
                    └────────────────────────┼────────────────────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
        ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
        │                  │    │                  │    │                  │
        │   Prometheus     │    │     Grafana      │    │      Jaeger      │
        │  Metrics Store   │    │   Dashboards     │    │  Distributed     │
        │     :9090        │    │     :3000        │    │    Tracing       │
        │                  │    │                  │    │    :16686        │
        └──────────────────┘    └──────────────────┘    └──────────────────┘
```

## Service Communication Patterns

### 1. Synchronous (HTTP/REST)

- Client → Kong → Services
- Service → Service (rare, via internal network)
- Used for: Real-time queries, CRUD operations

### 2. Asynchronous (Message Queue)

- Services publish events to RabbitMQ
- Other services consume events
- Used for: Video processing, notifications, analytics

**Event Flow Example:**

```
Lead Created → RabbitMQ (lead.created) → Video Service → Generate Video
                    ↓                           ↓
              Analytics Service          RabbitMQ (video.generated)
                    ↓                           ↓
            Update Dashboard              Social Service → Post Video
```

### 3. Caching Strategy

```
Request → Check Redis → Cache Hit? → Return Cached Data
                ↓
          Cache Miss
                ↓
          Query Database
                ↓
          Store in Redis (TTL)
                ↓
          Return Data
```

## Data Flow

### Lead Creation Flow

```
1. Client POST /api/leads
   ↓
2. Kong Gateway (auth + rate limit)
   ↓
3. Lead Service
   - Validate data
   - Calculate score
   - Save to PostgreSQL
   - Publish event: lead.created
   ↓
4. RabbitMQ (lead.created event)
   ↓
5. Multiple Consumers:
   - Video Service → Create personalized video
   - Automation Service → Trigger workflow
   - Analytics Service → Update metrics
   - Notification Service → Send welcome email
```

### Video Generation Flow

```
1. Video Service receives lead.created
   ↓
2. Check HeyGen API availability
   ↓
3. Create video job in queue
   ↓
4. Process video (async)
   - Generate script
   - Call HeyGen API
   - Poll for completion
   ↓
5. Store video URL in database
   ↓
6. Publish event: video.generated
   ↓
7. Social Service consumes event
   ↓
8. Post to TikTok, Instagram, YouTube
```

## Database Schema

### Lead Service Tables

```sql
leads
  - id (PK)
  - name
  - phone_number
  - email
  - source
  - status
  - priority
  - score
  - created_at
  - updated_at

lead_activities
  - id (PK)
  - lead_id (FK)
  - activity_type
  - description
  - created_at
```

### Video Service Tables

```sql
videos
  - id (PK)
  - lead_id (FK)
  - title
  - video_url
  - status
  - metadata
  - created_at
```

### Referral Service Tables

```sql
referrals
  - id (PK)
  - referrer_id (FK)
  - referred_id (FK)
  - referral_code
  - commission_amount
  - status
```

## Scalability Strategy

### Horizontal Scaling

- **Load Balancer**: Kong distributes traffic
- **Stateless Services**: No session data in services
- **Auto-scaling**: HPA based on CPU/memory
- **Database**: Read replicas for queries

### Vertical Scaling

- **Resource Limits**: CPU/memory per service
- **Connection Pooling**: Reuse DB connections
- **Caching**: Reduce database load

### Performance Optimization

1. **Database Indexing**
   - Composite indexes on (status, priority)
   - Full-text search on leads.name
   - Time-series indexes on created_at

2. **Caching Strategy**
   - Hot data: 1 hour TTL
   - Cold data: 24 hour TTL
   - Cache warming on startup

3. **Query Optimization**
   - Use async/await for I/O
   - Batch database queries
   - Limit result sets (pagination)

4. **Queue Management**
   - Priority queues for urgent tasks
   - Dead letter queue for failures
   - Rate limiting on consumers

## Security Architecture

### Defense in Depth

```
Layer 1: Kong Gateway
  - JWT authentication
  - API key validation
  - Rate limiting
  - IP whitelisting

Layer 2: Service Level
  - Input validation (Pydantic)
  - SQL injection prevention
  - XSS protection
  - CSRF tokens

Layer 3: Database
  - Encrypted at rest
  - Connection encryption (TLS)
  - Least privilege access
  - Audit logging

Layer 4: Network
  - Private subnet for services
  - Firewall rules
  - VPN for admin access
  - DDoS protection
```

### Authentication Flow

```
1. Client → Login request
   ↓
2. Auth Service validates credentials
   ↓
3. Generate JWT token (30min expiry)
   ↓
4. Client stores token
   ↓
5. Subsequent requests include token
   ↓
6. Kong validates token
   ↓
7. Forward to service with user context
```

## Failure Handling

### Circuit Breaker Pattern

```python
# Service A → Service B
try:
    response = await service_b.call()
except ServiceUnavailable:
    if circuit_breaker.is_open():
        return fallback_response()
    circuit_breaker.record_failure()
    raise
```

### Retry Strategy

- **Exponential Backoff**: 1s, 2s, 4s, 8s
- **Max Retries**: 3 attempts
- **Idempotency**: Safe to retry

### Health Checks

- **/health/live**: Is process alive?
- **/health/ready**: Can accept traffic?
- **Kubernetes probes**: Auto-restart on failure

## Observability

### Metrics (Prometheus)

```
# Request metrics
http_requests_total{service="lead-service", method="POST", status="200"}
http_request_duration_seconds{service="lead-service", endpoint="/api/leads"}

# Business metrics
leads_created_total{source="instagram"}
videos_generated_total{status="success"}
conversion_rate{source="referral"}

# Infrastructure metrics
db_connections_active{service="lead-service"}
queue_messages_pending{queue="video.processing"}
cache_hit_ratio{service="lead-service"}
```

### Logging (Structured JSON)

```json
{
  "timestamp": "2025-10-28T10:30:00Z",
  "level": "INFO",
  "service": "lead-service",
  "trace_id": "abc123",
  "span_id": "def456",
  "message": "Lead created",
  "lead_id": 12345,
  "source": "instagram"
}
```

### Tracing (Jaeger)

```
Request ID: abc123
├─ Kong Gateway (5ms)
├─ Lead Service (50ms)
│  ├─ Database Query (20ms)
│  ├─ Redis Cache (5ms)
│  └─ RabbitMQ Publish (10ms)
└─ Total: 90ms
```

## Disaster Recovery

### Backup Strategy

- **Database**: Daily full backup, hourly incremental
- **Redis**: RDB snapshots every 15 minutes
- **Files**: S3 with versioning enabled

### Recovery Plan

1. **Detect**: Automated alerts (Prometheus)
2. **Isolate**: Circuit breaker opens
3. **Failover**: Switch to backup (5 min RTO)
4. **Restore**: Load from backup (1 hour RPO)
5. **Verify**: Run smoke tests
6. **Resume**: Gradual traffic increase

## Cost Optimization

### Resource Efficiency

- **Right-sizing**: Adjust CPU/memory based on metrics
- **Spot Instances**: Use for non-critical workloads
- **Auto-scaling**: Scale down during low traffic
- **Reserved Capacity**: Long-term commitments

### Estimated Costs (AWS)

| Component | Monthly Cost |
|-----------|--------------|
| EKS Cluster | $150 |
| EC2 (10 nodes) | $500 |
| RDS PostgreSQL | $200 |
| ElastiCache | $100 |
| ALB | $50 |
| **Total** | **$1,000** |

---

**Last Updated**: 2025-10-28
**Version**: 1.0.0
**Maintained by**: AutoPro Engineering Team
