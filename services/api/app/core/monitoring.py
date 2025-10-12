"""
Monitoring and logging system for AutoPro Daune.

This module provides comprehensive monitoring, logging, and performance tracking
for the entire AutoPro Daune automation system.
"""

import logging
import time
import functools
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import asyncio
from contextlib import asynccontextmanager
import sys
import traceback

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
from .database import get_database

# Prometheus metrics
REGISTRY = CollectorRegistry()

# API request metrics
API_REQUESTS = Counter(
    'autoprodaune_api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status_code'],
    registry=REGISTRY
)

API_DURATION = Histogram(
    'autoprodaune_api_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    registry=REGISTRY
)

# Business metrics
LEADS_CREATED = Counter(
    'autoprodaune_leads_total',
    'Total number of leads created',
    ['source'],
    registry=REGISTRY
)

POSTS_PUBLISHED = Counter(
    'autoprodaune_posts_total',
    'Total number of social media posts published',
    ['platform', 'template_type'],
    registry=REGISTRY
)

REFERRALS_CREATED = Counter(
    'autoprodaune_referrals_total',
    'Total number of referrals created',
    registry=REGISTRY
)

WHATSAPP_MESSAGES = Counter(
    'autoprodaune_whatsapp_messages_total',
    'Total WhatsApp messages processed',
    ['direction'],
    registry=REGISTRY
)

# System metrics
AUTOMATION_STATUS = Gauge(
    'autoprodaune_automation_active',
    'Whether automation is currently active (1=active, 0=inactive)',
    registry=REGISTRY
)

DAILY_POSTS_COMPLETED = Gauge(
    'autoprodaune_daily_posts_completed',
    'Number of posts completed today',
    registry=REGISTRY
)

ERROR_COUNT = Counter(
    'autoprodaune_errors_total',
    'Total number of errors',
    ['service', 'error_type'],
    registry=REGISTRY
)

# Video engine metrics
VIDEO_BACKEND_AVAILABLE = Gauge(
    'autopro_backend_available',
    'Video backend availability (1=available, 0=unavailable)',
    ['backend'],
    registry=REGISTRY
)

VIDEO_PROCESSING_DURATION = Histogram(
    'autopro_video_processing_duration_seconds',
    'Video processing duration in seconds',
    ['result'],
    registry=REGISTRY
)

VIDEO_SIZE_BYTES = Histogram(
    'autopro_video_size_bytes',
    'Generated video file size in bytes',
    registry=REGISTRY
)

VIDEO_QUEUE_SIZE = Gauge(
    'autopro_queue_size',
    'Number of videos in queue by status',
    ['status'],
    registry=REGISTRY
)

