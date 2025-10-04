# AutoPro Video Engine - Observability Guide

## 📊 Monitoring & Observability Overview

The AutoPro Video Engine includes comprehensive observability features for production monitoring, debugging, and performance optimization.

## 🔍 Available Metrics

### Core Job Metrics

#### `autopro_video_jobs_total{status,provider}`
- **Type**: Counter
- **Description**: Total number of video generation jobs by status
- **Labels**:
  - `status`: `queued`, `processing`, `completed`, `failed`, `cancelled`
  - `provider`: `internal` (currently only provider)
- **Example**:
  ```prometheus
  autopro_video_jobs_total{status="completed",provider="internal"} 150
  autopro_video_jobs_total{status="failed",provider="internal"} 5
  ```

#### `autopro_video_processing_duration_seconds{status}`
- **Type**: Histogram
- **Description**: Time spent processing video jobs
- **Labels**:
  - `status`: `completed`, `failed`
- **Buckets**: 1s, 5s, 10s, 30s, 60s, 120s, 300s, 600s, 1800s
- **Example**:
  ```prometheus
  autopro_video_processing_duration_seconds_bucket{status="completed",le="60"} 45
  autopro_video_processing_duration_seconds_bucket{status="completed",le="120"} 120
  ```

#### `autopro_video_tts_seconds_total`
- **Type**: Counter
- **Description**: Total seconds of TTS audio generated
- **Example**:
  ```prometheus
  autopro_video_tts_seconds_total 2340.5
  ```

### Queue & Concurrency Metrics

#### `autopro_video_queue_length`
- **Type**: Gauge
- **Description**: Current number of jobs in the processing queue
- **Example**:
  ```prometheus
  autopro_video_queue_length 3
  ```

#### `autopro_video_processing_jobs`
- **Type**: Gauge
- **Description**: Current number of jobs being processed
- **Example**:
  ```prometheus
  autopro_video_processing_jobs 2
  ```

### Error & Failure Metrics

#### `autopro_video_job_failures_total{failure_reason}`
- **Type**: Counter
- **Description**: Total number of failed video jobs by failure reason
- **Labels**:
  - `failure_reason`: `max_retries_exceeded`, `processing_error`, `queue_error`, `validation_error`
- **Example**:
  ```prometheus
  autopro_video_job_failures_total{failure_reason="processing_error"} 3
  ```

### Resource & Performance Metrics

#### `autopro_video_size_bytes`
- **Type**: Histogram
- **Description**: Size of generated video files
- **Buckets**: 1MB, 5MB, 10MB, 25MB, 50MB
- **Example**:
  ```prometheus
  autopro_video_size_bytes_bucket{le="5242880"} 45  # 5MB
  ```

#### `autopro_video_total_cost_cents`
- **Type**: Counter
- **Description**: Total cost of video generation in cents
- **Example**:
  ```prometheus
  autopro_video_total_cost_cents 1250  # $12.50 total
  ```

### Backend Availability

#### `autopro_video_backend_available{backend}`
- **Type**: Gauge
- **Description**: Availability status of video processing backends
- **Labels**:
  - `backend`: `sadtalker`, `wav2lip`, `ffmpeg`
- **Values**: `1` (available) or `0` (unavailable)
- **Example**:
  ```prometheus
  autopro_video_backend_available{backend="sadtalker"} 1
  autopro_video_backend_available{backend="ffmpeg"} 1
  ```

## 🏥 Health Check Endpoints

### Basic Health Check
```bash
GET /health
```

**Response**:
```json
{
  "status": "ok",
  "service": "autopro-video-engine",
  "timestamp": "2025-01-04T12:00:00Z",
  "version": "1.0.0"
}
```

### Detailed Health Check
```bash
GET /health/detailed
```

