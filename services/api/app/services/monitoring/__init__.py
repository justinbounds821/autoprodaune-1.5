"""
Monitoring Services Package
Modular system monitoring and metrics collection
"""

from .models import (
    MetricType,
    AlertLevel,
    Metric,
    Alert,
    SystemHealth
)
from .collectors import (
    SystemMetricsCollector,
    BusinessMetricsCollector
)
from .alerts import AlertManager
from .service import MonitoringService

# Singleton instance
_monitoring_service = None

def get_monitoring_service() -> MonitoringService:
    """Returnează instanța singleton a MonitoringService"""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service

__all__ = [
    "MetricType",
    "AlertLevel",
    "Metric",
    "Alert",
    "SystemHealth",
    "SystemMetricsCollector",
    "BusinessMetricsCollector",
    "AlertManager",
    "MonitoringService",
    "get_monitoring_service",
]
