"""
Performance Optimizers - Individual optimization components
"""

import time
import asyncio
import json
import logging
import psutil
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from cachetools import TTLCache
from .models import OptimizationResult

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """Optimizator pentru baza de date"""
    
    def __init__(self):
        self.query_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minute cache
        self.slow_queries = []
        self.query_stats = {}
    
    async def optimize_query(self, query: str, params: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
        """Optimizează o interogare SQL"""
        start_time = time.time()
        
        try:
            # Verifică cache-ul
            cache_key = f"{query}_{hash(str(params)) if params else 'no_params'}"
            if cache_key in self.query_cache:
                logger.info(f"Query served from cache: {query[:50]}...")
                return {
                    "result": self.query_cache[cache_key],
                    "execution_time": 0.001,
                    "from_cache": True,
                    "optimization": "cache_hit"
                }
            
            # Simulează execuția query-ului
            await asyncio.sleep(0.01)  # Simulează timpul de execuție
            
            # Simulează rezultatul
            result = {"data": "simulated_query_result", "count": 150}
            
            # Adaugă în cache
            self.query_cache[cache_key] = result
            
            execution_time = time.time() - start_time
            
            # Înregistrează statistici
            self._record_query_stats(query, execution_time)
            
            # Verifică dacă query-ul este lent
            if execution_time > 0.1:  # 100ms threshold
                self.slow_queries.append({
                    "query": query,
                    "execution_time": execution_time,
                    "timestamp": datetime.now()
                })
            
            return {
                "result": result,
                "execution_time": execution_time,
                "from_cache": False,
                "optimization": "query_optimized"
            }
            
        except Exception as e:
            logger.error(f"Error optimizing query: {str(e)}")
            return {
                "error": str(e),
                "execution_time": time.time() - start_time,
                "from_cache": False,
                "optimization": "error"
            }
    
    def _record_query_stats(self, query: str, execution_time: float):
        """Înregistrează statisticile query-ului"""
        query_type = self._get_query_type(query)
        
        if query_type not in self.query_stats:
            self.query_stats[query_type] = {
                "count": 0,
                "total_time": 0,
                "avg_time": 0,
                "max_time": 0
            }
        
        stats = self.query_stats[query_type]
        stats["count"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["count"]
        stats["max_time"] = max(stats["max_time"], execution_time)
    
    def _get_query_type(self, query: str) -> str:
        """Determină tipul query-ului"""
        query_lower = query.lower().strip()
        if query_lower.startswith('select'):
            return 'SELECT'
        elif query_lower.startswith('insert'):
            return 'INSERT'
        elif query_lower.startswith('update'):
            return 'UPDATE'
        elif query_lower.startswith('delete'):
            return 'DELETE'
        else:
            return 'OTHER'
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Returnează recomandări de optimizare pentru baza de date"""
        recommendations = []
        
        # Analizează query-urile lente
        if self.slow_queries:
            slow_count = len(self.slow_queries)
            avg_slow_time = sum(q["execution_time"] for q in self.slow_queries) / slow_count
            
            recommendations.append({
                "type": "slow_queries",
                "priority": "high",
                "title": "Optimizează Query-urile Lente",
                "description": f"Găsite {slow_count} query-uri lente cu timpul mediu de {avg_slow_time:.3f}s",
                "suggestions": [
                    "Adaugă index-uri pe coloanele folosite în WHERE și ORDER BY",
                    "Optimizează JOIN-urile complexe",
                    "Folosește EXPLAIN ANALYZE pentru a analiza planul de execuție",
                    "Consideră denormalizarea pentru query-uri foarte frecvente"
                ]
            })
        
        # Analizează statisticile query-urilor
        for query_type, stats in self.query_stats.items():
            if stats["avg_time"] > 0.05:  # 50ms threshold
                recommendations.append({
                    "type": f"{query_type.lower()}_optimization",
                    "priority": "medium",
                    "title": f"Optimizează Query-urile {query_type}",
                    "description": f"Query-urile {query_type} au timpul mediu de {stats['avg_time']:.3f}s",
                    "suggestions": [
                        f"Adaugă index-uri specifice pentru query-urile {query_type}",
                        "Optimizează structura tabelelor",
                        "Consideră partiționarea pentru tabele mari"
                    ]
                })
        
        return recommendations


class APIResponseOptimizer:
    """Optimizator pentru răspunsurile API"""
    
    def __init__(self):
        self.response_cache = TTLCache(maxsize=500, ttl=600)  # 10 minute cache
        self.response_times = []
        self.compression_stats = {
            "compressed_responses": 0,
            "total_size_before": 0,
            "total_size_after": 0
        }
    
    async def optimize_response(self, data: Any, endpoint: str, 
                              enable_cache: bool = True, 
                              enable_compression: bool = True) -> Dict[str, Any]:
        """Optimizează un răspuns API"""
        start_time = time.time()
        
        try:
            # Serializează datele
            if isinstance(data, dict):
                serialized_data = json.dumps(data, default=str)
            else:
                serialized_data = str(data)
            
            original_size = len(serialized_data.encode('utf-8'))
            
            # Verifică cache-ul
            cache_key = f"{endpoint}_{hash(serialized_data)}"
            if enable_cache and cache_key in self.response_cache:
                logger.info(f"Response served from cache for endpoint: {endpoint}")
                return {
                    "data": self.response_cache[cache_key],
                    "processing_time": time.time() - start_time,
                    "from_cache": True,
                    "size": original_size,
                    "compressed": False,
                    "optimization": "cache_hit"
                }
            
            # Simulează compresia
            compressed_data = data
            compressed_size = original_size
            if enable_compression and original_size > 1024:  # 1KB threshold
                # Simulează compresia (în realitate ar folosi gzip)
                compressed_size = int(original_size * 0.7)  # 30% reduction
                self.compression_stats["compressed_responses"] += 1
                self.compression_stats["total_size_before"] += original_size
                self.compression_stats["total_size_after"] += compressed_size
            
            # Adaugă în cache
            if enable_cache:
                self.response_cache[cache_key] = data
            
            processing_time = time.time() - start_time
            self.response_times.append(processing_time)
            
            # Păstrează doar ultimele 1000 de timpi
            if len(self.response_times) > 1000:
                self.response_times = self.response_times[-1000:]
            
            return {
                "data": compressed_data,
                "processing_time": processing_time,
                "from_cache": False,
                "size": compressed_size,
                "compressed": compressed_size < original_size,
                "compression_ratio": (original_size - compressed_size) / original_size * 100 if original_size > 0 else 0,
                "optimization": "response_optimized"
            }
            
        except Exception as e:
            logger.error(f"Error optimizing response: {str(e)}")
            return {
                "error": str(e),
                "processing_time": time.time() - start_time,
                "from_cache": False,
                "size": 0,
                "compressed": False,
                "optimization": "error"
            }
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Returnează statisticile de compresie"""
        if self.compression_stats["compressed_responses"] > 0:
            avg_compression = (
                (self.compression_stats["total_size_before"] - self.compression_stats["total_size_after"]) /
                self.compression_stats["total_size_before"] * 100
            )
        else:
            avg_compression = 0
        
        return {
            "compressed_responses": self.compression_stats["compressed_responses"],
            "avg_compression_ratio": avg_compression,
            "total_bytes_saved": (
                self.compression_stats["total_size_before"] - self.compression_stats["total_size_after"]
            ),
            "avg_response_time": sum(self.response_times) / len(self.response_times) if self.response_times else 0
        }


class AsyncProcessingOptimizer:
    """Optimizator pentru procesarea asincronă"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.task_queue: asyncio.Queue[Any] = asyncio.Queue()
        self.active_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.task_stats = {}
    
    async def execute_concurrent_tasks(self, tasks: List[Callable], 
                                     max_concurrent: int = None) -> List[Any]:
        """Execută task-uri în paralel"""
        if max_concurrent is None:
            max_concurrent = self.max_workers
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(task):
            async with semaphore:
                return await self._execute_task(task)
        
        # Execută task-urile în paralel
        results = await asyncio.gather(
            *[execute_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )
        
        return results
    
    async def _execute_task(self, task: Callable) -> Any:
        """Execută un task individual"""
        start_time = time.time()
        task_name = task.__name__ if hasattr(task, '__name__') else 'anonymous_task'
        
        try:
            self.active_tasks += 1
            
            # Execută task-ul
            if asyncio.iscoroutinefunction(task):
                result = await task()
            else:
                # Execută în thread pool pentru task-uri sincrone
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(self.thread_pool, task)
            
            self.completed_tasks += 1
            execution_time = time.time() - start_time
            
            # Înregistrează statistici
            self._record_task_stats(task_name, execution_time, True)
            
            return result
            
        except Exception as e:
            self.failed_tasks += 1
            execution_time = time.time() - start_time
            
            # Înregistrează statistici
            self._record_task_stats(task_name, execution_time, False)
            
            logger.error(f"Task {task_name} failed: {str(e)}")
            raise
            
        finally:
            self.active_tasks -= 1
    
    def _record_task_stats(self, task_name: str, execution_time: float, success: bool):
        """Înregistrează statisticile task-ului"""
        if task_name not in self.task_stats:
            self.task_stats[task_name] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "total_time": 0,
                "avg_time": 0,
                "max_time": 0,
                "min_time": float('inf')
            }
        
        stats = self.task_stats[task_name]
        stats["total_executions"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["total_executions"]
        stats["max_time"] = max(stats["max_time"], execution_time)
        stats["min_time"] = min(stats["min_time"], execution_time)
        
        if success:
            stats["successful_executions"] += 1
        else:
            stats["failed_executions"] += 1
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Returnează statisticile task-urilor"""
        return {
            "active_tasks": self.active_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "task_stats": self.task_stats
        }


class MemoryOptimizer:
    """Optimizator pentru gestionarea memoriei"""
    
    def __init__(self):
        self.memory_usage_history = []
        self.gc_threshold = 80  # 80% memory usage threshold
        self.optimization_history = []
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Returnează utilizarea memoriei"""
        try:
            memory = psutil.virtual_memory()
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                "system_memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "percentage": memory.percent
                },
                "process_memory": {
                    "rss": process_memory.rss,  # Resident Set Size
                    "vms": process_memory.vms,  # Virtual Memory Size
                    "percentage": (process_memory.rss / memory.total) * 100
                },
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Error getting memory usage: {str(e)}")
            return {"error": str(e)}
    
    def optimize_memory(self, force_gc: bool = False) -> Dict[str, Any]:
        """Optimizează utilizarea memoriei"""
        start_time = time.time()
        
        try:
            memory_before = self.get_memory_usage()
            
            optimizations_applied = []
            
            # Verifică dacă este nevoie de garbage collection
            if force_gc or memory_before.get("system_memory", {}).get("percentage", 0) > self.gc_threshold:
                import gc
                gc.collect()
                optimizations_applied.append("garbage_collection")
            
            # Simulează alte optimizări de memorie
            if memory_before.get("system_memory", {}).get("percentage", 0) > 70:
                # Simulează eliberarea de cache-uri
                optimizations_applied.append("cache_cleanup")
            
            if memory_before.get("system_memory", {}).get("percentage", 0) > 85:
                # Simulează optimizarea structurilor de date
                optimizations_applied.append("data_structure_optimization")
            
            memory_after = self.get_memory_usage()
            
            optimization_time = time.time() - start_time
            
            # Calculează îmbunătățirea
            memory_saved = (
                memory_before.get("system_memory", {}).get("used", 0) -
                memory_after.get("system_memory", {}).get("used", 0)
            )
            
            optimization_result = OptimizationResult(
                optimization_type="memory_optimization",
                before_value=memory_before.get("system_memory", {}).get("percentage", 0),
                after_value=memory_after.get("system_memory", {}).get("percentage", 0),
                improvement_percentage=(
                    (memory_before.get("system_memory", {}).get("percentage", 0) -
                     memory_after.get("system_memory", {}).get("percentage", 0))
                    if memory_before.get("system_memory", {}).get("percentage", 0) > 0 else 0
                ),
                timestamp=datetime.now(),
                details={
                    "memory_saved_bytes": memory_saved,
                    "optimizations_applied": optimizations_applied,
                    "optimization_time": optimization_time
                }
            )
            
            self.optimization_history.append(optimization_result)
            
            # Păstrează doar ultimele 100 de optimizări
            if len(self.optimization_history) > 100:
                self.optimization_history = self.optimization_history[-100:]
            
            return {
                "memory_before": memory_before,
                "memory_after": memory_after,
                "memory_saved": memory_saved,
                "optimizations_applied": optimizations_applied,
                "optimization_time": optimization_time,
                "improvement_percentage": optimization_result.improvement_percentage
            }
            
        except Exception as e:
            logger.error(f"Error optimizing memory: {str(e)}")
            return {"error": str(e)}
    
    def get_memory_recommendations(self) -> List[Dict[str, Any]]:
        """Returnează recomandări pentru optimizarea memoriei"""
        recommendations = []
        memory_usage = self.get_memory_usage()
        
        system_percentage = memory_usage.get("system_memory", {}).get("percentage", 0)
        process_percentage = memory_usage.get("process_memory", {}).get("percentage", 0)
        
        if system_percentage > 90:
            recommendations.append({
                "type": "critical_memory",
                "priority": "critical",
                "title": "Utilizare Critică a Memoriei",
                "description": f"Sistemul folosește {system_percentage:.1f}% din memorie",
                "suggestions": [
                    "Rulează garbage collection forțat",
                    "Eliberează cache-uri nefolosite",
                    "Consideră restartarea serviciului",
                    "Monitorizează memory leaks"
                ]
            })
        elif system_percentage > 80:
            recommendations.append({
                "type": "high_memory",
                "priority": "high",
                "title": "Utilizare Ridicată a Memoriei",
                "description": f"Sistemul folosește {system_percentage:.1f}% din memorie",
                "suggestions": [
                    "Optimizează cache-urile",
                    "Reduce dimensiunea buffer-elor",
                    "Implementează memory pooling"
                ]
            })
        
        if process_percentage > 50:
            recommendations.append({
                "type": "high_process_memory",
                "priority": "medium",
                "title": "Utilizare Ridicată a Memoriei de Proces",
                "description": f"Procesul folosește {process_percentage:.1f}% din memoria sistemului",
                "suggestions": [
                    "Analizează memory leaks în cod",
                    "Optimizează structurile de date",
                    "Consideră streaming pentru fișiere mari"
                ]
            })
        
        return recommendations
