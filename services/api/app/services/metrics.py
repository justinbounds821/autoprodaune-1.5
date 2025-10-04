# services/api/app/services/metrics.py
"""
Prometheus metrics service for AutoPro Video Engine.
SRP: Metrics collection only, no business logic.
"""
import os
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MetricsService:
    """Service for collecting and exposing Prometheus metrics."""

    def __init__(self):
        """Initialize metrics service."""
        self.enabled = os.getenv("PROMETHEUS_METRICS_ENABLED", "false").lower() in ("1", "true", "yes")

        if not self.enabled:
            logger.info("Prometheus metrics disabled")
            return

        try:
            from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest

            # Create custom registry for video engine metrics
            self.registry = CollectorRegistry()

            # Job lifecycle metrics
            self.jobs_total = Counter(
                'autopro_video_jobs_total',
                'Total number of video generation jobs',
                ['status', 'provider'],
                registry=self.registry
            )

            # Processing duration histogram
            self.processing_duration_seconds = Histogram(
                'autopro_video_processing_duration_seconds',
                'Time spent processing video jobs',
                ['status'],
                buckets=(1, 5, 10, 30, 60, 120, 300, 600, 1800),
                registry=self.registry
            )

            # TTS duration counter
            self.tts_seconds_total = Counter(
                'autopro_video_tts_seconds_total',
                'Total seconds of TTS audio generated',
                registry=self.registry
            )

            # Queue metrics
            self.queue_length = Gauge(
                'autopro_video_queue_length',
                'Current number of jobs in queue',
                registry=self.registry
            )

            self.processing_jobs = Gauge(
                'autopro_video_processing_jobs',
                'Current number of jobs being processed',
                registry=self.registry
            )

            # Error metrics
            self.job_failures_total = Counter(
                'autopro_video_job_failures_total',
                'Total number of failed video jobs',
                ['failure_reason'],
                registry=self.registry
            )

            # Storage metrics
            self.video_size_bytes = Histogram(
                'autopro_video_size_bytes',
                'Size of generated video files',
                buckets=(1024*1024, 5*1024*1024, 10*1024*1024, 25*1024*1024, 50*1024*1024),
                registry=self.registry
            )

            # Cost metrics (in cents)
            self.total_cost_cents = Counter(
                'autopro_video_total_cost_cents',
                'Total cost of video generation in cents',
                registry=self.registry
            )

            # Backend availability
            self.backend_available = Gauge(
                'autopro_video_backend_available',
                'Availability of video processing backends',
                ['backend'],
                registry=self.registry
            )

            logger.info("✅ Prometheus metrics service initialized")

        except ImportError:
            logger.warning("prometheus_client not available, metrics disabled")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize metrics service: {e}")
            self.enabled = False

    def record_job_status(self, status: str, provider: str = "internal") -> None:
        """Record job status change."""
        if not self.enabled:
            return

        try:
            self.jobs_total.labels(status=status, provider=provider).inc()
            logger.debug(f"Recorded job status: {status}")
        except Exception as e:
            logger.error(f"Failed to record job status metric: {e}")

    def record_processing_duration(self, duration_seconds: float, status: str) -> None:
        """Record processing duration."""
        if not self.enabled:
            return

        try:
            self.processing_duration_seconds.labels(status=status).observe(duration_seconds)
            logger.debug(f"Recorded processing duration: {duration_seconds:.2f}s ({status})")
        except Exception as e:
            logger.error(f"Failed to record processing duration metric: {e}")

    def record_tts_duration(self, duration_seconds: float) -> None:
        """Record TTS audio duration."""
        if not self.enabled:
            return

        try:
            self.tts_seconds_total.inc(duration_seconds)
            logger.debug(f"Recorded TTS duration: {duration_seconds:.2f}s")
        except Exception as e:
            logger.error(f"Failed to record TTS duration metric: {e}")

    def update_queue_metrics(self, queue_length: int, processing_count: int) -> None:
        """Update queue-related metrics."""
        if not self.enabled:
            return

        try:
            self.queue_length.set(queue_length)
            self.processing_jobs.set(processing_count)
            logger.debug(f"Updated queue metrics: queue={queue_length}, processing={processing_count}")
        except Exception as e:
            logger.error(f"Failed to update queue metrics: {e}")

    def record_job_failure(self, reason: str) -> None:
        """Record job failure with reason."""
        if not self.enabled:
            return

        try:
            self.job_failures_total.labels(failure_reason=reason).inc()
            logger.debug(f"Recorded job failure: {reason}")
        except Exception as e:
            logger.error(f"Failed to record job failure metric: {e}")

    def record_video_size(self, size_bytes: int) -> None:
        """Record generated video file size."""
        if not self.enabled:
            return

        try:
            self.video_size_bytes.observe(size_bytes)
            logger.debug(f"Recorded video size: {size_bytes} bytes")
        except Exception as e:
            logger.error(f"Failed to record video size metric: {e}")

    def record_total_cost(self, cost_cents: int) -> None:
        """Record total cost in cents."""
        if not self.enabled:
            return

        try:
            self.total_cost_cents.inc(cost_cents)
            logger.debug(f"Recorded total cost: {cost_cents} cents")
        except Exception as e:
            logger.error(f"Failed to record cost metric: {e}")

    def set_backend_availability(self, backend: str, available: bool) -> None:
        """Set backend availability status."""
        if not self.enabled:
            return

        try:
            self.backend_available.labels(backend=backend).set(1 if available else 0)
            logger.debug(f"Set backend availability: {backend}={available}")
        except Exception as e:
            logger.error(f"Failed to set backend availability metric: {e}")

    def get_metrics_text(self) -> str:
        """Get current metrics in Prometheus text format."""
        if not self.enabled:
            return "# Metrics disabled"

        try:
            from prometheus_client import generate_latest
            return generate_latest(self.registry).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to generate metrics text: {e}")
            return "# Error generating metrics"

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of current metrics values."""
        if not self.enabled:
            return {"enabled": False, "error": "Metrics disabled"}

        try:
            # This would typically sample current values from the metrics
            # For now, return basic info
            return {
                "enabled": True,
                "metrics": [
                    "autopro_video_jobs_total",
                    "autopro_video_processing_duration_seconds",
                    "autopro_video_tts_seconds_total",
                    "autopro_video_queue_length",
                    "autopro_video_processing_jobs",
                    "autopro_video_job_failures_total",
                    "autopro_video_size_bytes",
                    "autopro_video_total_cost_cents",
                    "autopro_video_backend_available"
                ],
                "registry_size": len(self.registry.collect())
            }
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {"enabled": False, "error": str(e)}

# Global instance
_metrics_service = None

def get_metrics_service() -> MetricsService:
    """Get or create global metrics service instance."""
    global _metrics_service
    if _metrics_service is None:
        _metrics_service = MetricsService()
    return _metrics_service