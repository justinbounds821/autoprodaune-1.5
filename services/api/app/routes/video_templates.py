"""
Video Templates Router - Template management
Provides endpoints for video templates, presets, and configurations
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/video/templates", tags=["Video Templates"])


# Sample templates (in production, would be stored in database)
SAMPLE_TEMPLATES = [
    {
        "id": "template_insurance_claim",
        "name": "Insurance Claim Video",
        "description": "Professional video for insurance claim presentation",
        "category": "insurance",
        "config": {
            "resolution": "1920x1080",
            "fps": 30,
            "format": "mp4",
            "avatar": "professional_male_ro",
            "background": "office",
            "voice": "romanian_male_formal"
        },
        "preview_url": "/assets/templates/insurance_claim_preview.jpg"
    },
    {
        "id": "template_social_short",
        "name": "Social Media Short",
        "description": "Short-form video optimized for social media",
        "category": "social",
        "config": {
            "resolution": "1080x1920",  # Portrait
            "fps": 30,
            "format": "mp4",
            "avatar": "casual_female_ro",
            "background": "modern",
            "voice": "romanian_female_friendly",
            "duration_max": 60
        },
        "preview_url": "/assets/templates/social_short_preview.jpg"
    },
    {
        "id": "template_explainer",
        "name": "Explainer Video",
        "description": "Educational explainer video with animations",
        "category": "education",
        "config": {
            "resolution": "1920x1080",
            "fps": 25,
            "format": "mp4",
            "avatar": "teacher_ro",
            "background": "whiteboard",
            "voice": "romanian_neutral",
            "include_subtitles": True
        },
        "preview_url": "/assets/templates/explainer_preview.jpg"
    }
]


@router.get("")
async def list_templates(category: Optional[str] = None):
    """Get list of available video templates"""
    try:
        templates = SAMPLE_TEMPLATES
        
        if category:
            templates = [t for t in templates if t["category"] == category]
        
        return {
            "templates": templates,
            "total": len(templates),
            "categories": list(set(t["category"] for t in SAMPLE_TEMPLATES))
        }
    
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {str(e)}")


@router.get("/{template_id}")
async def get_template(template_id: str):
    """Get specific template configuration"""
    try:
        template = next((t for t in SAMPLE_TEMPLATES if t["id"] == template_id), None)
        
        if not template:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        
        return template
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template {template_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get template: {str(e)}")


@router.post("/{template_id}/preview")
async def generate_template_preview(template_id: str, custom_text: Optional[str] = None):
    """Generate preview of template with custom text"""
    try:
        template = next((t for t in SAMPLE_TEMPLATES if t["id"] == template_id), None)
        
        if not template:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        
        # In production, would generate actual preview
        return {
            "template_id": template_id,
            "preview_url": template["preview_url"],
            "custom_text": custom_text,
            "status": "preview_ready"
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
