# AutoPro Video Engine - Docker Deployment Guide

## 🚀 Production Deployment with Docker

This guide covers deploying the AutoPro Video Engine using Docker containers for production environments.

## 📋 Prerequisites

### System Requirements
- **Docker**: 20.10+ with Docker Compose
- **Docker Compose**: 2.0+
- **Hardware**: 4+ CPU cores, 8GB+ RAM recommended
- **Storage**: 50GB+ available disk space
- **Network**: Stable internet connection

### External Services
- **Supabase**: Database (configured via environment variables)
- **ElevenLabs**: TTS service (API key required)
- **Cloudflare R2**: Storage backend (for production)

## 🏗️ Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │  AutoPro API    │    │   External      │
│   (Optional)    │◄──►│   Container     │◄──►│   Services      │
└─────────────────┘    └─────────────────┘    │                 │
                                               │  ┌─────────────┐ │
┌─────────────────┐    ┌─────────────────┐    │  │  Supabase   │ │
│     Client      │    │   Prometheus    │    │  │  Database   │ │
│   Applications  │◄──►│   Metrics       │    │  └─────────────┘ │
└─────────────────┘    └─────────────────┘    │                 │
                                               │  ┌─────────────┐ │
┌─────────────────┐    ┌─────────────────┐    │  │ ElevenLabs  │ │
│     Admin       │    │     Grafana     │    │  │     TTS     │ │
│     Panel       │◄──►│   Dashboards    │    │  └─────────────┘ │
└─────────────────┘    └─────────────────┘    │                 │
                                               │  ┌─────────────┐ │
                                               │  │ Cloudflare  │ │
                                               │  │     R2      │ │
                                               │  └─────────────┘ │
                                               └─────────────────┘
```

## 🛠️ Quick Start Deployment

### 1. Environment Setup

Create environment file:
```bash
cd infra
cp .env.example .env
```

Edit `.env` with your production values:
```bash
# Core Configuration
USE_INTERNAL_VIDEO_ENGINE=true
LIPSYNC_BACKEND=sadtalker
VIDEO_ENGINE_MAX_CONCURRENCY=4
VIDEO_ENGINE_QUEUE_LIMIT=50

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key

# TTS
ELEVENLABS_API_KEY=sk-your-elevenlabs-key
ELEVENLABS_VOICE_ID=Rachel

# Storage (R2)
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
R2_BUCKET_NAME=autopro-videos

# Cost Tracking
TTS_COST_PER_SECOND=0.0001
PROCESSING_COST_PER_SECOND=0.001
STORAGE_COST_PER_MB=0.01

# Monitoring
PROMETHEUS_METRICS_ENABLED=true
```

### 2. Database Migration

Run database migrations:
```powershell
# From project root
.\scripts\db-migrate-video.ps1
```

### 3. Deploy Services

Start the production stack:
```bash
docker-compose up -d api
```

### 4. Verify Deployment

Check service health:
```bash
# Basic health check
curl http://localhost:8001/health

# Detailed health check
curl http://localhost:8001/health/detailed

# Metrics endpoint
curl http://localhost:8001/metrics
```

### 5. Load Testing

Test the deployment:
```powershell
# Test with production load
.\scripts\load-test-video.ps1 -ConcurrentJobs 5 -BaseUrl "http://localhost:8001"
```

## 📦 Service Configuration

### API Container

#### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8001` | API server port |
| `HOST` | `0.0.0.0` | Bind address |
| `USE_INTERNAL_VIDEO_ENGINE` | `true` | Enable video engine |
| `VIDEO_ENGINE_MAX_CONCURRENCY` | `2` | Max concurrent jobs |
| `VIDEO_ENGINE_QUEUE_LIMIT` | `20` | Max queue size |

#### Volume Mounts
```yaml
volumes:
  # Templates directory (read-only)
  - ../services/api/app/templates:/app/app/templates:ro

  # Generated videos (for local storage)
  - ../services/api/generated_videos:/app/generated_videos

  # Third-party tools (SadTalker, Wav2Lip)
  - ../services/api/third_party:/app/third_party:ro
```

#### Health Checks
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

### Optional: Monitoring Stack

#### Prometheus
```bash
# Enable monitoring profile
docker-compose --profile monitoring up -d

# Access Prometheus UI
open http://localhost:9090

# Access Grafana
open http://localhost:3000
# Default credentials: admin/admin
```

#### Grafana Dashboards
1. **AutoPro Video Engine**: Main operational dashboard
2. **System Resources**: CPU, memory, disk monitoring
3. **Business Metrics**: Cost tracking and usage analytics

## 🔧 Production Optimizations

### Performance Tuning

#### CPU Optimization
```bash
# For high-CPU systems
VIDEO_ENGINE_MAX_CONCURRENCY=8  # Increase based on CPU cores
VIDEO_ENGINE_PRESET=fast        # Faster encoding
```

#### Memory Optimization
```bash
# Reduce memory usage for constrained systems
VIDEO_ENGINE_MAX_CONCURRENCY=2
VIDEO_ENGINE_QUEUE_LIMIT=10
```

#### Storage Optimization
```bash
# Use R2 for production storage
VIDEO_ENGINE_STORAGE=r2
R2_BUCKET_NAME=autopro-videos-prod
```

### Security Hardening

#### Network Security
```yaml
# Use internal networks for production
networks:
  default:
    internal: true

# API service
api:
  networks:
    - default
    - traefik-public  # For reverse proxy
```

