"""
Health check utilities for Kubernetes readiness/liveness probes
"""
import time
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Response, status

from .logging import get_logger

logger = get_logger(__name__)


class HealthStatus(str, Enum):
    """Health check status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """Service health checker"""

    def __init__(self, service_name: str):
        """
        Initialize health checker
        
        Args:
            service_name: Name of the microservice
        """
        self.service_name = service_name
        self.start_time = time.time()
        self.checks: Dict[str, Callable] = {}
        self.dependencies: Dict[str, bool] = {}

    def add_check(self, name: str, check_func: Callable[[], bool]) -> None:
        """
        Add a health check function
        
        Args:
            name: Check name (e.g., "database", "redis", "rabbitmq")
            check_func: Function that returns True if healthy, False otherwise
        """
        self.checks[name] = check_func
        logger.info(f"Added health check: {name}")

    async def check_health(self) -> Dict[str, Any]:
        """
        Execute all health checks
        
        Returns:
            Health status dictionary
        """
        results = {}
        all_healthy = True

        # Run all checks
        for name, check_func in self.checks.items():
            try:
                is_healthy = await check_func() if callable(check_func) else check_func()
                results[name] = {
                    "status": HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
                    "healthy": is_healthy,
                }
                if not is_healthy:
                    all_healthy = False
            except Exception as e:
                logger.error(f"Health check '{name}' failed: {e}")
                results[name] = {
                    "status": HealthStatus.UNHEALTHY,
                    "healthy": False,
                    "error": str(e),
                }
                all_healthy = False

        # Overall status
        overall_status = HealthStatus.HEALTHY if all_healthy else HealthStatus.UNHEALTHY
        
        return {
            "service": self.service_name,
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": int(time.time() - self.start_time),
            "checks": results,
        }

    async def is_ready(self) -> bool:
        """
        Check if service is ready to accept traffic (Kubernetes readiness probe)
        
        Returns:
            True if all critical dependencies are healthy
        """
        health = await self.check_health()
        return health["status"] == HealthStatus.HEALTHY

    async def is_alive(self) -> bool:
        """
        Check if service is alive (Kubernetes liveness probe)
        
        Returns:
            True if service process is running
        """
        return True  # If we can execute this, we're alive


def create_health_router(health_check: HealthCheck) -> APIRouter:
    """
    Create FastAPI router with health endpoints
    
    Args:
        health_check: HealthCheck instance
        
    Returns:
        Configured APIRouter
    """
    router = APIRouter(tags=["health"])

    @router.get("/health")
    async def health():
        """Full health check with all dependencies"""
        health_data = await health_check.check_health()
        
        status_code = (
            status.HTTP_200_OK
            if health_data["status"] == HealthStatus.HEALTHY
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        
        return Response(
            content=str(health_data),
            status_code=status_code,
            media_type="application/json",
        )

    @router.get("/health/ready")
    async def readiness():
        """Kubernetes readiness probe"""
        is_ready = await health_check.is_ready()
        
        if is_ready:
            return {"status": "ready"}
        else:
            return Response(
                content='{"status": "not_ready"}',
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                media_type="application/json",
            )

    @router.get("/health/live")
    async def liveness():
        """Kubernetes liveness probe"""
        is_alive = await health_check.is_alive()
        
        if is_alive:
            return {"status": "alive"}
        else:
            return Response(
                content='{"status": "dead"}',
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                media_type="application/json",
            )

    return router


# Global health check instance
_health_instance: Optional[HealthCheck] = None


def init_health_check(service_name: str) -> HealthCheck:
    """
    Initialize global health check
    
    Args:
        service_name: Name of the microservice
        
    Returns:
        HealthCheck instance
    """
    global _health_instance
    _health_instance = HealthCheck(service_name)
    return _health_instance


def get_health_check() -> HealthCheck:
    """
    Get global health check instance
    
    Returns:
        HealthCheck instance
        
    Raises:
        RuntimeError: If health check not initialized
    """
    if _health_instance is None:
        raise RuntimeError("Health check not initialized. Call init_health_check() first.")
    return _health_instance
