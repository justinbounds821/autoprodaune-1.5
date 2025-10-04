"""
Analytics Collector - Wrapper compatibil pentru sistemul modular
"""

from .analytics import (
    AnalyticsReporter,
    DataSource,
    MetricType,
    MetricData,
    AnalyticsEvent,
    GoogleSheetsCollector,
    WhatsAppBusinessCollector,
    SocialMediaCollector,
    VideoGenerationCollector,
    FinancialCollector,
    WebsiteCollector
)

# Singleton instance
_analytics_collector = None

def get_analytics_collector() -> AnalyticsReporter:
    """Returnează instanța singleton a AnalyticsReporter"""
    global _analytics_collector
    if _analytics_collector is None:
        _analytics_collector = AnalyticsReporter()
    return _analytics_collector

# Funcții helper pentru colectarea rapidă
async def collect_all_analytics() -> list:
    """
    Funcție helper pentru colectarea tuturor metricilor
    
    Returns:
        Lista cu toate metricile colectate
    """
    collector = get_analytics_collector()
    return await collector.collect_all_metrics()

async def collect_analytics_by_source(source: DataSource) -> list:
    """
    Funcție helper pentru colectarea metricilor dintr-o sursă specifică
    
    Args:
        source: Sursa de date
        
    Returns:
        Lista cu metricile din sursa specificată
    """
    collector = get_analytics_collector()
    return await collector.collect_metrics_by_source(source)

async def track_analytics_event(
    event_type: str,
    user_id: str = None,
    session_id: str = None,
    properties: dict = None,
    source: DataSource = DataSource.API_BACKEND
) -> AnalyticsEvent:
    """
    Funcție helper pentru urmărirea evenimentelor
    
    Args:
        event_type: Tipul evenimentului
        user_id: ID-ul utilizatorului
        session_id: ID-ul sesiunii
        properties: Proprietățile evenimentului
        source: Sursa de date
        
    Returns:
        AnalyticsEvent cu datele evenimentului
    """
    collector = get_analytics_collector()
    return await collector.track_event(event_type, user_id, session_id, properties, source)

__all__ = [
    "AnalyticsReporter",
    "DataSource",
    "MetricType", 
    "MetricData",
    "AnalyticsEvent",
    "GoogleSheetsCollector",
    "TelegramBotCollector",
    "SocialMediaCollector",
    "VideoGenerationCollector",
    "FinancialCollector",
    "WebsiteCollector",
    "get_analytics_collector",
    "collect_all_analytics",
    "collect_analytics_by_source",
    "track_analytics_event"
]
