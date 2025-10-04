"""
Analytics Reporter - Main orchestrator for analytics operations
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from .models import DataSource, MetricType, MetricData, AnalyticsEvent
from .collectors import (
    GoogleSheetsCollector,
    WhatsAppBusinessCollector,
    SocialMediaCollector,
    VideoGenerationCollector,
    FinancialCollector,
    WebsiteCollector
)
from .processor import AnalyticsProcessor

logger = logging.getLogger(__name__)


class AnalyticsReporter:
    """Reporter principal pentru analytics"""
    
    def __init__(self):
        self.google_sheets = GoogleSheetsCollector()
        self.whatsapp_business = WhatsAppBusinessCollector()
        self.social_media = SocialMediaCollector()
        self.video_generation = VideoGenerationCollector()
        self.financial = FinancialCollector()
        self.website = WebsiteCollector()
        self.processor = AnalyticsProcessor()

        self.collectors = {
            DataSource.GOOGLE_SHEETS: self.google_sheets.collect_lead_data,
            DataSource.WHATSAPP_BUSINESS: self.whatsapp_business.collect_whatsapp_metrics,
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
    
    def process_metrics(self, metrics: List[MetricData]) -> Dict[str, Any]:
        """Procesează metricile și returnează statistici"""
        return self.processor.process_metrics(metrics)
    
    def filter_metrics_by_source(self, metrics: List[MetricData], source: DataSource) -> List[MetricData]:
        """Filtrează metricile după sursă"""
        return self.processor.filter_metrics_by_source(metrics, source)
    
    def filter_metrics_by_type(self, metrics: List[MetricData], metric_type: MetricType) -> List[MetricData]:
        """Filtrează metricile după tip"""
        return self.processor.filter_metrics_by_type(metrics, metric_type)
    
    def filter_metrics_by_time_range(
        self, 
        metrics: List[MetricData], 
        start_time: datetime, 
        end_time: datetime
    ) -> List[MetricData]:
        """Filtrează metricile după interval de timp"""
        return self.processor.filter_metrics_by_time_range(metrics, start_time, end_time)
    
    def aggregate_metrics(self, metrics: List[MetricData], group_by: str = "source") -> Dict[str, Any]:
        """Agregă metricile după un criteriu"""
        return self.processor.aggregate_metrics(metrics, group_by)
    
    def calculate_trends(self, metrics: List[MetricData], metric_name: str) -> Dict[str, Any]:
        """Calculează tendințele pentru o metrică specifică"""
        return self.processor.calculate_trends(metrics, metric_name)
    
    def generate_insights(self, metrics: List[MetricData]) -> List[str]:
        """Generează insights pe baza metricilor"""
        return self.processor.generate_insights(metrics)
