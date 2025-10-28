"""
AutoPro Common Library
Shared utilities for all AutoPro microservices
"""

__version__ = "1.0.0"

from .logging import get_logger, setup_logging
from .database import AsyncDatabase, get_db_session
from .cache import RedisCache, get_redis
from .messaging import RabbitMQProducer, RabbitMQConsumer, get_mq_connection
from .monitoring import PrometheusMetrics, setup_metrics
from .health import HealthCheck, create_health_router

__all__ = [
    "get_logger",
    "setup_logging",
    "AsyncDatabase",
    "get_db_session",
    "RedisCache",
    "get_redis",
    "RabbitMQProducer",
    "RabbitMQConsumer",
    "get_mq_connection",
    "PrometheusMetrics",
    "setup_metrics",
    "HealthCheck",
    "create_health_router",
]