class MonitoringManager:
    """
    Central monitoring and logging manager for AutoPro Daune.
    """

    def __init__(self):
        """Initialize the monitoring manager."""
        # Use existing SupabaseService for logging
        from ..services.supabase_client import get_supabase_service_instance
        self.supabase_service = get_supabase_service_instance()
        self.db = get_database()
        self.logger = self._setup_logging()

        # Performance tracking
        self.performance_data = {}
        self.start_time = time.time()

        # Initialize video metrics with default values
        VIDEO_BACKEND_AVAILABLE.labels(backend='sadtalker').set(0)
        VIDEO_BACKEND_AVAILABLE.labels(backend='heygen').set(0)
        VIDEO_QUEUE_SIZE.labels(status='queued').set(0)
        VIDEO_QUEUE_SIZE.labels(status='processing').set(0)

        self.logger.info("✅ MonitoringManager initialized with SupabaseService integration")

    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging."""
        logger = logging.getLogger('autoprodaune')
        logger.setLevel(logging.INFO)

        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Console handler with JSON-like format
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler for persistent logs (Windows compatible)
        try:
            import os
            logs_dir = os.getenv("LOGS_DIR", "./logs")
            os.makedirs(logs_dir, exist_ok=True)
            log_file = os.path.join(logs_dir, "autoprodaune.log")

            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError) as e:
            logger.warning(f"⚠️ Could not setup file logging: {e}")

        return logger

    async def log_event(
        self,
        level: str,
        category: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        service: str = "api",
        function: str = None
    ):
        """Log an event to both console and database."""
        try:
            # Log to console
            log_method = getattr(self.logger, level.lower(), self.logger.info)
            log_method(f"[{category}] {message}")

            # Log to database
            log_entry = {
                "level": level,
                "category": category,
                "message": message,
                "details": details or {},
                "source_service": service,
                "source_function": function,
                "created_at": datetime.now().isoformat()
            }

            # Run database logging in thread pool to avoid blocking
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(self._log_to_database, log_entry)

        except Exception as e:
            self.logger.error(f"❌ Failed to log event: {e}")

    def _log_to_database(self, log_entry: Dict[str, Any]):
        """Log entry to database using SupabaseService (non-blocking)."""
        try:
            # Use existing SupabaseService app_log method
            self.supabase_service.app_log(
                level=log_entry.get("level", "info"),
                service=log_entry.get("source_service", "api"),
                message=log_entry.get("message", ""),
                meta=log_entry.get("details", {})
            )
        except Exception as e:
            # Don't log database errors to avoid infinite loops
            print(f"Database logging error: {e}")

    def track_api_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Track API request metrics."""
        API_REQUESTS.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        API_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

    def track_lead_creation(self, source: str):
        """Track lead creation."""
        LEADS_CREATED.labels(source=source).inc()

    def track_post_publication(self, platform: str, template_type: str):
        """Track social media post publication."""
        POSTS_PUBLISHED.labels(platform=platform, template_type=template_type).inc()

    def track_referral_creation(self):
        """Track referral creation."""
        REFERRALS_CREATED.inc()

    def track_whatsapp_message(self, direction: str):
        """Track WhatsApp message processing."""
        WHATSAPP_MESSAGES.labels(direction=direction).inc()

    def track_error(self, service: str, error_type: str):
        """Track errors."""
        ERROR_COUNT.labels(service=service, error_type=error_type).inc()

    def update_automation_status(self, is_active: bool):
        """Update automation status metric."""
        AUTOMATION_STATUS.set(1 if is_active else 0)

    def update_daily_posts_count(self, count: int):
        """Update daily posts completed metric."""
        DAILY_POSTS_COMPLETED.set(count)

    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status."""
        try:
            # Database health
            db_healthy = self.db.test_connection()

            # Get recent system stats
            uptime = time.time() - self.start_time

            # Get today's activity
            today = datetime.now().date()
            daily_summary = await self.db.get_daily_summary(today)

            # Posts published today from real DB (fallback-safe)
            posts_today = 0
            try:
                start = datetime.combine(today, datetime.min.time()).isoformat()
                end = datetime.combine(today, datetime.max.time()).isoformat()
                res = self.db.client.table("social_posts").select("status,created_at,posted_at").gte("created_at", start).lte("created_at", end).execute()
                rows = res.data or []
                posts_today = sum(1 for r in rows if (r.get("status") or "").lower() in ("published", "posted"))
                # keep gauge in sync
                DAILY_POSTS_COMPLETED.set(posts_today)
            except Exception:
                # keep previous gauge if query fails
                posts_today = int(DAILY_POSTS_COMPLETED._value._value)

            # Get recent errors
            error_logs = await self._get_recent_errors()

            # API response times
            avg_response_time = self._calculate_avg_response_time()

            # Automation status: prefer gauge (can be updated by scheduler or working_automation)
            automation_running = AUTOMATION_STATUS._value._value > 0
            # Best-effort: sync gauge from scheduler if accessible, but do not override computed return value
            try:
                from ..services.automation_scheduler import get_automation_scheduler  # type: ignore
                status = get_automation_scheduler().get_status()
                # keep gauge consistent if scheduler state is known
                AUTOMATION_STATUS.set(1 if bool(status.get("is_running", False)) else 0)
            except Exception:
                pass

            return {
                "status": "healthy" if db_healthy else "degraded",
                "uptime_seconds": uptime,
                "database_healthy": db_healthy,
                "daily_summary": daily_summary,
                "recent_errors": len(error_logs),
                "avg_response_time_ms": avg_response_time,
                "automation_active": automation_running,
                "posts_today": posts_today,
                "last_check": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"❌ Error getting system health: {e}")
            return {
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }

    async def _get_recent_errors(self, hours: int = 24) -> list:
        """Get recent error logs."""
        try:
            since = (datetime.now() - timedelta(hours=hours)).isoformat()
            result = self.db.client.table("system_logs").select("*").eq("level", "error").gte("created_at", since).execute()
            return result.data or []
        except Exception:
            return []

    def _calculate_avg_response_time(self) -> float:
        """Calculate average API response time."""
        try:
            # Compute average from Histogram samples (_sum / _count)
            metrics = API_DURATION.collect()
            total_sum = 0.0
            total_count = 0.0
            for m in metrics:
                for s in m.samples:
                    # sample names end with _sum or _count
                    if s.name.endswith("_sum"):
                        total_sum += float(s.value)
                    elif s.name.endswith("_count"):
                        total_count += float(s.value)
            if total_count > 0:
                return (total_sum / total_count) * 1000.0  # milliseconds
            return 0.0
        except Exception:
            return 0.0

    async def generate_daily_report(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate comprehensive daily report."""
        try:
            if date is None:
                date = datetime.now().date()

            await self.log_event("info", "reporting", f"Generating daily report for {date}")

            # Get daily summary
            summary = await self.db.get_daily_summary(date)

            # Get social media analytics
            social_analytics = await self.db.get_social_analytics(days=1)

            # Get referral stats
            referral_stats = await self.db.get_referral_stats()

            # Get automation performance
            automation_performance = await self._get_automation_performance(date)

            report = {
                "date": date.isoformat(),
                "summary": summary,
                "social_analytics": social_analytics,
                "referral_stats": referral_stats,
                "automation_performance": automation_performance,
                "generated_at": datetime.now().isoformat()
            }

            await self.log_event("info", "reporting", f"Daily report generated successfully for {date}")

            return report

        except Exception as e:
            await self.log_event("error", "reporting", f"Failed to generate daily report: {e}")
            return {
                "date": date.isoformat() if date else None,
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }

    async def _get_automation_performance(self, date: datetime) -> Dict[str, Any]:
        """Get automation performance for a specific date."""
        try:
            date_start = datetime.combine(date, datetime.min.time()).isoformat()
            date_end = datetime.combine(date, datetime.max.time()).isoformat()

            # Get posts for the day
            result = self.db.client.table("social_posts").select("*").gte("created_at", date_start).lte("created_at", date_end).execute()
            posts = result.data or []

            # Calculate performance metrics
            total_posts = len(posts)
            successful_posts = len([p for p in posts if p.get("status") == "published"])
            failed_posts = total_posts - successful_posts

            # Template distribution
            template_distribution = {}
            for post in posts:
                template = post.get("template_type", "unknown")
                template_distribution[template] = template_distribution.get(template, 0) + 1

            return {
                "total_posts": total_posts,
                "successful_posts": successful_posts,
                "failed_posts": failed_posts,
                "success_rate": (successful_posts / total_posts * 100) if total_posts > 0 else 0,
                "template_distribution": template_distribution
            }

        except Exception as e:
            self.logger.error(f"❌ Error getting automation performance: {e}")
            return {
                "error": str(e)
            }

    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        return generate_latest(REGISTRY).decode('utf-8')

