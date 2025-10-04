"""
Analytics Processor - Data processing and analysis logic
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from .models import DataSource, MetricType, MetricData, AnalyticsEvent

logger = logging.getLogger(__name__)


class AnalyticsProcessor:
    """Procesează și analizează datele de analytics"""
    
    def __init__(self):
        pass
    
    def process_metrics(self, metrics: List[MetricData]) -> Dict[str, Any]:
        """
        Procesează o listă de metrici și returnează statistici
        
        Args:
            metrics: Lista de metrici de procesat
            
        Returns:
            Dicționar cu statistici procesate
        """
        if not metrics:
            return {"total_metrics": 0, "sources": {}, "types": {}}
        
        # Grupează metricile după sursă
        by_source = {}
        by_type = {}
        
        for metric in metrics:
            source = metric.source.value
            metric_type = metric.metric_type.value
            
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(metric)
            
            if metric_type not in by_type:
                by_type[metric_type] = []
            by_type[metric_type].append(metric)
        
        # Calculează statistici
        total_metrics = len(metrics)
        source_stats = {}
        type_stats = {}
        
        for source, source_metrics in by_source.items():
            values = [m.value for m in source_metrics if isinstance(m.value, (int, float))]
            if values:
                source_stats[source] = {
                    "count": len(source_metrics),
                    "avg_value": sum(values) / len(values),
                    "min_value": min(values),
                    "max_value": max(values),
                    "total_value": sum(values)
                }
        
        for metric_type, type_metrics in by_type.items():
            values = [m.value for m in type_metrics if isinstance(m.value, (int, float))]
            if values:
                type_stats[metric_type] = {
                    "count": len(type_metrics),
                    "avg_value": sum(values) / len(values),
                    "min_value": min(values),
                    "max_value": max(values),
                    "total_value": sum(values)
                }
        
        return {
            "total_metrics": total_metrics,
            "sources": source_stats,
            "types": type_stats,
            "processed_at": datetime.now().isoformat()
        }
    
    def filter_metrics_by_source(self, metrics: List[MetricData], source: DataSource) -> List[MetricData]:
        """Filtrează metricile după sursă"""
        return [m for m in metrics if m.source == source]
    
    def filter_metrics_by_type(self, metrics: List[MetricData], metric_type: MetricType) -> List[MetricData]:
        """Filtrează metricile după tip"""
        return [m for m in metrics if m.metric_type == metric_type]
    
    def filter_metrics_by_time_range(
        self, 
        metrics: List[MetricData], 
        start_time: datetime, 
        end_time: datetime
    ) -> List[MetricData]:
        """Filtrează metricile după interval de timp"""
        return [m for m in metrics if start_time <= m.timestamp <= end_time]
    
    def aggregate_metrics(self, metrics: List[MetricData], group_by: str = "source") -> Dict[str, Any]:
        """
        Agregă metricile după un criteriu
        
        Args:
            metrics: Lista de metrici
            group_by: Criteriul de grupare (source, type, name)
            
        Returns:
            Dicționar cu metricile agregate
        """
        if not metrics:
            return {}
        
        grouped = {}
        
        for metric in metrics:
            if group_by == "source":
                key = metric.source.value
            elif group_by == "type":
                key = metric.metric_type.value
            elif group_by == "name":
                key = metric.name
            else:
                key = "unknown"
            
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(metric)
        
        # Calculează statistici pentru fiecare grup
        aggregated = {}
        for key, group_metrics in grouped.items():
            values = [m.value for m in group_metrics if isinstance(m.value, (int, float))]
            if values:
                aggregated[key] = {
                    "count": len(group_metrics),
                    "avg_value": sum(values) / len(values),
                    "min_value": min(values),
                    "max_value": max(values),
                    "total_value": sum(values),
                    "metrics": group_metrics
                }
        
        return aggregated
    
    def calculate_trends(self, metrics: List[MetricData], metric_name: str) -> Dict[str, Any]:
        """
        Calculează tendințele pentru o metrică specifică
        
        Args:
            metrics: Lista de metrici
            metric_name: Numele metricii pentru care să calculeze tendințele
            
        Returns:
            Dicționar cu informații despre tendințe
        """
        # Filtrează metricile după nume
        filtered_metrics = [m for m in metrics if m.name == metric_name]
        
        if len(filtered_metrics) < 2:
            return {"trend": "insufficient_data", "change": 0}
        
        # Sortează după timestamp
        sorted_metrics = sorted(filtered_metrics, key=lambda x: x.timestamp)
        
        # Calculează tendința
        first_value = sorted_metrics[0].value
        last_value = sorted_metrics[-1].value
        
        if isinstance(first_value, (int, float)) and isinstance(last_value, (int, float)):
            change = last_value - first_value
            change_percentage = (change / first_value * 100) if first_value != 0 else 0
            
            trend = "increasing" if change > 0 else "decreasing" if change < 0 else "stable"
            
            return {
                "trend": trend,
                "change": change,
                "change_percentage": change_percentage,
                "first_value": first_value,
                "last_value": last_value,
                "data_points": len(sorted_metrics)
            }
        
        return {"trend": "invalid_data", "change": 0}
    
    def generate_insights(self, metrics: List[MetricData]) -> List[str]:
        """
        Generează insights pe baza metricilor
        
        Args:
            metrics: Lista de metrici
            
        Returns:
            Lista cu insights generate
        """
        insights = []
        
        if not metrics:
            return ["Nu există date pentru a genera insights"]
        
        # Procesează metricile
        stats = self.process_metrics(metrics)
        
        # Generează insights pe baza statisticilor
        total_metrics = stats.get("total_metrics", 0)
        if total_metrics > 0:
            insights.append(f"Colectat {total_metrics} metrici din {len(stats.get('sources', {}))} surse")
        
        # Insights pentru surse
        sources = stats.get("sources", {})
        for source, source_stats in sources.items():
            count = source_stats.get("count", 0)
            avg_value = source_stats.get("avg_value", 0)
            insights.append(f"{source}: {count} metrici, valoare medie: {avg_value:.2f}")
        
        # Insights pentru tipuri
        types = stats.get("types", {})
        for metric_type, type_stats in types.items():
            count = type_stats.get("count", 0)
            insights.append(f"Tip {metric_type}: {count} metrici")
        
        return insights
