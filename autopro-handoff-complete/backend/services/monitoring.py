"""
Monitoring Service - Wrapper compatibil pentru sistemul modular
"""

from .monitoring import (
    MonitoringService,
    MetricType,
    AlertLevel,
    Metric,
    Alert,
    SystemHealth,
    SystemMetricsCollector,
    BusinessMetricsCollector,
    AlertManager
)

# Singleton instance
_monitoring_service = None

def get_monitoring_service() -> MonitoringService:
    """Returnează instanța singleton a MonitoringService"""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service

# Funcții helper pentru colectarea rapidă
async def collect_metrics() -> list:
    """
    Funcție helper pentru colectarea metricilor
    
    Returns:
        Lista cu toate metricile
    """
    service = get_monitoring_service()
    return await service.collect_all_metrics()

def get_system_health() -> SystemHealth:
    """
    Funcție helper pentru obținerea stării sistemului
    
    Returns:
        SystemHealth cu starea sistemului
    """
    service = get_monitoring_service()
    return service.get_system_health()

def record_request_metric(response_time: float, is_error: bool = False):
    """
    Funcție helper pentru înregistrarea unei cereri
    
    Args:
        response_time: Timpul de răspuns în secunde
        is_error: Dacă cererea a rezultat într-o eroare
    """
    service = get_monitoring_service()
    service.record_request(response_time, is_error)

__all__ = [
    "MonitoringService",
    "MetricType",
    "AlertLevel",
    "Metric",
    "Alert",
    "SystemHealth",
    "SystemMetricsCollector",
    "BusinessMetricsCollector",
    "AlertManager",
    "get_monitoring_service",
    "collect_metrics",
    "get_system_health",
    "record_request_metric"
]
