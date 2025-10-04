# services/api/app/routes/health.py
"""
Enhanced health check routes for production monitoring.
SRP: Health monitoring only, no business logic.
"""
import os
import asyncio
import platform
import psutil
import logging
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "ok",
        "service": "autopro-video-engine",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": os.getenv("APP_VERSION", "1.0.0")
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """
    Comprehensive health check with dependency status.
    Returns detailed system and service health information.
    """
    health_data = {
        "status": "healthy",
        "service": "autopro-video-engine",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "uptime": _get_uptime_seconds(),
        "dependencies": {},
        "system": _get_system_info(),
        "queue": _get_queue_info()
    }

    # Check database connectivity
    health_data["dependencies"]["database"] = await _check_database_health()

    # Check storage backends
    health_data["dependencies"]["storage"] = _check_storage_health()

    # Check TTS service
    health_data["dependencies"]["tts"] = _check_tts_health()

    # Check video processing backends
    health_data["dependencies"]["video_backends"] = _check_video_backends_health()

    # Check external services
    health_data["dependencies"]["external_services"] = _check_external_services_health()

    # Determine overall health status
    overall_status = "healthy"
    for dep_name, dep_status in health_data["dependencies"].items():
        if dep_status.get("status") == "error":
            overall_status = "degraded"
            break
        elif dep_status.get("status") == "warning" and overall_status == "healthy":
            overall_status = "warning"

    health_data["status"] = overall_status

    return health_data

async def _check_database_health() -> Dict[str, Any]:
    """Check database connectivity and performance."""
    try:
        from ..services.job_repo_supabase import get_job_repo

        repo = get_job_repo()

        if not repo.enabled:
            return {
                "status": "warning",
                "message": "Database disabled",
                "details": "Supabase credentials not configured"
            }

        # Test basic query
        start_time = asyncio.get_event_loop().time()
        recent_jobs = repo.get_recent_jobs(limit=1)
        query_time = asyncio.get_event_loop().time() - start_time

        return {
            "status": "ok",
            "message": "Database connected",
            "query_time_ms": round(query_time * 1000, 2),
            "recent_jobs_count": len(recent_jobs)
        }

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "error",
            "message": f"Database error: {str(e)}"
        }

def _check_storage_health() -> Dict[str, Any]:
    """Check storage backend availability."""
    try:
        from ..services.storage_service import get_storage_service

        storage = get_storage_service()
        info = storage.get_storage_info()

        # Check if storage directory exists and is writable
        if info["storage_type"] == "local":
            storage_path = info.get("local_path")
            if storage_path and os.path.exists(storage_path):
                # Test write permissions
                test_file = os.path.join(storage_path, ".health_check")
                try:
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                    write_ok = True
                except:
                    write_ok = False

                return {
                    "status": "ok" if write_ok else "warning",
                    "message": "Local storage available" if write_ok else "Local storage read-only",
                    "type": "local",
                    "path": storage_path
                }
            else:
                return {
                    "status": "error",
                    "message": "Local storage path not found",
                    "type": "local"
                }
        else:  # R2 storage
            return {
                "status": "ok",
                "message": "R2 storage configured",
                "type": "r2",
                "bucket": info.get("r2_bucket")
            }

    except Exception as e:
        logger.error(f"Storage health check failed: {e}")
        return {
            "status": "error",
            "message": f"Storage error: {str(e)}"
        }

def _check_tts_health() -> Dict[str, Any]:
    """Check TTS service availability."""
    try:
        # Check if ElevenLabs credentials are configured
        api_key = os.getenv("ELEVENLABS_API_KEY")
        voice_id = os.getenv("ELEVENLABS_VOICE_ID")

        if api_key and voice_id:
            return {
                "status": "ok",
                "message": "ElevenLabs TTS configured",
                "provider": "elevenlabs",
                "voice_id": voice_id
            }
        else:
            return {
                "status": "warning",
                "message": "ElevenLabs TTS not configured, using fallback",
                "provider": "local_fallback"
            }

    except Exception as e:
        logger.error(f"TTS health check failed: {e}")
        return {
            "status": "error",
            "message": f"TTS error: {str(e)}"
        }

