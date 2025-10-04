"""
Performance Models - Data structures for performance optimization
"""

from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class OptimizationLevel(Enum):
    """Nivelurile de optimizare"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


@dataclass
class PerformanceMetric:
    """Metrică de performanță"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    optimization_applied: Optional[str] = None


@dataclass
class OptimizationResult:
    """Rezultatul unei optimizări"""
    optimization_type: str
    before_value: float
    after_value: float
    improvement_percentage: float
    timestamp: datetime
    details: Dict[str, Any]
