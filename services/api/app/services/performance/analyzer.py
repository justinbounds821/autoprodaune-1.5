"""
Performance Analyzer - Performance analysis and profiling
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .models import PerformanceMetric, OptimizationResult, OptimizationLevel

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analizor pentru performanța sistemului"""
    
    def __init__(self):
        self.metrics_history = []
        self.optimization_results = []
        self.performance_baseline = {}
    
    def analyze_performance(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Analizează performanța pe baza metricilor"""
        if not metrics:
            return {"error": "No metrics provided"}
        
        analysis = {
            "total_metrics": len(metrics),
            "analysis_timestamp": datetime.now().isoformat(),
            "performance_summary": {},
            "bottlenecks": [],
            "recommendations": []
        }
        
        # Grupează metricile pe tip
        metrics_by_type = {}
        for metric in metrics:
            metric_type = metric.name.split('_')[0]  # Prima parte a numelui
            if metric_type not in metrics_by_type:
                metrics_by_type[metric_type] = []
            metrics_by_type[metric_type].append(metric)
        
        # Analizează fiecare tip de metrică
        for metric_type, type_metrics in metrics_by_type.items():
            values = [m.value for m in type_metrics if isinstance(m.value, (int, float))]
            if values:
                analysis["performance_summary"][metric_type] = {
                    "count": len(values),
                    "avg_value": sum(values) / len(values),
                    "min_value": min(values),
                    "max_value": max(values),
                    "total_value": sum(values)
                }
                
                # Identifică bottleneck-uri
                if metric_type == "response" and max(values) > 2.0:  # 2 secunde
                    analysis["bottlenecks"].append({
                        "type": "slow_response",
                        "severity": "high",
                        "description": f"Response time exceeds 2s: {max(values):.2f}s",
                        "affected_metrics": len([m for m in type_metrics if m.value > 2.0])
                    })
                
                elif metric_type == "memory" and max(values) > 80:  # 80% memory
                    analysis["bottlenecks"].append({
                        "type": "high_memory_usage",
                        "severity": "critical",
                        "description": f"Memory usage exceeds 80%: {max(values):.1f}%",
                        "affected_metrics": len([m for m in type_metrics if m.value > 80])
                    })
        
        # Generează recomandări
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generează recomandări de optimizare"""
        recommendations = []
        
        # Recomandări pentru bottleneck-uri
        for bottleneck in analysis.get("bottlenecks", []):
            if bottleneck["type"] == "slow_response":
                recommendations.append({
                    "type": "response_optimization",
                    "priority": "high",
                    "title": "Optimizează Timpul de Răspuns",
                    "description": bottleneck["description"],
                    "suggestions": [
                        "Implementează caching pentru răspunsuri frecvente",
                        "Optimizează query-urile de bază de date",
                        "Consideră CDN pentru conținut static",
                        "Folosește async processing pentru operațiuni grele"
                    ]
                })
            
            elif bottleneck["type"] == "high_memory_usage":
                recommendations.append({
                    "type": "memory_optimization",
                    "priority": "critical",
                    "title": "Optimizează Utilizarea Memoriei",
                    "description": bottleneck["description"],
                    "suggestions": [
                        "Implementează garbage collection regulat",
                        "Optimizează cache-urile și buffer-ele",
                        "Consideră memory pooling",
                        "Monitorizează memory leaks"
                    ]
                })
        
        # Recomandări generale pe baza metricilor
        performance_summary = analysis.get("performance_summary", {})
        
        if "cpu" in performance_summary and performance_summary["cpu"]["avg_value"] > 70:
            recommendations.append({
                "type": "cpu_optimization",
                "priority": "medium",
                "title": "Optimizează Utilizarea CPU",
                "description": f"CPU usage average: {performance_summary['cpu']['avg_value']:.1f}%",
                "suggestions": [
                    "Optimizează algoritmii computaționali",
                    "Implementează parallel processing",
                    "Consideră load balancing"
                ]
            })
        
        return recommendations
    
    def compare_with_baseline(self, current_metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Compară metricile curente cu baseline-ul"""
        if not self.performance_baseline:
            return {"error": "No baseline available"}
        
        comparison = {
            "comparison_timestamp": datetime.now().isoformat(),
            "improvements": [],
            "degradations": [],
            "overall_trend": "stable"
        }
        
        # Compară fiecare metrică cu baseline-ul
        for metric in current_metrics:
            if metric.name in self.performance_baseline:
                baseline_value = self.performance_baseline[metric.name]
                current_value = metric.value
                
                if isinstance(current_value, (int, float)) and isinstance(baseline_value, (int, float)):
                    change_percentage = ((current_value - baseline_value) / baseline_value) * 100
                    
                    if change_percentage > 10:  # Îmbunătățire semnificativă
                        comparison["improvements"].append({
                            "metric": metric.name,
                            "baseline": baseline_value,
                            "current": current_value,
                            "improvement": change_percentage
                        })
                    elif change_percentage < -10:  # Degradare semnificativă
                        comparison["degradations"].append({
                            "metric": metric.name,
                            "baseline": baseline_value,
                            "current": current_value,
                            "degradation": abs(change_percentage)
                        })
        
        # Determină trend-ul general
        if len(comparison["improvements"]) > len(comparison["degradations"]):
            comparison["overall_trend"] = "improving"
        elif len(comparison["degradations"]) > len(comparison["improvements"]):
            comparison["overall_trend"] = "degrading"
        
        return comparison
    
    def set_baseline(self, metrics: List[PerformanceMetric]):
        """Setează baseline-ul de performanță"""
        self.performance_baseline = {}
        for metric in metrics:
            if isinstance(metric.value, (int, float)):
                self.performance_baseline[metric.name] = metric.value
        
        logger.info(f"Performance baseline set with {len(self.performance_baseline)} metrics")
    
    def track_optimization_result(self, result: OptimizationResult):
        """Urmărește rezultatul unei optimizări"""
        self.optimization_results.append(result)
        
        # Păstrează doar ultimele 100 de rezultate
        if len(self.optimization_results) > 100:
            self.optimization_results = self.optimization_results[-100:]
        
        logger.info(f"Optimization result tracked: {result.optimization_type} - {result.improvement_percentage:.2f}% improvement")
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Returnează sumarul optimizărilor"""
        if not self.optimization_results:
            return {"error": "No optimization results available"}
        
        total_optimizations = len(self.optimization_results)
        avg_improvement = sum(r.improvement_percentage for r in self.optimization_results) / total_optimizations
        
        # Grupează pe tip de optimizare
        by_type = {}
        for result in self.optimization_results:
            if result.optimization_type not in by_type:
                by_type[result.optimization_type] = []
            by_type[result.optimization_type].append(result)
        
        return {
            "total_optimizations": total_optimizations,
            "average_improvement": avg_improvement,
            "optimizations_by_type": {
                opt_type: len(results) for opt_type, results in by_type.items()
            },
            "best_optimization": max(self.optimization_results, key=lambda r: r.improvement_percentage),
            "recent_optimizations": self.optimization_results[-10:]  # Ultimele 10
        }
