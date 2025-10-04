"""
Monitoring Service - Main orchestrator for monitoring operations
"""

import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
from dataclasses import asdict
from .models import Metric, SystemHealth
from .collectors import SystemMetricsCollector, BusinessMetricsCollector
from .alerts import AlertManager

logger = logging.getLogger(__name__)


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