def _check_video_backends_health() -> Dict[str, Any]:
    """Check video processing backend availability."""
    backends = {}

    try:
        from ..services.lipsync_backend import get_lipsync_backend

        backend = get_lipsync_backend()
        backend_info = backend.get_backend_info()

        backends["lipsync"] = {
            "status": "ok" if backend_info["available"] else "warning",
            "backend": backend_info["backend"],
            "message": f"Lip-sync backend {backend_info['backend']} available" if backend_info["available"] else f"Lip-sync backend {backend_info['backend']} not available"
        }

        # Check FFmpeg availability
        try:
            import subprocess
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True, text=True, timeout=5
            )
            backends["ffmpeg"] = {
                "status": "ok",
                "message": "FFmpeg available",
                "version": result.stderr.split('\n')[0] if result.stderr else "unknown"
            }
        except:
            backends["ffmpeg"] = {
                "status": "error",
                "message": "FFmpeg not available"
            }

    except Exception as e:
        logger.error(f"Video backends health check failed: {e}")
        backends["error"] = {
            "status": "error",
            "message": f"Backend check error: {str(e)}"
        }

    # Overall status
    overall_status = "ok"
    for backend in backends.values():
        if backend.get("status") == "error":
            overall_status = "error"
            break
        elif backend.get("status") == "warning" and overall_status == "ok":
            overall_status = "warning"

    return {
        "status": overall_status,
        "backends": backends
    }

def _check_external_services_health() -> Dict[str, Any]:
    """Check external service dependencies."""
    services = {}

    # Check webhook endpoint if configured
    webhook_url = os.getenv("WEBHOOK_COMPLETED_URL")
    if webhook_url:
        try:
            import httpx
            # Simple HEAD request to check if endpoint is reachable
            response = httpx.head(webhook_url, timeout=5.0)
            services["webhook"] = {
                "status": "ok" if response.status_code < 400 else "warning",
                "message": f"Webhook endpoint reachable (status: {response.status_code})"
            }
        except Exception as e:
            services["webhook"] = {
                "status": "warning",
                "message": f"Webhook endpoint not reachable: {str(e)}"
            }

    # Check Redis if configured
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            import redis
            r = redis.from_url(redis_url)
            r.ping()
            services["redis"] = {
                "status": "ok",
                "message": "Redis connected"
            }
        except Exception as e:
            services["redis"] = {
                "status": "warning",
                "message": f"Redis not available: {str(e)}"
            }

    # Overall status
    overall_status = "ok"
    for service in services.values():
        if service.get("status") == "error":
            overall_status = "error"
            break
        elif service.get("status") == "warning" and overall_status == "ok":
            overall_status = "warning"

    return {
        "status": overall_status,
        "services": services
    }

def _get_system_info() -> Dict[str, Any]:
    """Get system resource information."""
    try:
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count(),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent_used": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "free": psutil.disk_usage('/').free,
                "percent_used": psutil.disk_usage('/').percent
            }
        }
    except Exception as e:
        logger.error(f"System info collection failed: {e}")
        return {"error": str(e)}

def _get_queue_info() -> Dict[str, Any]:
    """Get video processing queue information."""
    try:
        from ..services.job_store import get_queue_stats

        stats = get_queue_stats()
        return {
            "total_jobs": stats["total_jobs"],
            "processing_count": stats["processing_count"],
            "queue_length": stats["queue_length"],
            "concurrency_limit": stats["concurrency_limit"],
            "queue_limit": stats["queue_limit"],
            "status_counts": stats["status_counts"]
        }
    except Exception as e:
        logger.error(f"Queue info collection failed: {e}")
        return {"error": str(e)}

def _get_uptime_seconds() -> float:
    """Get system uptime in seconds."""
    try:
        # Try to get boot time from psutil
        boot_time = psutil.boot_time()
        return time.time() - boot_time
    except:
        # Fallback to process start time
        import psutil
        process = psutil.Process()
        return time.time() - process.create_time()