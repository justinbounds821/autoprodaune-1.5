"""
Monitoring Service - Serviciu pentru expunerea metricilor custom și monitoring
"""

import logging
import time
import psutil
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json

# Configurează logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class AlertManager:
    """Manager pentru alerte"""
    
    def __init__(self):
        self.alerts = []
        self.alert_rules = {
            "system_cpu_usage": {"warning": 80, "critical": 90},
            "system_memory_usage": {"warning": 85, "critical": 95},
            "system_disk_usage": {"warning": 80, "critical": 90},
            "application_error_rate": {"warning": 5, "critical": 10},
            "application_response_time_avg": {"warning": 2, "critical": 5},
            "business_roi_percentage": {"warning": 50, "critical": 25}
        }
    
    def check_alerts(self, metrics: List[Metric]) -> List[Alert]:
        """Verifică alertele pe baza metricilor"""
        new_alerts = []
        
        for metric in metrics:
            if metric.name in self.alert_rules:
                rules = self.alert_rules[metric.name]
                
                # Verifică alerte critice
                if "critical" in rules and metric.value >= rules["critical"]:
                    alert = Alert(
                        id=f"critical_{metric.name}_{int(time.time())}",
                        name=f"Critical {metric.name}",
                        level=AlertLevel.CRITICAL,
                        message=f"{metric.name} is at critical level: {metric.value}",
                        metric_name=metric.name,
                        threshold=rules["critical"],
                        current_value=metric.value,
                        timestamp=datetime.now()
                    )
                    new_alerts.append(alert)
                
                # Verifică alerte warning
                elif "warning" in rules and metric.value >= rules["warning"]:
                    alert = Alert(
                        id=f"warning_{metric.name}_{int(time.time())}",
                        name=f"Warning {metric.name}",
                        level=AlertLevel.WARNING,
                        message=f"{metric.name} is at warning level: {metric.value}",
                        metric_name=metric.name,
                        threshold=rules["warning"],
                        current_value=metric.value,
                        timestamp=datetime.now()
                    )
                    new_alerts.append(alert)
        
        # Adaugă alertele noi
        self.alerts.extend(new_alerts)
        
        # Păstrează doar ultimele 1000 de alerte
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
        
        return new_alerts
    
    def get_active_alerts(self) -> List[Alert]:
        """Returnează alertele active"""
        return [alert for alert in self.alerts if not alert.resolved]
    
    def resolve_alert(self, alert_id: str):
        """Rezolvă o alertă"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                break

class MonitoringService:
    """Serviciu principal de monitoring"""
    
    def __init__(self):
        self.system_collector = SystemMetricsCollector()
        self.business_collector = BusinessMetricsCollector()
        self.alert_manager = AlertManager()
        self.metrics_history = []
        
    async def collect_all_metrics(self) -> List[Metric]:
        """Colectează toate metricile"""
        all_metrics = []
        
        try:
            # Colectează metrici de sistem
            system_metrics = self.system_collector.collect_system_metrics()
            all_metrics.extend(system_metrics)
            
            # Colectează metrici de aplicație
            app_metrics = self.system_collector.collect_application_metrics()
            all_metrics.extend(app_metrics)
            
            # Colectează metrici de business
            financial_metrics = self.business_collector.collect_financial_metrics()
            all_metrics.extend(financial_metrics)
            
            social_metrics = self.business_collector.collect_social_media_metrics()
            all_metrics.extend(social_metrics)
            
            video_metrics = self.business_collector.collect_video_generation_metrics()
            all_metrics.extend(video_metrics)
            
            # Verifică alertele
            new_alerts = self.alert_manager.check_alerts(all_metrics)
            if new_alerts:
                logger.warning(f"Generated {len(new_alerts)} new alerts")
            
            # Salvează în istoric
            self.metrics_history.append({
                "timestamp": datetime.now(),
                "metrics": all_metrics
            })
            
            # Păstrează doar ultimele 1000 de intrări
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
        
        return all_metrics
    
    def get_system_health(self) -> SystemHealth:
        """Returnează starea sistemului"""
        try:
            # Colectează metrici de sistem
            system_metrics = self.system_collector.collect_system_metrics()
            app_metrics = self.system_collector.collect_application_metrics()
            
            # Extrage valorile
            cpu_usage = next((m.value for m in system_metrics if m.name == "system_cpu_usage"), 0)
            memory_usage = next((m.value for m in system_metrics if m.name == "system_memory_usage"), 0)
            disk_usage = next((m.value for m in system_metrics if m.name == "system_disk_usage"), 0)
            error_rate = next((m.value for m in app_metrics if m.name == "application_error_rate"), 0)
            response_time_avg = next((m.value for m in app_metrics if m.name == "application_response_time_avg"), 0)
            uptime = next((m.value for m in app_metrics if m.name == "application_uptime"), 0)
            
            # Determină statusul sistemului
            if cpu_usage > 90 or memory_usage > 95 or disk_usage > 90 or error_rate > 10:
                status = "unhealthy"
            elif cpu_usage > 80 or memory_usage > 85 or disk_usage > 80 or error_rate > 5:
                status = "degraded"
            else:
                status = "healthy"
            
            return SystemHealth(
                status=status,
                uptime=uptime,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                active_connections=0,  # Placeholder
                error_rate=error_rate,
                response_time_avg=response_time_avg,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}")
            return SystemHealth(
                status="unknown",
                uptime=0,
                cpu_usage=0,
                memory_usage=0,
                disk_usage=0,
                active_connections=0,
                error_rate=0,
                response_time_avg=0,
                timestamp=datetime.now()
            )
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Returnează un sumar al metricilor"""
        try:
            all_metrics = asyncio.run(self.collect_all_metrics())
            
            # Grupează metricile pe tip
            metrics_by_type = {}
            for metric in all_metrics:
                if metric.metric_type.value not in metrics_by_type:
                    metrics_by_type[metric.metric_type.value] = []
                metrics_by_type[metric.metric_type.value].append(metric.name)
            
            # Calculează statistici
            total_metrics = len(all_metrics)
            active_alerts = len(self.alert_manager.get_active_alerts())
            system_health = self.get_system_health()
            
            return {
                "total_metrics": total_metrics,
                "metrics_by_type": metrics_by_type,
                "active_alerts": active_alerts,
                "system_health": asdict(system_health),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting metrics summary: {str(e)}")
            return {"error": str(e)}
    
    def record_request(self, response_time: float, is_error: bool = False):
        """Înregistrează o cerere pentru monitoring"""
        self.system_collector.record_request(response_time, is_error)
    
    def get_prometheus_metrics(self) -> str:
        """Returnează metricile în format Prometheus"""
        try:
            all_metrics = asyncio.run(self.collect_all_metrics())
            
            prometheus_lines = []
            
            for metric in all_metrics:
                # Construiește label-urile
                labels = []
                for key, value in metric.labels.items():
                    labels.append(f'{key}="{value}"')
                
                labels_str = "{" + ",".join(labels) + "}" if labels else ""
                
                # Formatează linia Prometheus
                line = f"{metric.name}{labels_str} {metric.value} {int(metric.timestamp.timestamp() * 1000)}"
                prometheus_lines.append(line)
            
            return "\n".join(prometheus_lines)
            
        except Exception as e:
            logger.error(f"Error generating Prometheus metrics: {str(e)}")
            return f"# Error generating metrics: {str(e)}"

# Singleton instance
_monitoring_service = None

def get_monitoring_service() -> MonitoringService:
    """Returnează instanța singleton a MonitoringService"""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service

# Funcții helper
async def collect_metrics() -> List[Metric]:
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
