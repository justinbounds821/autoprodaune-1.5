"""
Analytics Collectors - Individual data collectors for different sources
"""

import os
import logging
import inspect
from typing import Dict, Any, List, Optional
from datetime import datetime
from .models import DataSource, MetricType, MetricData

logger = logging.getLogger(__name__)


class BaseMetricsCollector:
    """Funcționalități comune pentru colectorii de metrici."""

    def __init__(self, cache: Optional[Any] = None):
        self.cache = cache

    async def _fetch_from_cache(self, key: str) -> Optional[Any]:
        if not self.cache:
            return None

        try:
            cached_value = self.cache.get(key)
            if inspect.isawaitable(cached_value):
                cached_value = await cached_value
            return cached_value
        except Exception as exc:
            logger.warning("Nu s-a putut accesa cache-ul pentru %s: %s", key, exc)
            return None

    async def _safe_call_provider(
        self,
        provider: Any,
        candidate_methods: List[str],
        *,
        context: str,
    ) -> Optional[Any]:
        for method_name in candidate_methods:
            if hasattr(provider, method_name):
                method = getattr(provider, method_name)
                try:
                    result = method()
                    if inspect.isawaitable(result):
                        result = await result
                    return result
                except Exception as exc:
                    raise RuntimeError(
                        f"{context} provider method '{method_name}' failed: {exc}"
                    ) from exc
        raise RuntimeError(
            f"No supported provider methods found for {context} metrics collection"
        )

    async def _query_supabase_table(self, client: Any, table_name: str) -> Optional[Any]:
        try:
            query = client.table(table_name).select("*")
        except AttributeError as exc:
            raise RuntimeError(
                "Supabase client nu expune interfața table(...).select(...)"
            ) from exc

        try:
            response = query.execute() if hasattr(query, "execute") else query
            if inspect.isawaitable(response):
                response = await response
        except Exception as exc:
            raise RuntimeError(
                f"Interogarea Supabase pentru tabelul '{table_name}' a eșuat: {exc}"
            ) from exc

        if isinstance(response, dict):
            return response.get("data") or response
        if hasattr(response, "data"):
            return response.data
        return response

    def _build_metrics_from_payload(
        self,
        payload: Any,
        *,
        source: DataSource,
        default_description: str,
    ) -> List[MetricData]:
        metrics: List[MetricData] = []

        def _append_metric(
            metric_name: str, metric_value: Any, description: Optional[str] = None
        ) -> None:
            if not isinstance(metric_value, (int, float)):
                logger.debug(
                    "Valoarea pentru metrica %s nu este numerică și va fi ignorată",
                    metric_name,
                )
                return

            metrics.append(
                MetricData(
                    name=metric_name,
                    value=metric_value,
                    metric_type=MetricType.GAUGE,
                    labels={"source": source.value},
                    timestamp=datetime.now(),
                    source=source,
                    description=description or f"{default_description}: {metric_name}",
                )
            )

        if isinstance(payload, dict):
            for key, value in payload.items():
                _append_metric(key, value)
        elif isinstance(payload, list):
            for entry in payload:
                if isinstance(entry, dict):
                    if "name" in entry and "value" in entry:
                        _append_metric(entry["name"], entry["value"], entry.get("description"))
                    else:
                        for key, value in entry.items():
                            _append_metric(key, value)
                else:
                    logger.debug("Element payload necunoscut: %s", entry)
        else:
            raise TypeError(
                "Payload-ul pentru metrici trebuie să fie dict sau listă de dict-uri"
            )

        return metrics


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


class WhatsAppBusinessCollector:
    """Colector pentru date din WhatsApp Business API"""

    def __init__(self, access_token: Optional[str] = None, phone_number_id: Optional[str] = None):
        self.access_token = access_token or os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.phone_number_id = phone_number_id or os.getenv("WHATSAPP_PHONE_NUMBER_ID")

    async def collect_whatsapp_metrics(self) -> List[MetricData]:
        """Colectează metrici despre WhatsApp Business"""
        metrics = []

        try:
            if not self.access_token:
                logger.warning("WHATSAPP_ACCESS_TOKEN nu este configurat")
                return metrics

            # Simulează colectarea datelor din WhatsApp Business API
            whatsapp_data = {
                "total_contacts": 1450,
                "messages_sent_today": 89,
                "messages_received_today": 156,
                "active_conversations": 34,
                "response_rate": 95.2,
                "average_response_time": 3.4  # minutes
            }

            for key, value in whatsapp_data.items():
                metric = MetricData(
                    name=key,
                    value=value,
                    metric_type=MetricType.GAUGE,
                    labels={"source": "whatsapp_business"},
                    timestamp=datetime.now(),
                    source=DataSource.WHATSAPP_BUSINESS,
                    description=f"WhatsApp Business metric: {key}"
                )
                metrics.append(metric)

            logger.info(f"Colectat {len(metrics)} metrici din WhatsApp Business")

        except Exception as e:
            logger.error(f"Eroare la colectarea datelor din WhatsApp Business: {str(e)}")

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


