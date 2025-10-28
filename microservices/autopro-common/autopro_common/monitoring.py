"""
Prometheus monitoring and OpenTelemetry tracing utilities
"""
import os
import time
from typing import Callable, Optional
from functools import wraps

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .logging import get_logger

logger = get_logger(__name__)


class PrometheusMetrics:
    """Prometheus metrics collector for FastAPI services"""

    def __init__(self, service_name: str, registry: Optional[CollectorRegistry] = None):
        """
        Initialize Prometheus metrics
        
        Args:
            service_name: Name of the microservice
            registry: Custom registry (creates new if None)
        """
        self.service_name = service_name
        self.registry = registry or CollectorRegistry()

        # HTTP metrics
        self.http_requests_total = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        self.http_request_duration_seconds = Histogram(
            "http_request_duration_seconds",
            "HTTP request latency",
            ["method", "endpoint"],
            registry=self.registry,
        )

        self.http_requests_in_progress = Gauge(
            "http_requests_in_progress",
            "HTTP requests in progress",
            ["method", "endpoint"],
            registry=self.registry,
        )

        # Database metrics
        self.db_queries_total = Counter(
            "db_queries_total",
            "Total database queries",
            ["table", "operation"],
            registry=self.registry,
        )

        self.db_query_duration_seconds = Histogram(
            "db_query_duration_seconds",
            "Database query latency",
            ["table", "operation"],
            registry=self.registry,
        )

        self.db_connections = Gauge(
            "db_connections",
            "Active database connections",
            registry=self.registry,
        )

        # Cache metrics
        self.cache_hits_total = Counter(
            "cache_hits_total",
            "Total cache hits",
            registry=self.registry,
        )

        self.cache_misses_total = Counter(
            "cache_misses_total",
            "Total cache misses",
            registry=self.registry,
        )

        # Queue metrics
        self.queue_messages_published = Counter(
            "queue_messages_published",
            "Total messages published to queue",
            ["queue"],
            registry=self.registry,
        )

        self.queue_messages_consumed = Counter(
            "queue_messages_consumed",
            "Total messages consumed from queue",
            ["queue"],
            registry=self.registry,
        )

        self.queue_processing_duration_seconds = Histogram(
            "queue_processing_duration_seconds",
            "Queue message processing time",
            ["queue"],
            registry=self.registry,
        )

        # Business metrics (generic counter and gauge)
        self.business_events = Counter(
            "business_events_total",
            "Business events counter",
            ["event_type"],
            registry=self.registry,
        )

        self.business_gauge = Gauge(
            "business_metric",
            "Business metric gauge",
            ["metric_name"],
            registry=self.registry,
        )

        logger.info(f"Prometheus metrics initialized for {service_name}")

    def track_http_request(
        self,
        method: str,
        endpoint: str,
        status: int,
        duration: float,
    ) -> None:
        """Track HTTP request metrics"""
        self.http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        self.http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

    def track_db_query(
        self,
        table: str,
        operation: str,
        duration: float,
    ) -> None:
        """Track database query metrics"""
        self.db_queries_total.labels(table=table, operation=operation).inc()
        self.db_query_duration_seconds.labels(table=table, operation=operation).observe(duration)

    def track_cache_hit(self) -> None:
        """Track cache hit"""
        self.cache_hits_total.inc()

    def track_cache_miss(self) -> None:
        """Track cache miss"""
        self.cache_misses_total.inc()

    def track_queue_publish(self, queue: str) -> None:
        """Track message published to queue"""
        self.queue_messages_published.labels(queue=queue).inc()

    def track_queue_consume(self, queue: str, duration: float) -> None:
        """Track message consumed from queue"""
        self.queue_messages_consumed.labels(queue=queue).inc()
        self.queue_processing_duration_seconds.labels(queue=queue).observe(duration)

    def track_business_event(self, event_type: str) -> None:
        """Track business event"""
        self.business_events.labels(event_type=event_type).inc()

    def set_business_metric(self, metric_name: str, value: float) -> None:
        """Set business metric gauge"""
        self.business_gauge.labels(metric_name=metric_name).set(value)

    def export_metrics(self) -> bytes:
        """Export metrics in Prometheus format"""
        return generate_latest(self.registry)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for automatic Prometheus metrics collection"""

    def __init__(self, app, metrics: PrometheusMetrics):
        super().__init__(app)
        self.metrics = metrics

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Track all HTTP requests automatically"""
        method = request.method
        endpoint = request.url.path

        # Skip metrics endpoint itself
        if endpoint == "/metrics":
            return await call_next(request)

        # Track in-progress requests
        self.metrics.http_requests_in_progress.labels(
            method=method,
            endpoint=endpoint,
        ).inc()

        # Measure request duration
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Track metrics
            self.metrics.track_http_request(
                method=method,
                endpoint=endpoint,
                status=response.status_code,
                duration=duration,
            )
            
            return response
            
        finally:
            # Decrement in-progress counter
            self.metrics.http_requests_in_progress.labels(
                method=method,
                endpoint=endpoint,
            ).dec()


# Global metrics instance
_metrics_instance: Optional[PrometheusMetrics] = None


def init_metrics(service_name: str) -> PrometheusMetrics:
    """
    Initialize global Prometheus metrics
    
    Args:
        service_name: Name of the microservice
        
    Returns:
        PrometheusMetrics instance
    """
    global _metrics_instance
    _metrics_instance = PrometheusMetrics(service_name)
    return _metrics_instance


def get_metrics() -> PrometheusMetrics:
    """
    Get global Prometheus metrics instance
    
    Returns:
        PrometheusMetrics instance
        
    Raises:
        RuntimeError: If metrics not initialized
    """
    if _metrics_instance is None:
        raise RuntimeError("Metrics not initialized. Call init_metrics() first.")
    return _metrics_instance


def setup_metrics(app, service_name: str) -> PrometheusMetrics:
    """
    Setup Prometheus metrics for FastAPI app
    
    Args:
        app: FastAPI application
        service_name: Name of the microservice
        
    Returns:
        PrometheusMetrics instance
    """
    metrics = init_metrics(service_name)
    
    # Add middleware for automatic tracking
    app.add_middleware(PrometheusMiddleware, metrics=metrics)
    
    # Add /metrics endpoint
    @app.get("/metrics")
    async def metrics_endpoint():
        return Response(
            content=metrics.export_metrics(),
            media_type=CONTENT_TYPE_LATEST,
        )
    
    logger.info(f"Prometheus metrics endpoint enabled at /metrics")
    
    return metrics
