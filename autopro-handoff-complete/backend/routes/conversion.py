"""
Conversion tracking routes for AutoPro Daune API.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from ..services.conversion_tracking import (
    ConversionTracker,
    ConversionEvent,
    ConversionSource
)
from ..services.supabase_client import get_supabase_service_instance

router = APIRouter(
    prefix="/api/conversion",
    tags=["conversion"],
    responses={404: {"description": "Not found"}}
)

logger = logging.getLogger(__name__)


class TrackEventRequest(BaseModel):
    event_type: str
    source: str
    user_id: Optional[str] = None
    lead_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/track")
async def track_event(request: TrackEventRequest) -> Dict[str, Any]:
    """
    Track a conversion event.
    
    Args:
        request: Event tracking data
        
    Returns:
        Tracking result
    """
    try:
        # Initialize tracker with Supabase
        tracker = ConversionTracker(supabase_client=get_supabase_service_instance())
        
        # Convert strings to enums
        try:
            event_type = ConversionEvent(request.event_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid event_type: {request.event_type}"
            )
        
        try:
            source = ConversionSource(request.source)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source: {request.source}"
            )
        
        # Track event
        result = tracker.track_event(
            event_type=event_type,
            source=source,
            user_id=request.user_id,
            lead_id=request.lead_id,
            metadata=request.metadata
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ConversionAPI] Tracking failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to track event: {str(e)}"
        )


@router.get("/stats")
async def get_conversion_stats(
    source: Optional[str] = None,
    days: int = 30
) -> Dict[str, Any]:
    """
    Get conversion statistics.
    
    Args:
        source: Optional source filter
        days: Number of days to analyze
        
    Returns:
        Conversion statistics
    """
    try:
        tracker = ConversionTracker(supabase_client=get_supabase_service_instance())
        
        source_enum = ConversionSource(source) if source else None
        
        stats = tracker.get_conversion_rate(source=source_enum, days=days)
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"[ConversionAPI] Stats failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get conversion stats: {str(e)}"
        )


@router.get("/top-sources")
async def get_top_sources(days: int = 30, limit: int = 5) -> Dict[str, Any]:
    """
    Get top performing sources.
    
    Args:
        days: Number of days to analyze
        limit: Max sources to return
        
    Returns:
        Top sources
    """
    try:
        tracker = ConversionTracker(supabase_client=get_supabase_service_instance())
        
        sources = tracker.get_top_sources(days=days, limit=limit)
        
        return {
            "success": True,
            "top_sources": sources
        }
        
    except Exception as e:
        logger.error(f"[ConversionAPI] Top sources failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get top sources: {str(e)}"
        )
