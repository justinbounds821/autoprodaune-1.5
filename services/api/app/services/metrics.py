"""
Metrics Service - Prometheus metrics collection
Single Responsibility: Expose application metrics for monitoring
Safe-by-default: Disabled unless PROMETHEUS_METRICS_ENABLED=true
"""
import os
import logging
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

logger = logging.getLogger(__name__)


class MetricsService:
    """
    Collect and expose Prometheus metrics for monitoring.
    Tracks job counts, processing times, errors, etc.
    """
    
    def __init__(self):
        self.enabled = os.getenv("PROMETHEUS_METRICS_ENABLED", "false").lower() == "true"
        self.registry = CollectorRegistry()
        
        if not self.enabled:
            logger.info("⚠️ Prometheus metrics disabled (PROMETHEUS_METRICS_ENABLED=false)")
            return
        
        # Initialize metrics
        self._init_metrics()
        logger.info("✅ Prometheus metrics enabled")
    
    def _init_metrics(self):
        """Initialize Prometheus metric collectors"""
        # Job counters
        self.jobs_created = Counter(
            'autopro_jobs_created_total',
            'Total number of jobs created',
            ['status'],
            registry=self.registry
        )
        
        self.jobs_completed = Counter(
            'autopro_jobs_completed_total',
            'Total number of jobs completed',
            registry=self.registry
        )
        
        self.jobs_failed = Counter(
            'autopro_jobs_failed_total',
            'Total number of jobs failed',
            ['error_type'],
            registry=self.registry
        )
        
        # Processing time histograms
        self.job_duration = Histogram(
            'autopro_job_duration_seconds',
            'Job processing duration in seconds',
            ['job_type'],
            registry=self.registry
        )
        
        self.tts_duration = Histogram(
            'autopro_tts_duration_seconds',
            'TTS generation duration in seconds',
            registry=self.registry
        )
        
        self.video_render_duration = Histogram(
            'autopro_video_render_duration_seconds',
            'Video rendering duration in seconds',
            registry=self.registry
        )
        
        # Queue metrics
        self.queue_size = Gauge(
            'autopro_queue_size',
            'Current job queue size',
            ['status'],
            registry=self.registry
        )
        
        # Cost metrics
        self.total_cost = Counter(
            'autopro_total_cost_cents',
            'Total processing cost in cents',
            ['service'],
            registry=self.registry
        )
        
        # AI feature metrics
        self.ai_insights_generated = Counter(
            'autopro_ai_insights_generated_total',
            'Total AI insights generated',
            registry=self.registry
        )
        
        self.vector_searches = Counter(
            'autopro_vector_searches_total',
            'Total vector similarity searches performed',
            registry=self.registry
        )
        
        self.captions_generated = Counter(
            'autopro_captions_generated_total',
            'Total caption files generated',
            ['format'],
            registry=self.registry
        )
    
    def record_job_created(self, status: str = "pending"):
        """Record new job creation"""
        if self.enabled:
            self.jobs_created.labels(status=status).inc()
    
    def record_job_completed(self):
        """Record job completion"""
        if self.enabled:
            self.jobs_completed.inc()
    
    def record_job_failed(self, error_type: str = "unknown"):
        """Record job failure"""
        if self.enabled:
            self.jobs_failed.labels(error_type=error_type).inc()
    
    def record_job_duration(self, duration_seconds: float, job_type: str = "default"):
        """Record job processing duration"""
        if self.enabled:
            self.job_duration.labels(job_type=job_type).observe(duration_seconds)
    
    def record_tts_duration(self, duration_seconds: float):
        """Record TTS generation duration"""
        if self.enabled:
            self.tts_duration.observe(duration_seconds)
    
    def record_video_render_duration(self, duration_seconds: float):
        """Record video rendering duration"""
        if self.enabled:
            self.video_render_duration.observe(duration_seconds)
    
    def set_queue_size(self, size: int, status: str = "pending"):
        """Update queue size gauge"""
        if self.enabled:
            self.queue_size.labels(status=status).set(size)
    
    def record_cost(self, amount_cents: float, service: str):
        """Record processing cost"""
        if self.enabled:
            self.total_cost.labels(service=service).inc(amount_cents)
    
    def record_ai_insight(self):
        """Record AI insight generation"""
        if self.enabled:
            self.ai_insights_generated.inc()
    
    def record_vector_search(self):
        """Record vector search query"""
        if self.enabled:
            self.vector_searches.inc()
    
    def record_caption_generated(self, format: str = "srt"):
        """Record caption file generation"""
        if self.enabled:
            self.captions_generated.labels(format=format).inc()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of current metrics"""
        if not self.enabled:
            return {"enabled": False}
        
        # Note: In production, these would be fetched from Prometheus
        return {
            "enabled": True,
            "metrics_available": [
                "autopro_jobs_created_total",
                "autopro_jobs_completed_total",
                "autopro_jobs_failed_total",
                "autopro_job_duration_seconds",
                "autopro_queue_size",
                "autopro_total_cost_cents"
            ]
        }
    
    def get_health(self) -> Dict[str, Any]:
        """Health check for metrics service"""
        return {
            "enabled": self.enabled,
            "registry_collectors": len(self.registry._collector_to_names) if self.enabled else 0
        }


# Singleton instance
_instance = None

def get_metrics_service() -> MetricsService:
    """Get or create MetricsService singleton"""
    global _instance
    if _instance is None:
        _instance = MetricsService()
    return _instance
