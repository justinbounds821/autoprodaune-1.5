"""
Monitoring Models - Data structures for monitoring system
"""

from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class MetricType(Enum):
    """Tipurile de metrici"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertLevel(Enum):
    """Nivelurile de alerte"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Reprezentarea unei metrici"""
    name: str
    value: float
    metric_type: MetricType
    labels: Dict[str, str]
    timestamp: datetime
    description: Optional[str] = None


@dataclass
class Alert:
    """Reprezentarea unei alerte"""
    id: str
    name: str
    level: AlertLevel
    message: str
    metric_name: str
    threshold: float
    current_value: float
    timestamp: datetime
    resolved: bool = False


@dataclass
class SystemHealth:
    """Reprezentarea stării sistemului"""
    status: str  # healthy, degraded, unhealthy
    uptime: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_connections: int
    error_rate: float
    response_time_avg: float
    timestamp: datetime
