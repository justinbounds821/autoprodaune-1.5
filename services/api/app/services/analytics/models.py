"""
Analytics Models - Data structures for analytics system
"""

from typing import Dict, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class DataSource(Enum):
    """Sursele de date pentru analytics"""
    GOOGLE_SHEETS = "google_sheets"
    WHATSAPP_BUSINESS = "whatsapp_business"
    SOCIAL_MEDIA = "social_media"
    VIDEO_GENERATION = "video_generation"
    FINANCIAL = "financial"
    WEBSITE = "website"
    N8N_WORKFLOWS = "n8n_workflows"
    CLOUDFLARE_R2 = "cloudflare_r2"
    API_BACKEND = "api_backend"


class MetricType(Enum):
    """Tipurile de metrici"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricData:
    """Reprezentarea unei metrici"""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    labels: Dict[str, str]
    timestamp: datetime
    source: DataSource
    description: Optional[str] = None


@dataclass
class AnalyticsEvent:
    """Reprezentarea unui eveniment pentru analytics"""
    event_type: str
    user_id: Optional[str]
    session_id: Optional[str]
    properties: Dict[str, Any]
    timestamp: datetime
    source: DataSource
