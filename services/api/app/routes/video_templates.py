# services/api/app/routes/video_templates.py
"""
Video template routes for template library access.
SRP: Template management only, no business logic.
"""
import os
import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/video", tags=["video-templates"])

@router.get("/templates")
async def list_templates():
    """
    List available video templates.

    Returns:
        List of available templates with metadata
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

@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """
    Get specific template configuration.

    Args:
        template_id: Template identifier

    Returns:
        Template configuration
    """
    try:
        from ..services.template_engine import get_template_engine

        template_engine = get_template_engine()
        template = template_engine._load_template(template_id)

        if not template:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")

        return template

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template {template_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get template: {str(e)}")

@router.get("/costs/{job_id}")
async def get_job_costs(job_id: str):
    """
    Get cost breakdown for a specific job.

    Args:
        job_id: Job identifier

    Returns:
        Cost information for the job
    """
    try:
        from ..services.job_repo_supabase import get_job_repo

        repo = get_job_repo()

        if not repo.enabled:
            raise HTTPException(status_code=503, detail="Cost tracking not available")

        # Get job with cost information
        job = repo.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Get cost details from video_costs table
        try:
            from supabase import create_client

            client = create_client(
                os.getenv("SUPABASE_URL", ""),
                os.getenv("SUPABASE_SERVICE_KEY", "")
            )

            result = client.table("video_costs").select("*").eq("job_id", job_id).execute()

            if result.data and len(result.data) > 0:
                cost_data = result.data[0]
                return {
                    "job_id": job_id,
                    "status": job.get("status"),
                    "tts_seconds": cost_data.get("tts_seconds", 0),
                    "processing_seconds": cost_data.get("processing_seconds", 0),
                    "storage_mb": cost_data.get("storage_mb", 0),
                    "amount_cents": cost_data.get("amount_cents", 0),
                    "created_at": cost_data.get("created_at"),
                    "breakdown": {
                        "tts_cost": cost_data.get("tts_seconds", 0) * float(os.getenv("TTS_COST_PER_SECOND", "0.0001")),
                        "processing_cost": cost_data.get("processing_seconds", 0) * float(os.getenv("PROCESSING_COST_PER_SECOND", "0.001")),
                        "storage_cost": cost_data.get("storage_mb", 0) * float(os.getenv("STORAGE_COST_PER_MB", "0.01"))
                    }
                }
            else:
                # No cost data available yet
                return {
                    "job_id": job_id,
                    "status": job.get("status"),
                    "message": "Cost data not available yet"
                }

        except Exception as e:
            logger.error(f"Failed to get costs for job {job_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get costs: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job costs: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting job costs: {str(e)}")

@router.get("/webhooks")
async def list_webhooks(job_id: str = None, limit: int = 20):
    """
    List webhook delivery attempts.

    Args:
        job_id: Optional job ID filter
        limit: Maximum number of webhooks to return

    Returns:
        List of webhook delivery records
    """
    try:
        from ..services.job_repo_supabase import get_job_repo

        repo = get_job_repo()

        if not repo.enabled:
            raise HTTPException(status_code=503, detail="Webhook tracking not available")

        # Get webhooks from Supabase
        try:
            from supabase import create_client

            client = create_client(
                os.getenv("SUPABASE_URL", ""),
                os.getenv("SUPABASE_SERVICE_KEY", "")
            )

            query = client.table("video_webhooks").select("*").order("created_at", desc=True).limit(limit)

            if job_id:
                query = query.eq("job_id", job_id)

            result = query.execute()

            webhooks = []
            for webhook in result.data:
                webhooks.append({
                    "id": webhook.get("id"),
                    "job_id": webhook.get("job_id"),
                    "url": webhook.get("url"),
                    "delivered": webhook.get("delivered", False),
                    "last_error": webhook.get("last_error"),
                    "created_at": webhook.get("created_at"),
                    "updated_at": webhook.get("updated_at")
                })

            return {
                "webhooks": webhooks,
                "total": len(webhooks)
            }

        except Exception as e:
            logger.error(f"Failed to get webhooks: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get webhooks: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting webhooks: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting webhooks: {str(e)}")