"""
Performance Service - Main orchestrator for performance optimization
"""

import time
import logging
from typing import Dict, Any, List
from datetime import datetime
from .models import OptimizationLevel, PerformanceMetric, OptimizationResult
from .optimizers import (
    DatabaseOptimizer,
    APIResponseOptimizer,
    AsyncProcessingOptimizer,
    MemoryOptimizer
)
from .analyzer import PerformanceAnalyzer

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """Optimizator principal de performanță"""
    
    def __init__(self):
        self.db_optimizer = DatabaseOptimizer()
        self.api_optimizer = APIResponseOptimizer()
        self.async_optimizer = AsyncProcessingOptimizer()
        self.memory_optimizer = MemoryOptimizer()
        self.analyzer = PerformanceAnalyzer()
        self.optimization_history = []
        
    async def run_comprehensive_optimization(self, level: OptimizationLevel = OptimizationLevel.MEDIUM) -> Dict[str, Any]:
        """Rulează optimizarea completă a sistemului"""
        start_time = time.time()
        results = {}
        
        try:
            # 1. Optimizare bază de date
            db_recommendations = self.db_optimizer.get_optimization_recommendations()
            results["database"] = {
                "recommendations": db_recommendations,
                "optimization_level": level.value
            }
            
            # 2. Optimizare API responses
            compression_stats = self.api_optimizer.get_compression_stats()
            results["api"] = {
                "compression_stats": compression_stats,
                "optimization_level": level.value
            }
            
            # 3. Optimizare procesare asincronă
            task_stats = self.async_optimizer.get_task_stats()
            results["async_processing"] = {
                "task_stats": task_stats,
                "optimization_level": level.value
            }
            
            # 4. Optimizare memorie
            memory_optimization = self.memory_optimizer.optimize_memory(
                force_gc=(level == OptimizationLevel.HIGH or level == OptimizationLevel.MAXIMUM)
            )
            results["memory"] = memory_optimization
            
            # 5. Recomandări generale
            general_recommendations = self._generate_general_recommendations(level)
            results["general"] = {
                "recommendations": general_recommendations,
                "optimization_level": level.value
            }
            
            total_time = time.time() - start_time
            
            # Salvează rezultatul
            optimization_result = {
                "timestamp": datetime.now(),
                "level": level.value,
                "total_time": total_time,
                "results": results
            }
            
            self.optimization_history.append(optimization_result)
            
            # Păstrează doar ultimele 50 de optimizări
            if len(self.optimization_history) > 50:
                self.optimization_history = self.optimization_history[-50:]
            
            logger.info(f"Comprehensive optimization completed in {total_time:.2f}s at level {level.value}")
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Error in comprehensive optimization: {str(e)}")
            return {"error": str(e), "timestamp": datetime.now()}
    
    def _generate_general_recommendations(self, level: OptimizationLevel) -> List[Dict[str, Any]]:
        """Generează recomandări generale de optimizare"""
        recommendations = []
        
        if level in [OptimizationLevel.HIGH, OptimizationLevel.MAXIMUM]:
            recommendations.extend([
                {
                    "type": "connection_pooling",
                    "priority": "high",
                    "title": "Implementează Connection Pooling",
                    "description": "Optimizează conexiunile la baza de date cu pooling",
                    "suggestions": [
                        "Configurează pool size optim",
                        "Implementează connection timeout",
                        "Monitorizează pool utilization"
                    ]
                },
                {
                    "type": "caching_strategy",
                    "priority": "high",
                    "title": "Implementează Strategie de Caching",
                    "description": "Adaugă caching la multiple niveluri",
                    "suggestions": [
                        "Redis pentru distributed caching",
                        "Application-level caching",
                        "CDN pentru static assets"
                    ]
                }
            ])
        
        if level == OptimizationLevel.MAXIMUM:
            recommendations.extend([
                {
                    "type": "microservices",
                    "priority": "medium",
                    "title": "Consideră Microservices Architecture",
                    "description": "Împarte aplicația în servicii independente",
                    "suggestions": [
                        "Identifică bounded contexts",
                        "Implementează service discovery",
                        "Configurează load balancing"
                    ]
                },
                {
                    "type": "database_sharding",
                    "priority": "medium",
                    "title": "Consideră Database Sharding",
                    "description": "Împarte baza de date pentru scalabilitate",
                    "suggestions": [
                        "Identifică sharding keys",
                        "Implementează consistent hashing",
                        "Configurează cross-shard queries"
                    ]
                }
            ])
        
        return recommendations
    
    def analyze_performance(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Analizează performanța sistemului"""
        return self.analyzer.analyze_performance(metrics)
    
    def set_performance_baseline(self, metrics: List[PerformanceMetric]):
        """Setează baseline-ul de performanță"""
        self.analyzer.set_baseline(metrics)
    
    def compare_with_baseline(self, current_metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Compară performanța curentă cu baseline-ul"""
        return self.analyzer.compare_with_baseline(current_metrics)
    
    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """Returnează istoricul optimizărilor"""
        return self.optimization_history
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Returnează sumarul optimizărilor"""
        return self.analyzer.get_optimization_summary()
    
    def optimize_database_query(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Optimizează o interogare de bază de date"""
        return self.db_optimizer.optimize_query(query, params)
    
    def optimize_api_response(self, data: Any, endpoint: str, 
                            enable_cache: bool = True, 
                            enable_compression: bool = True) -> Dict[str, Any]:
        """Optimizează un răspuns API"""
        return self.api_optimizer.optimize_response(data, endpoint, enable_cache, enable_compression)
    
    def optimize_memory_usage(self, force_gc: bool = False) -> Dict[str, Any]:
        """Optimizează utilizarea memoriei"""
        return self.memory_optimizer.optimize_memory(force_gc)
    
    def execute_concurrent_tasks(self, tasks: List[Any], max_concurrent: int = None) -> List[Any]:
        """Execută task-uri în paralel"""
        return self.async_optimizer.execute_concurrent_tasks(tasks, max_concurrent)
