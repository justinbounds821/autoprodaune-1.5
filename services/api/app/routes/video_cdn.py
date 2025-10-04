# services/api/app/routes/video_cdn.py
"""
Video CDN routes for CDN operations and enhanced features.
SRP: CDN API routing only, delegates to services.
"""
import os
import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/video", tags=["video-cdn"])

@router.get("/jobs")
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by job status"),
    limit: int = Query(50, description="Maximum number of jobs to return", ge=1, le=100),
    offset: int = Query(0, description="Offset for pagination", ge=0)
):
    """
    List video jobs with enhanced information.

    Query Parameters:
    - status: Filter by job status (optional)
    - limit: Maximum jobs to return (default: 50, max: 100)
    - offset: Pagination offset (default: 0)

    Returns:
        List of jobs with metadata
    """
    try:
        from ..services.job_repo_supabase import get_job_repo

        repo = get_job_repo()

        if not repo.enabled:
            raise HTTPException(status_code=503, detail="Job repository not available")

        # Get recent jobs from Supabase
        jobs = repo.get_recent_jobs(limit=limit)

        # Filter by status if provided
        if status:
            jobs = [job for job in jobs if job.get("status") == status]

        # Apply pagination
        total_jobs = len(jobs)
        start_idx = min(offset, total_jobs)
        end_idx = min(start_idx + limit, total_jobs)
        paginated_jobs = jobs[start_idx:end_idx]

        # Enhance job data with additional information
        enhanced_jobs = []
        for job in paginated_jobs:
            enhanced_job = dict(job)

            # Add thumbnail URL if available
            if job.get("thumb_url"):
                enhanced_job["thumbnail_url"] = job["thumb_url"]

            # Add metadata if available
            if job.get("meta"):
                enhanced_job["metadata"] = job["meta"]

            enhanced_jobs.append(enhanced_job)

        return {
            "jobs": enhanced_jobs,
            "total": total_jobs,
            "limit": limit,
            "offset": offset,
            "has_more": end_idx < total_jobs
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")

@router.post("/cdn/purge/{job_id}")
async def purge_cdn_job(job_id: str):
    """
    Purge all CDN objects related to a job.

    Args:
        job_id: Job identifier

    Returns:
        Purge operation results
    """
    try:
        from ..services.cdn_manager import get_cdn_manager

        cdn_manager = get_cdn_manager()

        if not cdn_manager.r2_client:
            raise HTTPException(status_code=503, detail="CDN manager not available")

        # Purge related objects
        purged_count = cdn_manager.purge_related_objects(job_id)

        # Also purge from storage service if different
        from ..services.storage_service import get_storage_service
        storage = get_storage_service()

        storage_purged = False
        if hasattr(storage, 'purge_cdn_object'):
            # Try to purge main video file
            video_key = f"videos/{job_id}.mp4"  # Simplified key pattern
            storage_purged = storage.purge_cdn_object(video_key)

        return {
            "job_id": job_id,
            "purged_objects": purged_count,
            "storage_purged": storage_purged,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to purge CDN for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to purge CDN: {str(e)}")

@router.get("/billing/export")
async def export_billing(
    month: str = Query(..., description="Month in YYYY-MM format", regex=r"^\d{4}-\d{2}$")
):
    """
    Export billing data for a specific month.

    Query Parameters:
    - month: Month in YYYY-MM format (e.g., "2025-01")

    Returns:
        Export results with file URL
    """
    try:
        from ..services.billing_export import get_billing_export_service

        export_service = get_billing_export_service()
        result = await export_service.export_monthly_billing(month)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export billing for month {month}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export billing: {str(e)}")

@router.get("/billing/exports")
async def list_billing_exports():
    """
    List all available billing exports.

    Returns:
        List of billing export records
    """
    try:
        from ..services.billing_export import get_billing_export_service

        export_service = get_billing_export_service()
        exports = export_service.list_available_exports()

        return {
            "exports": exports,
            "total": len(exports)
        }

    except Exception as e:
        logger.error(f"Failed to list billing exports: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list billing exports: {str(e)}")

@router.get("/cdn/info")
async def get_cdn_info():
    """
    Get CDN configuration and status information.

    Returns:
        CDN configuration and operational status
    """
    try:
        from ..services.cdn_manager import get_cdn_manager
        from ..services.storage_service import get_storage_service

        cdn_manager = get_cdn_manager()
        storage_service = get_storage_service()

        return {
            "cdn_manager": cdn_manager.get_cdn_info(),
            "storage_service": storage_service.get_storage_info(),
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get CDN info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get CDN info: {str(e)}")

@router.get("/jobs/{job_id}/cdn-url")
async def get_job_cdn_url(job_id: str):
    """
    Get CDN URL for a specific job.

    Args:
        job_id: Job identifier

    Returns:
        CDN URL information
    """
    try:
        from ..services.storage_service import get_storage_service

        storage = get_storage_service()
        cdn_url = storage.get_video_url(job_id)

        if not cdn_url:
            raise HTTPException(status_code=404, detail="Job or CDN URL not found")

        return {
            "job_id": job_id,
            "cdn_url": cdn_url,
            "is_signed": storage.sign_urls,
            "ttl_seconds": storage.sign_ttl if storage.sign_urls else None,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get CDN URL for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get CDN URL: {str(e)}")

@router.post("/housekeeping/run")
async def run_housekeeping():
    """
    Manually trigger housekeeping cleanup.

    Returns:
        Housekeeping operation results
    """
    try:
        from ..services.housekeeping import get_housekeeping_service

        housekeeping = get_housekeeping_service()
        results = await housekeeping.run_cleanup_cycle()

        return results

    except Exception as e:
        logger.error(f"Failed to run housekeeping: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run housekeeping: {str(e)}")

@router.get("/templates")
async def list_templates():
    """
    List available video templates.

    Returns:
        List of available templates
    """
    try:
        from ..services.template_engine import get_template_engine

        template_engine = get_template_engine()
        templates = template_engine.list_available_templates()

        return {
            "templates": templates,
            "total": len(templates)
        }

    except Exception as e:
        logger.error(f"Failed to list templates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {str(e)}")