"""
Video Templates Router - Template management
Provides endpoints for video templates, presets, and configurations
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/video/templates", tags=["Video Templates"])


@router.get("")
async def list_templates(category: Optional[str] = None):
    """Get list of available video templates from database"""
    try:
        from ..services.supabase_client import get_supabase
        supabase = get_supabase()
        
        # Query templates from database
        query = supabase.table("video_templates").select("*").eq("is_active", True)
        
        if category:
            query = query.eq("category", category)
        
        response = query.execute()
        templates = response.data or []
        
        # Get unique categories
        all_categories_response = supabase.table("video_templates").select("category").eq("is_active", True).execute()
        categories = list(set(t["category"] for t in (all_categories_response.data or [])))
        
        return {
            "templates": templates,
            "total": len(templates),
            "categories": categories
        }
    
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {str(e)}")


@router.get("/{template_id}")
async def get_template(template_id: str):
    """Get specific template configuration from database"""
    try:
        from ..services.supabase_client import get_supabase
        supabase = get_supabase()
        
        response = supabase.table("video_templates").select("*").eq("id", template_id).eq("is_active", True).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        
        return response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template {template_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get template: {str(e)}")


@router.post("/{template_id}/preview")
async def generate_template_preview(template_id: str, custom_text: Optional[str] = None):
    """Generate preview of template with custom text"""
    try:
        from ..services.supabase_client import get_supabase
        supabase = get_supabase()
        
        response = supabase.table("video_templates").select("*").eq("id", template_id).eq("is_active", True).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        
        template = response.data[0]
        
        return {
            "template_id": template_id,
            "preview_url": template.get("preview_url"),
            "custom_text": custom_text,
            "status": "preview_ready",
            "template_config": template.get("config", {})
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating preview for {template_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate preview: {str(e)}")


@router.get("/costs/{job_id}")
async def get_job_costs(job_id: str):
    """Get cost breakdown for a specific job"""
    try:
        from ..services.cost_tracker import get_cost_tracker
        
        cost_tracker = get_cost_tracker()
        
        if not cost_tracker.enabled:
            return {
                "enabled": False,
                "message": "Cost tracking not enabled"
            }
        
        cost_data = await cost_tracker.get_job_cost(job_id)
        
        if not cost_data:
            # Return estimated costs
            return {
                "job_id": job_id,
                "estimated": True,
                "tts_seconds": 30,
                "processing_seconds": 45,
                "storage_mb": 50,
                "amount_cents": 150,
                "breakdown": {
                    "tts": {"seconds": 30, "cost_dollars": 0.30},
                    "processing": {"seconds": 45, "cost_dollars": 0.045},
                    "storage": {"megabytes": 50, "cost_dollars": 0.005}
                }
            }
        
        return cost_data
    
    except Exception as e:
        logger.error(f"Error getting costs for {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get costs: {str(e)}")