# Decorators for monitoring

def monitor_api_call(endpoint: str):
    """Decorator to monitor API calls."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            method = "POST"  # Default, could be extracted from request
            status_code = 500  # Default error status

            try:
                result = await func(*args, **kwargs)
                status_code = 200
                return result
            except Exception as e:
                get_monitoring().track_error("api", type(e).__name__)
                raise
            finally:
                duration = time.time() - start_time
                get_monitoring().track_api_request(method, endpoint, status_code, duration)

        return wrapper
    return decorator

def monitor_business_operation(operation_type: str):
    """Decorator to monitor business operations."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)

                # Track specific business metrics
                if operation_type == "lead_creation":
                    source = kwargs.get("source", "unknown")
                    get_monitoring().track_lead_creation(source)
                elif operation_type == "referral_creation":
                    get_monitoring().track_referral_creation()
                elif operation_type == "post_publication":
                    platform = kwargs.get("platform", "unknown")
                    template_type = kwargs.get("template_type", "unknown")
                    get_monitoring().track_post_publication(platform, template_type)

                return result
            except Exception as e:
                get_monitoring().track_error(operation_type, type(e).__name__)
                raise

        return wrapper
    return decorator

@asynccontextmanager
async def performance_timer(operation_name: str):
    """Context manager for timing operations."""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        await get_monitoring().log_event(
            "info",
            "performance",
            f"{operation_name} completed in {duration:.3f}s",
            {"duration_seconds": duration}
        )

# Global monitoring instance (lazy initialization)
_monitoring_instance = None

def get_monitoring() -> MonitoringManager:
    """Get the global monitoring instance."""
    global _monitoring_instance
    if _monitoring_instance is None:
        _monitoring_instance = MonitoringManager()
    return _monitoring_instance

# FastAPI dependency
def get_monitoring_manager():
    """FastAPI dependency to get monitoring manager."""
    return get_monitoring()