**Response**:
```json
{
  "status": "healthy",
  "service": "autopro-video-engine",
  "timestamp": "2025-01-04T12:00:00Z",
  "version": "1.0.0",
  "uptime": 3600.5,
  "dependencies": {
    "database": {
      "status": "ok",
      "message": "Database connected",
      "query_time_ms": 45.2,
      "recent_jobs_count": 15
    },
    "storage": {
      "status": "ok",
      "message": "R2 storage configured",
      "type": "r2",
      "bucket": "autopro-videos"
    },
    "tts": {
      "status": "ok",
      "message": "ElevenLabs TTS configured",
      "provider": "elevenlabs",
      "voice_id": "Rachel"
    },
    "video_backends": {
      "status": "ok",
      "backends": {
        "lipsync": {
          "status": "ok",
          "backend": "sadtalker",
          "message": "Lip-sync backend sadtalker available"
        },
        "ffmpeg": {
          "status": "ok",
          "message": "FFmpeg available",
          "version": "5.1.2"
        }
      }
    },
    "external_services": {
      "status": "ok",
      "services": {
        "webhook": {
          "status": "ok",
          "message": "Webhook endpoint reachable (status: 200)"
        }
      }
    }
  },
  "system": {
    "platform": "Linux-5.15.0-91-generic-x86_64",
    "python_version": "3.11.7",
    "cpu_count": 8,
    "memory": {
      "total": 17179869184,
      "available": 8589934592,
      "percent_used": 50.0
    },
    "disk": {
      "total": 259899059200,
      "free": 129949529600,
      "percent_used": 50.0
    }
  },
  "queue": {
    "total_jobs": 25,
    "processing_count": 2,
    "queue_length": 3,
    "concurrency_limit": 4,
    "queue_limit": 50,
    "status_counts": {
      "queued": 3,
      "processing": 2,
      "completed": 18,
      "failed": 2
    }
  }
}
```

## 📝 Structured Logging

### Log Format
All video engine operations use structured logging with consistent fields:

```json
{
  "timestamp": "2025-01-04T12:00:00.123Z",
  "level": "INFO",
  "logger": "services.video_engine",
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "phase": "tts_start",
  "message": "Starting TTS generation",
  "duration_ms": 150.5,
  "extra_fields": "..."
}
```

### Log Levels
- **DEBUG**: Detailed operation tracing
- **INFO**: Normal operational messages
- **WARNING**: Recoverable issues
- **ERROR**: Failed operations requiring attention

### Key Log Events

#### Job Lifecycle
```
🎬 Job {job_id}: processing_start - Started processing
🎬 Job {job_id}: tts_start - Starting TTS generation
🎬 Job {job_id}: tts_complete - TTS generated in 2.3s
🎬 Job {job_id}: timeline_start - Building video timeline
🎬 Job {job_id}: lipsync_start - Starting lip-sync with sadtalker
🎬 Job {job_id}: composition_start - Starting video composition
🎬 Job {job_id}: upload_start - Uploading video to storage
🎬 Job {job_id}: job_complete - Job completed successfully in 87.3s
```

#### Error Events
```
❌ Job {job_id}: job_failed - Job failed after 45.2s: TTS API timeout
🔄 Job {job_id}: start_attempt - Attempt 2/3
⏳ Job {job_id}: retry_wait - Waiting 12s before retry
```

## 📈 Grafana Dashboard Configuration

### Dashboard JSON Structure
```json
{
  "dashboard": {
    "title": "AutoPro Video Engine",
    "tags": ["autopro", "video", "production"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Job Success Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(autopro_video_jobs_total{status=\"completed\"}[5m]) / rate(autopro_video_jobs_total[5m]) * 100",
            "legendFormat": "Success Rate %"
          }
        ]
      },
      {
        "title": "Processing Duration",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(autopro_video_processing_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Queue Status",
        "type": "graph",
        "targets": [
          {
            "expr": "autopro_video_queue_length",
            "legendFormat": "Queue Length"
          },
          {
            "expr": "autopro_video_processing_jobs",
            "legendFormat": "Processing Jobs"
          }
        ]
      },
      {
        "title": "Cost Tracking",
        "type": "graph",
        "targets": [
          {
            "expr": "autopro_video_total_cost_cents / 100",
            "legendFormat": "Total Cost ($)"
          }
        ]
      }
    ]
  }
}
```

### Key Dashboard Panels

1. **Job Success Rate** - Overall system health indicator
2. **Processing Duration** - Performance monitoring
3. **Queue Status** - Load and capacity monitoring
4. **Cost Tracking** - Financial monitoring
5. **Error Rate** - Failure analysis
6. **Backend Availability** - Service health
7. **Resource Usage** - System performance

## 🚨 Alerting Rules

### Critical Alerts
```yaml
groups:
  - name: autopro-video-engine
    rules:
      - alert: HighFailureRate
        expr: |
          rate(autopro_video_job_failures_total[5m]) /
          rate(autopro_video_jobs_total[5m]) > 0.2
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High video job failure rate detected"
          description: "Failure rate is {{ $value }}%, above 20% threshold"

      - alert: QueueOverloaded
        expr: autopro_video_queue_length > 40
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Video processing queue overloaded"
          description: "Queue length is {{ $value }}, above 40 threshold"
```

