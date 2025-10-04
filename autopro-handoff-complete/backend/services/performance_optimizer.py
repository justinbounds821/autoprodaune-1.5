"""
Performance Optimizer - Wrapper compatibil pentru sistemul modular
"""

from .performance import (
    PerformanceOptimizer,
    OptimizationLevel,
    PerformanceMetric,
    OptimizationResult,
    DatabaseOptimizer,
    APIResponseOptimizer,
    AsyncProcessingOptimizer,
    MemoryOptimizer,
    PerformanceAnalyzer
)

# Singleton instance
_performance_optimizer = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """Returnează instanța singleton a PerformanceOptimizer"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer

# Funcții helper pentru optimizarea rapidă
async def optimize_performance(optimization_level: OptimizationLevel = OptimizationLevel.MEDIUM) -> dict:
    """
    Funcție helper pentru optimizarea performanței
    
    Args:
        optimization_level: Nivelul de optimizare
        
    Returns:
        Rezultatul optimizării
    """
    optimizer = get_performance_optimizer()
    return await optimizer.run_comprehensive_optimization(optimization_level)

def analyze_performance_metrics(metrics: list) -> dict:
    """
    Funcție helper pentru analiza performanței
    
    Args:
        metrics: Lista de metrici de analizat
        
    Returns:
        Analiza performanței
    """
    optimizer = get_performance_optimizer()
    return optimizer.analyze_performance(metrics)

def optimize_database_query(query: str, params: dict = None) -> dict:
    """
    Funcție helper pentru optimizarea query-urilor
    
    Args:
        query: Query-ul de optimizat
        params: Parametrii query-ului
        
    Returns:
        Rezultatul optimizării
    """
    optimizer = get_performance_optimizer()
    return optimizer.optimize_database_query(query, params)

__all__ = [
    "PerformanceOptimizer",
    "OptimizationLevel",
    "PerformanceMetric",
    "OptimizationResult",
    "DatabaseOptimizer",
    "APIResponseOptimizer",
    "AsyncProcessingOptimizer",
    "MemoryOptimizer",
    "PerformanceAnalyzer",
    "get_performance_optimizer",
    "optimize_performance",
    "analyze_performance_metrics",
    "optimize_database_query"
]
