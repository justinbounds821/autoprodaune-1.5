"""
Video CDN Router - CDN management and cache control
Provides endpoints for CDN URLs, cache purging, delivery stats
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
import logging

from ..services.cdn_manager import get_cdn_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/video/cdn", tags=["Video CDN"])


@router.get("/info")
async def get_cdn_info():
    """Get CDN configuration and status"""
    cdn = get_cdn_manager()
    
    return {
        "cdn_manager": cdn.get_health(),
        "storage_service": {
            "type": "cloudflare_r2",
            "configured": bool(cdn.cdn_domain)
        }
    }


@router.get("/url/{job_id}")
async def get_job_cdn_url(job_id: str, signed: bool = False, ttl_seconds: Optional[int] = None):
    """
    Get CDN URL for job output video.
    Optionally generate signed URL with expiration.
    """
    try:
        from ..services.supabase_client import get_supabase
        supabase = get_supabase()
        
        # Verify job exists
        job_response = supabase.table("video_jobs").select("output_url").eq("id", job_id).execute()
        
        if not job_response.data:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        cdn = get_cdn_manager()
        
        url_data = await cdn.get_cdn_url(
            job_id=job_id,
            signed=signed,
            ttl_seconds=ttl_seconds
        )
        
        return url_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CDN URL for {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get CDN URL: {str(e)}")


@router.post("/purge/{job_id}")
async def purge_job_cache(job_id: str):
    """
    Purge CDN cache for specific job.
    Forces CDN to fetch fresh content on next request.
    """
    try:
        cdn = get_cdn_manager()
        
        if not cdn.enabled:
            raise HTTPException(status_code=503, detail="CDN caching not enabled")
        
        result = await cdn.purge_cache(job_id)
        
        if not result.get("purged"):
            raise HTTPException(
                status_code=500,
                detail=f"Cache purge failed: {result.get('reason', 'unknown')}"
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error purging cache for {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Cache purge failed: {str(e)}")


@router.get("/stats")
async def get_cdn_stats():
    """Get CDN usage statistics"""
    try:
        cdn = get_cdn_manager()
        
        if not cdn.enabled:
            return {"enabled": False, "message": "CDN not configured"}
        
        stats = await cdn.get_cache_stats()
        return stats
    
    except Exception as e:
        logger.error(f"Error getting CDN stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
