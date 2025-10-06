"""
Video Housekeeping Router - Auto-cleanup and maintenance
Provides endpoints for manual cleanup and housekeeping status
"""
from fastapi import APIRouter, HTTPException
import logging

from ..services.housekeeping import get_housekeeping_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/video/housekeeping", tags=["Video Housekeeping"])


@router.get("/status")
async def get_housekeeping_status():
    """Get housekeeping service status"""
    try:
        housekeeping = get_housekeeping_service()
        
        return housekeeping.get_health()
    
    except Exception as e:
        logger.error(f"Error getting housekeeping status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.post("/run")
async def run_manual_cleanup():
    """Manually trigger cleanup cycle"""
    try:
        housekeeping = get_housekeeping_service()
        
        if housekeeping.is_running:
            return {
                "status": "already_running",
                "message": "Cleanup is already in progress"
            }
        
        result = await housekeeping.run_cleanup()
        
        return result
    
    except Exception as e:
        logger.error(f"Error running cleanup: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.get("/history")
async def get_cleanup_history(limit: int = 10):
    """Get cleanup history (would be stored in DB in production)"""
    try:
        # For now, return housekeeping status
        # In production, store cleanup runs in database
        housekeeping = get_housekeeping_service()
        
        return {
            "status": "tracking_not_implemented",
            "message": "Cleanup history tracking would be implemented in production",
            "current_config": housekeeping.get_health()
        }
    
    except Exception as e:
        logger.error(f"Error getting cleanup history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")
