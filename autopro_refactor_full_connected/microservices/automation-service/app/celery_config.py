"""
Celery Configuration for Automation Service
"""
import os
from autopro_common.mq import celery_app

# Configure Celery with separate Redis databases
celery_app.conf.update(
    broker_url=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    result_backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1"),
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)