### Warning Alerts
```yaml
      - alert: SlowProcessing
        expr: |
          histogram_quantile(0.95, rate(autopro_video_processing_duration_seconds_bucket[10m])) > 180
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Slow video processing detected"
          description: "95th percentile processing time is {{ $value }}s, above 180s threshold"

      - alert: BackendUnavailable
        expr: autopro_video_backend_available == 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Video backend unavailable"
          description: "Video processing backend is not available"
```

## 🔧 Monitoring Setup

### Prometheus Configuration
```yaml
scrape_configs:
  - job_name: 'autopro-video-engine'
    static_configs:
      - targets: ['api:8001']
    metrics_path: '/metrics'
    scrape_interval: 10s
    scrape_timeout: 5s
```

### Grafana Data Source
```json
{
  "name": "AutoPro Video Engine",
  "type": "prometheus",
  "url": "http://prometheus:9090",
  "access": "proxy",
  "isDefault": false
}
```

## 📋 Troubleshooting with Observability

### Common Issues & Diagnostics

#### 1. High Queue Length
**Symptoms**: `autopro_video_queue_length` > 20
**Diagnosis**:
- Check `autopro_video_processing_jobs` - if low, increase concurrency
- Check `autopro_video_processing_duration_seconds` - if high, investigate bottlenecks
- Check backend availability metrics

#### 2. High Failure Rate
**Symptoms**: `autopro_video_job_failures_total` increasing rapidly
**Diagnosis**:
- Check failure reasons in `autopro_video_job_failures_total{failure_reason}`
- Review detailed health check for service availability
- Check system resource metrics

#### 3. Slow Processing
**Symptoms**: `autopro_video_processing_duration_seconds` > 180s
**Diagnosis**:
- Check backend availability (`autopro_video_backend_available`)
- Review system resource usage in `/health/detailed`
- Check for external service timeouts (TTS, storage)

#### 4. Cost Overruns
**Symptoms**: `autopro_video_total_cost_cents` growing faster than expected
**Diagnosis**:
- Check `autopro_video_tts_seconds_total` for TTS usage
- Review `autopro_video_processing_duration_seconds` for processing time
- Check `autopro_video_size_bytes` for storage costs

### Debug Commands
```bash
# Check current metrics
curl http://localhost:8001/metrics | grep autopro_video

# Check detailed health
curl http://localhost:8001/health/detailed | jq '.dependencies'

# Check recent job failures
curl http://localhost:8001/api/video/templates
curl http://localhost:8001/api/video/webhooks

# Check queue status
curl http://localhost:8001/api/video/video/heygen/health
```

## 📊 Performance Benchmarks

### Expected Metric Values (Production)

| Metric | Expected Range | Alert Threshold |
|--------|---------------|-----------------|
| `autopro_video_jobs_total` | 100-1000/day | - |
| `autopro_video_processing_duration_seconds` | 60-120s | >180s |
| `autopro_video_queue_length` | 0-10 | >40 |
| `autopro_video_job_failures_total` | <5% of total | >20% |
| `autopro_video_size_bytes` | 3-8MB per video | >20MB |

### Resource Usage (Production Server)
- **CPU**: 40-70% during processing
- **Memory**: 60-80% of available RAM
- **Disk I/O**: 10-50 MB/s during composition
- **Network**: 1-5 Mbps for TTS API calls

---

## 📈 Key Insights from Metrics

### Performance Optimization
- **TTS Duration**: `autopro_video_tts_seconds_total` / `autopro_video_jobs_total` = cost per job
- **Processing Efficiency**: `autopro_video_processing_duration_seconds` trends over time
- **Queue Health**: `autopro_video_queue_length` vs `autopro_video_processing_jobs` ratio

### Cost Analysis
- **TTS Cost**: `autopro_video_tts_seconds_total` × TTS rate
- **Processing Cost**: `autopro_video_processing_duration_seconds` × processing rate
- **Storage Cost**: `autopro_video_size_bytes` × storage rate

### Reliability Monitoring
- **Success Rate**: `(completed jobs / total jobs) × 100`
- **Failure Patterns**: Breakdown by `failure_reason`
- **Retry Effectiveness**: Jobs that succeed after retries

---

**Last Updated**: 2025-01-04
**Version**: 1.0.0
**Status**: ✅ **Complete**