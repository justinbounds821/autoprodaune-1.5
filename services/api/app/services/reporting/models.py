"""
Reporting Models - Data structures for report generation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class ReportType(Enum):
    """Tipurile de rapoarte"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class ReportFormat(Enum):
    """Formatele de rapoarte"""
    JSON = "json"
    HTML = "html"
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"


class AlertLevel(Enum):
    """Nivelurile de alerte"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    SUCCESS = "success"


@dataclass
class ReportSection:
    """Secțiunea unui raport"""
    title: str
    content: Dict[str, Any]
    charts: List[Dict[str, Any]] = None  # type: ignore
    summary: str = ""
    
    def __post_init__(self):
        if self.charts is None:
            self.charts = []


@dataclass
class Alert:
    """Reprezentarea unei alerte"""
    id: str
    title: str
    message: str
    level: AlertLevel
    category: str
    timestamp: datetime
    kpi_name: Optional[str] = None
    threshold: Optional[float] = None
    current_value: Optional[float] = None
    resolved: bool = False


@dataclass
class Report:
    """Reprezentarea unui raport"""
    id: str
    title: str
    report_type: ReportType
    format: ReportFormat
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    sections: List[ReportSection]
    summary: str
    alerts: List[Alert]
    metadata: Dict[str, Any] = None  # type: ignore
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
