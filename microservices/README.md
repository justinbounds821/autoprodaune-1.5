# AutoProDaune Microservices Architecture

**Version:** 2.0.0  
**Status:** IN DEVELOPMENT  
**Migration Start:** 28 October 2025

## 📁 Project Structure

```
microservices/
├── infrastructure/              # Infrastructure configuration
│   ├── prometheus/              # Monitoring
│   ├── grafana/                 # Dashboards
│   ├── rabbitmq/                # Message queue
│   ├── redis/                   # Cache
│   └── kong/                    # API Gateway
│
├── services/                    # Microservices
│   ├── lead-service/            # Lead management
│   ├── video-service/           # Video generation
│   ├── social-service/          # Social media
│   ├── financial-service/       # Financial tracking
│   ├── referral-service/        # Referral program
│   ├── automation-service/      # Background jobs
│   ├── notification-service/    # Notifications
│   ├── analytics-service/       # Analytics
│   ├── whatsapp-service/        # WhatsApp integration
│   └── mcp-service/             # Workflow orchestration
│
├── shared/                      # Shared libraries
│   ├── autopro-common/          # Common utilities
│   ├── autopro-models/          # Pydantic models
│   └── autopro-messaging/       # Queue clients
│
├── docker-compose.infrastructure.yml  # Infrastructure
├── docker-compose.services.yml        # Microservices
└── docker-compose.yml                 # Full stack
```

## 🚀 Quick Start

### Prerequisites
- Docker 24.0+
- Docker Compose 2.0+
- 8GB RAM minimum
- 20GB disk space

### Start Infrastructure
```bash
cd microservices
docker-compose -f docker-compose.infrastructure.yml up -d

# Verify all services are healthy
docker-compose -f docker-compose.infrastructure.yml ps
```

### Access Points
- **RabbitMQ Management**: http://localhost:15672 (autopro/autopro_pass_2025)
- **Redis**: localhost:6379 (password: autopro_redis_2025)
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/autopro_grafana_2025)
- **Jaeger**: http://localhost:16686
- **Kong Admin**: http://localhost:8001
- **Kong Proxy**: http://localhost:8000

### Stop Infrastructure
```bash
docker-compose -f docker-compose.infrastructure.yml down
```

## 📊 Monitoring

### Prometheus
- Metrics collection: http://localhost:9090
- Targets: http://localhost:9090/targets
- Alerts: http://localhost:9090/alerts

### Grafana Dashboards
1. **System Overview** - All services health
2. **Service Performance** - Latency, throughput, errors
3. **Database Metrics** - Query performance, connections
4. **Queue Metrics** - RabbitMQ queue depth, consumers
5. **Business Metrics** - Leads, videos, revenue

### Jaeger Tracing
- UI: http://localhost:16686
- Trace all requests across services
- Performance bottleneck identification

## 🔧 Development

### Service Template
```bash
# Create new service from template
cd microservices/services
cp -r _service-template my-service
cd my-service
# Update service name in all config files
```

### Local Development
```bash
# Run single service with hot reload
cd services/lead-service
python -m uvicorn app.main:app --reload --port 8001

# Or use Docker
docker-compose -f docker-compose.services.yml up lead-service
```

### Testing
```bash
# Run tests for single service
cd services/lead-service
pytest tests/ -v

# Run integration tests
pytest tests/integration/ -v
```

## 📈 Migration Progress

### PHASE 1: Infrastructure Setup ✅ (Current)
- [x] Docker Compose infrastructure
- [x] RabbitMQ configuration
- [x] Redis setup
- [x] Prometheus + Grafana
- [x] Jaeger tracing
- [x] Kong API Gateway
- [ ] CI/CD pipeline (Week 1-2)

### PHASE 2: Core Services (Week 3-6)
- [ ] Lead Service
- [ ] Video Service
- [ ] Social Service
- [ ] Financial Service
- [ ] Referral Service

### PHASE 3: Supporting Services (Week 7-8)
- [ ] Automation Service
- [ ] Notification Service
- [ ] Analytics Service
- [ ] WhatsApp Service
- [ ] MCP Service (refactored)

### PHASE 4: Migration & Cutover (Week 9-10)
- [ ] Dual-run testing
- [ ] Load testing
- [ ] Production cutover
- [ ] Monolith decommission

### PHASE 5: Optimization (Week 11-12)
- [ ] Performance tuning
- [ ] Documentation
- [ ] Team training
- [ ] Runbooks

## 🐛 Troubleshooting

### Infrastructure not starting
```bash
# Check logs
docker-compose -f docker-compose.infrastructure.yml logs -f

# Restart specific service
docker-compose -f docker-compose.infrastructure.yml restart redis
```

### RabbitMQ not accessible
```bash
# Check RabbitMQ logs
docker logs autopro-rabbitmq

# Reset RabbitMQ
docker-compose -f docker-compose.infrastructure.yml down
docker volume rm microservices_rabbitmq_data
docker-compose -f docker-compose.infrastructure.yml up -d rabbitmq
```

### Prometheus not scraping
```bash
# Verify Prometheus config
docker exec autopro-prometheus promtool check config /etc/prometheus/prometheus.yml

# Reload Prometheus config
curl -X POST http://localhost:9090/-/reload
```

## 📚 Documentation

- **Architecture**: See `/workspace/DIAGNOSTIC_TEHNIC_AUTOPRODAUNE_MCP_ORCHESTRATOR.md`
- **API Documentation**: Each service exposes OpenAPI at `/docs`
- **Runbooks**: See `docs/runbooks/`
- **Deployment Guide**: See `docs/deployment.md`

## 🔐 Security

- All passwords are for **development only**
- Production passwords managed via Secrets Manager
- API Gateway handles authentication (JWT)
- Rate limiting per service
- Network isolation via Docker networks

## 📞 Support

For issues or questions:
1. Check logs: `docker-compose logs -f <service>`
2. Check metrics: Grafana dashboards
3. Check traces: Jaeger UI
4. Consult diagnostic document
5. Contact team

---

**Last Updated:** 28 October 2025  
**Next Review:** Week 2 (Service Template Creation)
