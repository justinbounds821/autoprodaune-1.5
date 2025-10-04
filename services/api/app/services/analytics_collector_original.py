"""
Analytics Collector - Serviciu pentru colectarea datelor din diverse surse pentru analytics
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import aiohttp
import requests
from sqlalchemy.orm import Session

# Configurează logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSource(Enum):
    """Sursele de date pentru analytics"""
    GOOGLE_SHEETS = "google_sheets"
    TELEGRAM_BOT = "telegram_bot"
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

class GoogleSheetsCollector:
    """Colector pentru date din Google Sheets"""
    
    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path or os.getenv("GOOGLE_CREDENTIALS_PATH")
        self.spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID")
        
    async def collect_lead_data(self) -> List[MetricData]:
        """Colectează date despre leads din Google Sheets"""
        metrics = []
        
        try:
            # Simulează colectarea datelor din Google Sheets
            # În producție, ar folosi Google Sheets API
            
            # Date simulate pentru leads
            lead_data = {
                "total_leads": 150,
                "new_leads_today": 12,
                "converted_leads": 45,
                "conversion_rate": 30.0,
                "avg_response_time": 2.5
            }
            
            for key, value in lead_data.items():
                metric = MetricData(
                    name=key,
                    value=value,
                    metric_type=MetricType.GAUGE,
                    labels={"source": "google_sheets"},
                    timestamp=datetime.now(),
                    source=DataSource.GOOGLE_SHEETS,
                    description=f"Lead metric: {key}"
                )
                metrics.append(metric)
                
            logger.info(f"Colectat {len(metrics)} metrici din Google Sheets")
            
        except Exception as e:
            logger.error(f"Eroare la colectarea datelor din Google Sheets: {str(e)}")
            
        return metrics

class TelegramBotCollector:
    """Colector pentru date din Telegram Bot"""
    
    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        
    async def collect_bot_metrics(self) -> List[MetricData]:
        """Colectează metrici despre bot-ul Telegram"""
        metrics = []
        
        try:
            if not self.bot_token:
                logger.warning("TELEGRAM_BOT_TOKEN nu este configurat")
                return metrics
                
            # Simulează colectarea datelor din Telegram Bot API
            bot_data = {
                "total_users": 1250,
                "active_users_today": 89,
                "messages_sent_today": 456,
                "commands_executed": 234,
                "error_rate": 2.1
            }
            
            for key, value in bot_data.items():
                metric = MetricData(
                    name=key,
                    value=value,
                    metric_type=MetricType.GAUGE,
                    labels={"source": "telegram_bot"},
                    timestamp=datetime.now(),
                    source=DataSource.TELEGRAM_BOT,
                    description=f"Telegram bot metric: {key}"
                )
                metrics.append(metric)
                
            logger.info(f"Colectat {len(metrics)} metrici din Telegram Bot")
            
        except Exception as e:
            logger.error(f"Eroare la colectarea datelor din Telegram Bot: {str(e)}")
            
        return metrics

class SocialMediaCollector:
    """Colector pentru date din social media"""
    
    def __init__(self):
        self.platforms = ["tiktok", "instagram", "youtube", "facebook"]
        
    async def collect_social_metrics(self) -> List[MetricData]:
        """Colectează metrici despre social media"""
        metrics = []
        
        try:
            # Simulează colectarea datelor din platformele sociale
            social_data = {
                "total_posts": 89,
                "posts_today": 5,
                "total_views": 45678,
                "total_likes": 1234,
                "total_comments": 567,
                "engagement_rate": 4.2,
                "reach_today": 2345
            }
            
            for key, value in social_data.items():
                metric = MetricData(
                    name=key,
                    value=value,
                    metric_type=MetricType.GAUGE,
                    labels={"source": "social_media"},
                    timestamp=datetime.now(),
                    source=DataSource.SOCIAL_MEDIA,
                    description=f"Social media metric: {key}"
                )
                metrics.append(metric)
                
            logger.info(f"Colectat {len(metrics)} metrici din Social Media")
            
        except Exception as e:
            logger.error(f"Eroare la colectarea datelor din Social Media: {str(e)}")
            
        return metrics

class VideoGenerationCollector:
    """Colector pentru date despre generarea video"""
    
    def __init__(self):
        pass
        
    async def collect_video_metrics(self) -> List[MetricData]:
        """Colectează metrici despre generarea video"""
        metrics = []
        
        try:
            # Simulează colectarea datelor din sistemul de generare video
            video_data = {
                "total_videos_generated": 45,
                "videos_today": 3,
                "total_processing_time": 234.5,
                "avg_generation_time": 45.2,
                "success_rate": 95.6,
                "failed_generations": 2,
                "total_cost": 125.50
            }
            
            for key, value in video_data.items():
                metric = MetricData(
                    name=key,
                    value=value,
                    metric_type=MetricType.GAUGE,
                    labels={"source": "video_generation"},
                    timestamp=datetime.now(),
                    source=DataSource.VIDEO_GENERATION,
                    description=f"Video generation metric: {key}"
                )
                metrics.append(metric)
                
            logger.info(f"Colectat {len(metrics)} metrici din Video Generation")
            
        except Exception as e:
            logger.error(f"Eroare la colectarea datelor din Video Generation: {str(e)}")
            
        return metrics

class FinancialCollector:
    """Colector pentru date financiare"""
    
    def __init__(self):
        pass
        
    async def collect_financial_metrics(self) -> List[MetricData]:
        """Colectează metrici financiare"""
        metrics = []
        
        try:
            # Simulează colectarea datelor financiare
            financial_data = {
                "total_revenue": 5678.90,
                "total_costs": 2345.67,
                "net_profit": 3333.23,
                "roi_percentage": 142.1,
                "cost_per_lead": 15.67,
                "revenue_per_lead": 37.86,
                "monthly_revenue": 1234.56
            }
            
            for key, value in financial_data.items():
                metric = MetricData(
                    name=key,
                    value=value,
                    metric_type=MetricType.GAUGE,
                    labels={"source": "financial"},
                    timestamp=datetime.now(),
                    source=DataSource.FINANCIAL,
                    description=f"Financial metric: {key}"
                )
                metrics.append(metric)
                
            logger.info(f"Colectat {len(metrics)} metrici financiare")
            
        except Exception as e:
            logger.error(f"Eroare la colectarea datelor financiare: {str(e)}")
            
        return metrics

class WebsiteCollector:
    """Colector pentru date despre website"""
    
    def __init__(self):
        self.website_url = os.getenv("WEBSITE_URL", "https://autoprodane.ro")
        
    async def collect_website_metrics(self) -> List[MetricData]:
        """Colectează metrici despre website"""
        metrics = []
        
        try:
            # Simulează colectarea datelor despre website
            website_data = {
                "total_visitors": 4567,
                "visitors_today": 234,
                "page_views": 12345,
                "bounce_rate": 35.6,
                "avg_session_duration": 2.5,
                "conversion_rate": 3.2,
                "top_pages": ["/", "/contact", "/services"]
            }
            
            for key, value in website_data.items():
                metric = MetricData(
                    name=key,
                    value=value if isinstance(value, (int, float)) else 0,
                    metric_type=MetricType.GAUGE,
                    labels={"source": "website"},
                    timestamp=datetime.now(),
                    source=DataSource.WEBSITE,
                    description=f"Website metric: {key}"
                )
                metrics.append(metric)
                
            logger.info(f"Colectat {len(metrics)} metrici din Website")
            
        except Exception as e:
            logger.error(f"Eroare la colectarea datelor din Website: {str(e)}")
            
        return metrics

class AnalyticsCollector:
    """Colector principal pentru analytics"""
    
    def __init__(self):
        self.google_sheets = GoogleSheetsCollector()
        self.telegram_bot = TelegramBotCollector()
        self.social_media = SocialMediaCollector()
        self.video_generation = VideoGenerationCollector()
        self.financial = FinancialCollector()
        self.website = WebsiteCollector()
        
        self.collectors = {
            DataSource.GOOGLE_SHEETS: self.google_sheets.collect_lead_data,
            DataSource.TELEGRAM_BOT: self.telegram_bot.collect_bot_metrics,
            DataSource.SOCIAL_MEDIA: self.social_media.collect_social_metrics,
            DataSource.VIDEO_GENERATION: self.video_generation.collect_video_metrics,
            DataSource.FINANCIAL: self.financial.collect_financial_metrics,
            DataSource.WEBSITE: self.website.collect_website_metrics
        }
    
    async def collect_all_metrics(self, sources: Optional[List[DataSource]] = None) -> List[MetricData]:
        """
        Colectează metrici din toate sursele sau din sursele specificate
        
        Args:
            sources: Lista de surse de date (None pentru toate)
            
        Returns:
            Lista cu toate metricile colectate
        """
        all_metrics = []
        
        sources_to_collect = sources or list(self.collectors.keys())
        
        logger.info(f"Încep colectarea metricilor din {len(sources_to_collect)} surse...")
        
        # Colectează metrici din fiecare sursă
        tasks = []
        for source in sources_to_collect:
            if source in self.collectors:
                tasks.append(self.collectors[source]())
        
        # Rulează toate task-urile în paralel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Procesează rezultatele
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Eroare la colectarea metricilor: {str(result)}")
            else:
                all_metrics.extend(result)
        
        logger.info(f"Colectat total {len(all_metrics)} metrici")
        return all_metrics
    
    async def collect_metrics_by_source(self, source: DataSource) -> List[MetricData]:
        """
        Colectează metrici dintr-o sursă specifică
        
        Args:
            source: Sursa de date
            
        Returns:
            Lista cu metricile din sursa specificată
        """
        if source not in self.collectors:
            logger.warning(f"Colector pentru {source.value} nu este disponibil")
            return []
        
        try:
            metrics = await self.collectors[source]()
            logger.info(f"Colectat {len(metrics)} metrici din {source.value}")
            return metrics
        except Exception as e:
            logger.error(f"Eroare la colectarea metricilor din {source.value}: {str(e)}")
            return []
    
    def get_available_sources(self) -> List[DataSource]:
        """Returnează lista de surse disponibile"""
        return list(self.collectors.keys())
    
    async def collect_custom_metric(
        self,
        name: str,
        value: Union[int, float],
        metric_type: MetricType,
        source: DataSource,
        labels: Optional[Dict[str, str]] = None,
        description: Optional[str] = None
    ) -> MetricData:
        """
        Colectează o metrică personalizată
        
        Args:
            name: Numele metricii
            value: Valoarea metricii
            metric_type: Tipul metricii
            source: Sursa de date
            labels: Etichete pentru metrică
            description: Descrierea metricii
            
        Returns:
            MetricData cu datele specificate
        """
        metric = MetricData(
            name=name,
            value=value,
            metric_type=metric_type,
            labels=labels or {},
            timestamp=datetime.now(),
            source=source,
            description=description
        )
        
        logger.info(f"Colectat metrică personalizată: {name} = {value}")
        return metric
    
    async def track_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        source: DataSource = DataSource.API_BACKEND
    ) -> AnalyticsEvent:
        """
        Urmărește un eveniment pentru analytics
        
        Args:
            event_type: Tipul evenimentului
            user_id: ID-ul utilizatorului
            session_id: ID-ul sesiunii
            properties: Proprietățile evenimentului
            source: Sursa de date
            
        Returns:
            AnalyticsEvent cu datele evenimentului
        """
        event = AnalyticsEvent(
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            properties=properties or {},
            timestamp=datetime.now(),
            source=source
        )
        
        logger.info(f"Urmărit eveniment: {event_type} de la {source.value}")
        return event

# Singleton instance
_analytics_collector = None

def get_analytics_collector() -> AnalyticsCollector:
    """Returnează instanța singleton a AnalyticsCollector"""
    global _analytics_collector
    if _analytics_collector is None:
        _analytics_collector = AnalyticsCollector()
    return _analytics_collector

# Funcții helper pentru colectarea rapidă
async def collect_all_analytics() -> List[MetricData]:
    """
    Funcție helper pentru colectarea tuturor metricilor
    
    Returns:
        Lista cu toate metricile
    """
    collector = get_analytics_collector()
    return await collector.collect_all_metrics()

async def collect_analytics_by_source(source: DataSource) -> List[MetricData]:
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
    user_id: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None
) -> AnalyticsEvent:
    """
    Funcție helper pentru urmărirea unui eveniment
    
    Args:
        event_type: Tipul evenimentului
        user_id: ID-ul utilizatorului
        properties: Proprietățile evenimentului
        
    Returns:
        AnalyticsEvent cu datele evenimentului
    """
    collector = get_analytics_collector()
    return await collector.track_event(event_type, user_id, properties=properties)
