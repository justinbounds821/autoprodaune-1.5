"""
Monitoring Collectors - Individual metric collectors for system and business metrics
"""

import time
import psutil
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from datetime import datetime

from ..analytics.models import (
    MetricData as AnalyticsMetricData,
    MetricType as AnalyticsMetricType,
    DataSource as AnalyticsDataSource,
)
from .models import Metric, MetricType

if TYPE_CHECKING:
    from ..supabase_client import SupabaseService
    from ..analytics.processor import AnalyticsProcessor

logger = logging.getLogger(__name__)


class SystemMetricsCollector:
    """Colector pentru metrici de sistem"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
    
    def collect_system_metrics(self) -> List[Metric]:
        """Colectează metrici de sistem"""
        metrics = []
        
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.append(Metric(
                name="system_cpu_usage",
                value=cpu_percent,
                metric_type=MetricType.GAUGE,
                labels={"host": "autopro-daune"},
                timestamp=datetime.now(),
                description="CPU usage percentage"
            ))
            
            # Memory Usage
            memory = psutil.virtual_memory()
            metrics.append(Metric(
                name="system_memory_usage",
                value=memory.percent,
                metric_type=MetricType.GAUGE,
                labels={"host": "autopro-daune"},
                timestamp=datetime.now(),
                description="Memory usage percentage"
            ))
            
            # Disk Usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            metrics.append(Metric(
                name="system_disk_usage",
                value=disk_percent,
                metric_type=MetricType.GAUGE,
                labels={"host": "autopro-daune"},
                timestamp=datetime.now(),
                description="Disk usage percentage"
            ))
            
            # Network I/O
            network = psutil.net_io_counters()
            metrics.append(Metric(
                name="system_network_bytes_sent",
                value=network.bytes_sent,
                metric_type=MetricType.COUNTER,
                labels={"host": "autopro-daune"},
                timestamp=datetime.now(),
                description="Network bytes sent"
            ))
            
            metrics.append(Metric(
                name="system_network_bytes_recv",
                value=network.bytes_recv,
                metric_type=MetricType.COUNTER,
                labels={"host": "autopro-daune"},
                timestamp=datetime.now(),
                description="Network bytes received"
            ))
            
            # Process count
            process_count = len(psutil.pids())
            metrics.append(Metric(
                name="system_process_count",
                value=process_count,
                metric_type=MetricType.GAUGE,
                labels={"host": "autopro-daune"},
                timestamp=datetime.now(),
                description="Number of running processes"
            ))
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
        
        return metrics
    
    def collect_application_metrics(self) -> List[Metric]:
        """Colectează metrici de aplicație"""
        metrics = []
        
        try:
            # Uptime
            uptime = time.time() - self.start_time
            metrics.append(Metric(
                name="application_uptime",
                value=uptime,
                metric_type=MetricType.GAUGE,
                labels={"service": "autopro-daune"},
                timestamp=datetime.now(),
                description="Application uptime in seconds"
            ))
            
            # Request count
            metrics.append(Metric(
                name="application_requests_total",
                value=self.request_count,
                metric_type=MetricType.COUNTER,
                labels={"service": "autopro-daune"},
                timestamp=datetime.now(),
                description="Total number of requests"
            ))
            
            # Error count
            metrics.append(Metric(
                name="application_errors_total",
                value=self.error_count,
                metric_type=MetricType.COUNTER,
                labels={"service": "autopro-daune"},
                timestamp=datetime.now(),
                description="Total number of errors"
            ))
            
            # Error rate
            error_rate = (self.error_count / max(self.request_count, 1)) * 100
            metrics.append(Metric(
                name="application_error_rate",
                value=error_rate,
                metric_type=MetricType.GAUGE,
                labels={"service": "autopro-daune"},
                timestamp=datetime.now(),
                description="Error rate percentage"
            ))
            
            # Average response time
            if self.response_times:
                avg_response_time = sum(self.response_times) / len(self.response_times)
                metrics.append(Metric(
                    name="application_response_time_avg",
                    value=avg_response_time,
                    metric_type=MetricType.GAUGE,
                    labels={"service": "autopro-daune"},
                    timestamp=datetime.now(),
                    description="Average response time in seconds"
                ))
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {str(e)}")
        
        return metrics
    
    def record_request(self, response_time: float, is_error: bool = False):
        """Înregistrează o cerere"""
        self.request_count += 1
        self.response_times.append(response_time)
        
        if is_error:
            self.error_count += 1
        
        # Păstrează doar ultimele 1000 de timpi de răspuns
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]


class BusinessMetricsCollector:
    """Colector pentru metrici de business"""

    def __init__(
        self,
        supabase_service: Optional["SupabaseService"] = None,
        analytics_processor: Optional["AnalyticsProcessor"] = None,
    ):
        self.supabase_service = supabase_service
        self.analytics_processor = analytics_processor

    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                # Support timestamps that end with "Z" or include timezone info
                normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
                return datetime.fromisoformat(normalized)
            except ValueError:
                pass
        return datetime.now()

    def _append_metric(
        self,
        metrics: List[Metric],
        *,
        name: str,
        value: Any,
        metric_type: MetricType,
        labels: Dict[str, str],
        timestamp: datetime,
        description: str,
    ) -> None:
        numeric_value = self._to_float(value)
        if numeric_value is None:
            return
        metrics.append(
            Metric(
                name=name,
                value=numeric_value,
                metric_type=metric_type,
                labels=labels,
                timestamp=timestamp,
                description=description,
            )
        )

    def _build_analytics_metric(
        self,
        *,
        name: str,
        value: float,
        timestamp: datetime,
        labels: Dict[str, str],
        source: AnalyticsDataSource,
    ) -> AnalyticsMetricData:
        return AnalyticsMetricData(
            name=name,
            value=value,
            metric_type=AnalyticsMetricType.GAUGE,
            labels=labels,
            timestamp=timestamp,
            source=source,
            description=f"Collected via {source.value} source",
        )
    
    def collect_financial_metrics(self) -> List[Metric]:
        """Colectează metrici financiare"""
        metrics: List[Metric] = []

        if not self.supabase_service:
            logger.warning("Supabase service not configured for financial metrics collection")
            return metrics

        try:
            dashboard = self.supabase_service.financial_dashboard()
        except Exception as exc:
            logger.error("Error collecting financial metrics from Supabase: %s", exc, exc_info=True)
            return metrics

        timestamp = datetime.now()

        self._append_metric(
            metrics,
            name="business_total_revenue",
            value=(dashboard or {}).get("total_revenue"),
            metric_type=MetricType.GAUGE,
            labels={"currency": "EUR", "aggregation": "total"},
            timestamp=timestamp,
            description="Total revenue reported by Supabase dashboard",
        )
        self._append_metric(
            metrics,
            name="business_total_costs",
            value=(dashboard or {}).get("total_costs"),
            metric_type=MetricType.GAUGE,
            labels={"currency": "EUR", "aggregation": "total"},
            timestamp=timestamp,
            description="Total costs reported by Supabase dashboard",
        )
        self._append_metric(
            metrics,
            name="business_net_profit",
            value=(dashboard or {}).get("net_profit"),
            metric_type=MetricType.GAUGE,
            labels={"currency": "EUR", "aggregation": "total"},
            timestamp=timestamp,
            description="Net profit calculated from Supabase dashboard",
        )
        self._append_metric(
            metrics,
            name="business_roi_percentage",
            value=(dashboard or {}).get("roi_percentage"),
            metric_type=MetricType.GAUGE,
            labels={"aggregation": "total"},
            timestamp=timestamp,
            description="ROI percentage calculated from Supabase dashboard",
        )

        recent_revenues = (dashboard or {}).get("recent_revenues") or []
        recent_costs = (dashboard or {}).get("recent_costs") or []

        for index, revenue in enumerate(recent_revenues):
            amount = self._to_float((revenue or {}).get("amount"))
            if amount is None:
                continue
            revenue_timestamp = self._parse_timestamp((revenue or {}).get("timestamp"))
            labels = {
                "entry": str(index),
                "category": "revenue",
                "currency": (revenue or {}).get("currency", "EUR"),
            }
            self._append_metric(
                metrics,
                name="business_recent_revenue_amount",
                value=amount,
                metric_type=MetricType.GAUGE,
                labels=labels,
                timestamp=revenue_timestamp,
                description="Recent revenue entry fetched from Supabase",
            )

        for index, cost in enumerate(recent_costs):
            amount = self._to_float((cost or {}).get("cost"))
            if amount is None:
                continue
            cost_timestamp = self._parse_timestamp((cost or {}).get("timestamp"))
            labels = {
                "entry": str(index),
                "category": "cost",
                "currency": (cost or {}).get("currency", "EUR"),
            }
            self._append_metric(
                metrics,
                name="business_recent_cost_amount",
                value=amount,
                metric_type=MetricType.GAUGE,
                labels=labels,
                timestamp=cost_timestamp,
                description="Recent cost entry fetched from Supabase",
            )

        analytics_metrics: List[AnalyticsMetricData] = []
        for revenue in recent_revenues:
            amount = self._to_float((revenue or {}).get("amount"))
            if amount is None:
                continue
            analytics_metrics.append(
                self._build_analytics_metric(
                    name="recent_revenue",
                    value=amount,
                    timestamp=self._parse_timestamp((revenue or {}).get("timestamp")),
                    labels={"category": "revenue"},
                    source=AnalyticsDataSource.FINANCIAL,
                )
            )

        for cost in recent_costs:
            amount = self._to_float((cost or {}).get("cost"))
            if amount is None:
                continue
            analytics_metrics.append(
                self._build_analytics_metric(
                    name="recent_cost",
                    value=amount,
                    timestamp=self._parse_timestamp((cost or {}).get("timestamp")),
                    labels={"category": "cost"},
                    source=AnalyticsDataSource.FINANCIAL,
                )
            )

        if self.analytics_processor and analytics_metrics:
            try:
                analytics_summary = self.analytics_processor.process_metrics(analytics_metrics)
            except Exception as exc:
                logger.error("Error processing financial analytics metrics: %s", exc, exc_info=True)
            else:
                total_metrics = analytics_summary.get("total_metrics")
                if isinstance(total_metrics, (int, float)):
                    self._append_metric(
                        metrics,
                        name="business_financial_recent_activity_count",
                        value=total_metrics,
                        metric_type=MetricType.GAUGE,
                        labels={"aggregation": "count", "source": "supabase"},
                        timestamp=timestamp,
                        description="Number of recent financial entries processed",
                    )

                financial_totals = (analytics_summary.get("sources") or {}).get(AnalyticsDataSource.FINANCIAL.value, {})
                total_value = financial_totals.get("total_value")
                if isinstance(total_value, (int, float)):
                    self._append_metric(
                        metrics,
                        name="business_financial_recent_activity_total_value",
                        value=total_value,
                        metric_type=MetricType.GAUGE,
                        labels={"aggregation": "sum", "source": "supabase"},
                        timestamp=timestamp,
                        description="Aggregated total value for recent financial entries",
                    )

        return metrics
    
    def collect_social_media_metrics(self) -> List[Metric]:
        """Colectează metrici de social media"""
        metrics: List[Metric] = []

        if not self.supabase_service:
            logger.warning("Supabase service not configured for social media metrics collection")
            return metrics

        try:
            summary = self.supabase_service.social_summary()
        except Exception as exc:
            logger.error("Error collecting social media metrics from Supabase: %s", exc, exc_info=True)
            return metrics

        timestamp = datetime.now()
        analytics_metrics: List[AnalyticsMetricData] = []

        for platform, stats in (summary or {}).items():
            if not isinstance(stats, dict):
                continue

            self._append_metric(
                metrics,
                name="social_media_posts_today",
                value=stats.get("posts_today"),
                metric_type=MetricType.GAUGE,
                labels={"platform": platform, "period": "daily"},
                timestamp=timestamp,
                description="Number of posts published today",
            )
            self._append_metric(
                metrics,
                name="social_media_followers_total",
                value=stats.get("followers") or stats.get("followers_total"),
                metric_type=MetricType.GAUGE,
                labels={"platform": platform},
                timestamp=timestamp,
                description="Total followers per platform",
            )
            self._append_metric(
                metrics,
                name="social_media_engagement_rate",
                value=stats.get("engagement_rate") or stats.get("engagement"),
                metric_type=MetricType.GAUGE,
                labels={"platform": platform},
                timestamp=timestamp,
                description="Engagement rate for the platform",
            )
            self._append_metric(
                metrics,
                name="social_media_revenue_total",
                value=stats.get("revenue"),
                metric_type=MetricType.GAUGE,
                labels={"platform": platform, "currency": stats.get("currency", "EUR")},
                timestamp=timestamp,
                description="Total revenue attributed to the platform",
            )

            if self.analytics_processor:
                for metric_name, key in (
                    ("posts_today", "posts_today"),
                    ("followers", "followers"),
                    ("engagement_rate", "engagement_rate"),
                    ("revenue", "revenue"),
                ):
                    numeric_value = self._to_float(stats.get(key))
                    if numeric_value is None:
                        continue
                    analytics_metrics.append(
                        self._build_analytics_metric(
                            name=f"{platform}_{metric_name}",
                            value=numeric_value,
                            timestamp=timestamp,
                            labels={"platform": platform, "metric": metric_name},
                            source=AnalyticsDataSource.SOCIAL_MEDIA,
                        )
                    )

        if self.analytics_processor and analytics_metrics:
            try:
                social_summary = self.analytics_processor.process_metrics(analytics_metrics)
            except Exception as exc:
                logger.error("Error processing social media analytics metrics: %s", exc, exc_info=True)
            else:
                total_metrics = social_summary.get("total_metrics")
                if isinstance(total_metrics, (int, float)):
                    self._append_metric(
                        metrics,
                        name="social_media_metrics_count",
                        value=total_metrics,
                        metric_type=MetricType.GAUGE,
                        labels={"aggregation": "count", "source": "supabase"},
                        timestamp=timestamp,
                        description="Number of social media metrics processed",
                    )

                social_totals = (social_summary.get("sources") or {}).get(AnalyticsDataSource.SOCIAL_MEDIA.value, {})
                total_value = social_totals.get("total_value")
                if isinstance(total_value, (int, float)):
                    self._append_metric(
                        metrics,
                        name="social_media_metrics_total_value",
                        value=total_value,
                        metric_type=MetricType.GAUGE,
                        labels={"aggregation": "sum", "source": "supabase"},
                        timestamp=timestamp,
                        description="Aggregated total value for social media metrics",
                    )

        return metrics
    
    def collect_video_generation_metrics(self) -> List[Metric]:
        """Colectează metrici de generare video"""
        metrics = []
        
        try:
            # Simulează colectarea metricilor de generare video
            metrics.extend([
                Metric(
                    name="video_generation_jobs_total",
                    value=15,
                    metric_type=MetricType.GAUGE,
                    labels={"period": "daily"},
                    timestamp=datetime.now(),
                    description="Total video generation jobs"
                ),
                Metric(
                    name="video_generation_success_rate",
                    value=95.6,
                    metric_type=MetricType.GAUGE,
                    labels={"period": "daily"},
                    timestamp=datetime.now(),
                    description="Video generation success rate"
                ),
                Metric(
                    name="video_generation_avg_duration",
                    value=45.2,
                    metric_type=MetricType.GAUGE,
                    labels={"period": "daily"},
                    timestamp=datetime.now(),
                    description="Average video generation duration"
                ),
                Metric(
                    name="video_generation_total_cost",
                    value=125.50,
                    metric_type=MetricType.GAUGE,
                    labels={"currency": "USD", "period": "daily"},
                    timestamp=datetime.now(),
                    description="Total video generation cost"
                )
            ])
            
        except Exception as e:
            logger.error(f"Error collecting video generation metrics: {str(e)}")
        
        return metrics
