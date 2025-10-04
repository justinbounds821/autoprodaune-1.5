"""
Monitoring Collectors - Individual metric collectors for system and business metrics
"""

import time
import psutil
import logging
from typing import List
from datetime import datetime
from .models import Metric, MetricType

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
    
    def __init__(self):
        pass
    
    def collect_financial_metrics(self) -> List[Metric]:
        """Colectează metrici financiare"""
        metrics = []
        
        try:
            # Simulează colectarea metricilor financiare
            # În implementarea reală, ar citi din baza de date
            
            metrics.extend([
                Metric(
                    name="business_revenue_daily",
                    value=1250.0,
                    metric_type=MetricType.GAUGE,
                    labels={"currency": "RON", "period": "daily"},
                    timestamp=datetime.now(),
                    description="Daily revenue"
                ),
                Metric(
                    name="business_costs_daily",
                    value=450.0,
                    metric_type=MetricType.GAUGE,
                    labels={"currency": "RON", "period": "daily"},
                    timestamp=datetime.now(),
                    description="Daily costs"
                ),
                Metric(
                    name="business_roi_percentage",
                    value=177.8,
                    metric_type=MetricType.GAUGE,
                    labels={"period": "daily"},
                    timestamp=datetime.now(),
                    description="Return on Investment percentage"
                ),
                Metric(
                    name="business_leads_total",
                    value=150,
                    metric_type=MetricType.GAUGE,
                    labels={"period": "daily"},
                    timestamp=datetime.now(),
                    description="Total leads received"
                ),
                Metric(
                    name="business_conversions_total",
                    value=45,
                    metric_type=MetricType.GAUGE,
                    labels={"period": "daily"},
                    timestamp=datetime.now(),
                    description="Total conversions"
                )
            ])
            
        except Exception as e:
            logger.error(f"Error collecting financial metrics: {str(e)}")
        
        return metrics
    
    def collect_social_media_metrics(self) -> List[Metric]:
        """Colectează metrici de social media"""
        metrics = []
        
        try:
            # Simulează colectarea metricilor de social media
            metrics.extend([
                Metric(
                    name="social_media_posts_total",
                    value=25,
                    metric_type=MetricType.GAUGE,
                    labels={"period": "daily"},
                    timestamp=datetime.now(),
                    description="Total social media posts"
                ),
                Metric(
                    name="social_media_views_total",
                    value=45678,
                    metric_type=MetricType.GAUGE,
                    labels={"period": "daily"},
                    timestamp=datetime.now(),
                    description="Total social media views"
                ),
                Metric(
                    name="social_media_engagement_total",
                    value=1234,
                    metric_type=MetricType.GAUGE,
                    labels={"period": "daily"},
                    timestamp=datetime.now(),
                    description="Total social media engagement"
                ),
                Metric(
                    name="social_media_followers_total",
                    value=2500,
                    metric_type=MetricType.GAUGE,
                    labels={"period": "daily"},
                    timestamp=datetime.now(),
                    description="Total social media followers"
                )
            ])
            
        except Exception as e:
            logger.error(f"Error collecting social media metrics: {str(e)}")
        
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