class VideoGenerationCollector(BaseMetricsCollector):
    """Colector pentru date despre generarea video"""

    def __init__(
        self,
        supabase_client: Optional[Any] = None,
        cache: Optional[Any] = None,
        video_metrics_repository: Optional[Any] = None,
        external_api: Optional[Any] = None,
    ):
        """Permite injectarea dependențelor necesare colectării metricilor."""

        super().__init__(cache=cache)

        self.supabase_client = supabase_client
        self.video_metrics_repository = video_metrics_repository
        self.external_api = external_api
        
    async def collect_video_metrics(self) -> List[MetricData]:
        """Colectează metrici despre generarea video"""
        metrics = []

        try:
            video_data = await self._get_video_metrics_from_dependencies()

            if not video_data:
                logger.warning("Nu există date de generare video disponibile")
                return metrics

            metrics.extend(
                self._build_metrics_from_payload(
                    payload=video_data,
                    source=DataSource.VIDEO_GENERATION,
                    default_description="Video generation metric",
                )
            )

            logger.info(f"Colectat {len(metrics)} metrici din Video Generation")

        except Exception as exc:
            logger.error("Eroare la colectarea datelor din Video Generation: %s", exc)
            raise

        return metrics

    async def _get_video_metrics_from_dependencies(self) -> Optional[Any]:
        """Extrage metricile de generare video din dependențele configurate."""

        if not any([self.supabase_client, self.cache, self.video_metrics_repository, self.external_api]):
            raise RuntimeError(
                "Niciun provider de date configurat pentru metricile de generare video"
            )

        data = await self._fetch_from_cache("video_generation_metrics")
        if data:
            return data

        if self.video_metrics_repository:
            data = await self._safe_call_provider(
                self.video_metrics_repository,
                ["get_video_metrics", "fetch_video_metrics", "list_video_metrics"],
                context="video",
            )
            if data:
                return data

        if self.external_api:
            data = await self._safe_call_provider(
                self.external_api,
                ["get_metrics", "fetch_metrics", "video_metrics"],
                context="video external",
            )
            if data:
                return data

        if self.supabase_client:
            data = await self._query_supabase_table(
                client=self.supabase_client, table_name="video_generation_metrics"
            )
            if data:
                return data

        return None


class FinancialCollector(BaseMetricsCollector):
    """Colector pentru date financiare"""

    def __init__(
        self,
        supabase_client: Optional[Any] = None,
        cache: Optional[Any] = None,
        financial_repository: Optional[Any] = None,
        accounting_api: Optional[Any] = None,
    ):
        super().__init__(cache=cache)

        self.supabase_client = supabase_client
        self.financial_repository = financial_repository
        self.accounting_api = accounting_api

    async def collect_financial_metrics(self) -> List[MetricData]:
        """Colectează metrici financiare"""
        metrics = []

        try:
            financial_data = await self._get_financial_metrics_from_dependencies()

            if not financial_data:
                logger.warning("Nu există date financiare disponibile")
                return metrics

            metrics.extend(
                self._build_metrics_from_payload(
                    payload=financial_data,
                    source=DataSource.FINANCIAL,
                    default_description="Financial metric",
                )
            )

            logger.info(f"Colectat {len(metrics)} metrici financiare")

        except Exception as exc:
            logger.error("Eroare la colectarea datelor financiare: %s", exc)
            raise

        return metrics

    async def _get_financial_metrics_from_dependencies(self) -> Optional[Any]:
        if not any([self.supabase_client, self.cache, self.financial_repository, self.accounting_api]):
            raise RuntimeError(
                "Niciun provider de date configurat pentru metricile financiare"
            )

        data = await self._fetch_from_cache("financial_metrics")
        if data:
            return data

        if self.financial_repository:
            data = await self._safe_call_provider(
                self.financial_repository,
                ["get_financial_metrics", "fetch_financial_metrics", "list_financial_metrics"],
                context="financial",
            )
            if data:
                return data

        if self.accounting_api:
            data = await self._safe_call_provider(
                self.accounting_api,
                ["get_metrics", "fetch_metrics", "financial_metrics"],
                context="financial external",
            )
            if data:
                return data

        if self.supabase_client:
            data = await self._query_supabase_table(
                client=self.supabase_client, table_name="financial_metrics"
            )
            if data:
                return data

        return None


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