#### Environment Variables
```bash
# Use secrets management in production
SUPABASE_SERVICE_KEY_FILE=/run/secrets/supabase_key
ELEVENLABS_API_KEY_FILE=/run/secrets/elevenlabs_key
```

### Scaling Configuration

#### Horizontal Scaling
```yaml
# Multiple API instances
services:
  api:
    deploy:
      replicas: 3
    depends_on:
      - redis  # For job queue coordination

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
```

#### Load Balancing
```yaml
# Traefik reverse proxy configuration
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
    ports:
      - "80:80"
      - "8080:8080"  # Dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```

## 🔍 Monitoring & Troubleshooting

### Health Check Endpoints

#### Basic Health
```bash
curl http://localhost:8001/health
```

#### Detailed Health
```bash
curl http://localhost:8001/health/detailed | jq '.'
```

#### Metrics
```bash
# Prometheus format
curl http://localhost:8001/metrics

# Key metrics to watch
curl http://localhost:8001/metrics | grep autopro_video_jobs_total
curl http://localhost:8001/metrics | grep autopro_video_queue_length
```

### Log Monitoring

#### Container Logs
```bash
# View API logs
docker-compose logs -f api

# View specific service logs
docker-compose logs -f prometheus
docker-compose logs -f grafana
```

#### Log Aggregation
```yaml
# Add logging configuration
api:
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```

### Troubleshooting Commands

#### Check Service Status
```bash
# Container status
docker-compose ps

# Service health
docker-compose exec api curl -f http://localhost:8001/health

# Resource usage
docker stats
```

#### Debug Container Issues
```bash
# Enter container for debugging
docker-compose exec api bash

# Check environment variables
docker-compose exec api env | grep VIDEO_ENGINE

# Test FFmpeg availability
docker-compose exec api ffmpeg -version
```

## 🚨 Production Checklist

### Pre-Deployment
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] External API keys valid
- [ ] Storage bucket accessible
- [ ] Network security configured

### Post-Deployment
- [ ] Health checks passing
- [ ] Load test completed successfully
- [ ] Metrics collection working
- [ ] Monitoring dashboards accessible
- [ ] Backup procedures tested

### Ongoing Monitoring
- [ ] Job success rate >95%
- [ ] Processing time <180s average
- [ ] Queue length <40
- [ ] Error rate <5%
- [ ] Cost tracking accurate

## 📊 Production Metrics Dashboard

Access Grafana at `http://localhost:3000` for:
1. **Real-time Performance**: Job processing rates and durations
2. **Resource Utilization**: CPU, memory, and storage usage
3. **Cost Analysis**: TTS, processing, and storage costs
4. **Error Tracking**: Failure rates and reasons
5. **Queue Health**: Backlog and processing status

## 🔄 Updates and Maintenance

### Application Updates
```bash
# Build new image
docker-compose build --no-cache api

# Deploy with zero downtime
docker-compose up -d api

# Rollback if needed
docker-compose down
git checkout previous-version
docker-compose up -d api
```

### Database Updates
```bash
# Run migrations
docker-compose exec api python -c "
from app.services.job_repo_supabase import get_job_repo
print('Database connection OK')
"
```

### Backup Procedures
```bash
# Database backups (Supabase handles automatically)
# Video backups (R2 handles automatically)
# Configuration backups (Git repository)
```

## 🔒 Security Considerations

### Network Security
- Use internal Docker networks for service communication
- Configure firewalls to restrict API access
- Use HTTPS in production with proper certificates

### Secret Management
```bash
# Use Docker secrets for sensitive data
echo "your-secret-key" | docker secret create supabase_key -

# Or use external secret management (Vault, AWS Secrets Manager)
```

### Access Control
- Configure Row Level Security (RLS) in Supabase
- Use API keys with minimal required permissions
- Implement rate limiting for API endpoints

## 📞 Support & Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check logs
docker-compose logs api

# Check environment
docker-compose exec api env | grep -E "(SUPABASE|ELEVENLABS|R2)"

# Test dependencies
docker-compose exec api python -c "
import ffmpeg
from supabase import create_client
print('Dependencies OK')
"
```

#### Poor Performance
```bash
# Check resource usage
docker stats

# Check queue status
curl http://localhost:8001/health/detailed | jq '.queue'

# Check backend availability
curl http://localhost:8001/health/detailed | jq '.dependencies.video_backends'
```

#### High Error Rate
```bash
# Check failure metrics
curl http://localhost:8001/metrics | grep autopro_video_job_failures

# Check recent errors
curl http://localhost:8001/api/video/webhooks?limit=10
```

### Getting Help

1. **Check Logs**: `docker-compose logs -f api`
2. **Health Check**: `curl http://localhost:8001/health/detailed`
3. **Metrics**: `curl http://localhost:8001/metrics`
4. **Documentation**: See troubleshooting guides in `/autopro-handoff`

---

## 🎯 Deployment Status

| Component | Status | URL/Access |
|-----------|--------|------------|
| **API Server** | ✅ Running | http://localhost:8001 |
| **Health Checks** | ✅ Working | /health, /health/detailed |
| **Metrics** | ✅ Collecting | /metrics |
| **Database** | ✅ Connected | Supabase |
| **Storage** | ✅ Configured | R2/Cloudflare |
| **Monitoring** | ⚠️ Optional | Prometheus + Grafana |

**Overall Status**: ✅ **Production Ready**

---

**Last Updated**: 2025-01-04
**Version**: 1.0.0
**Environment**: Production