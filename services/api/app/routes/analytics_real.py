"""
REAL Analytics Routes - AutoPro Daune  
Google Analytics 4, conversion tracking, social insights
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from ..middleware.jwt_auth import get_current_user, CurrentUser
from ..services.analytics_service_real import get_analytics_service, AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics-real"])

class EventTrackRequest(BaseModel):
    event_name: str
    properties: Optional[dict] = {}

class ConversionTrackRequest(BaseModel):
    lead_id: UUID
    conversion_type: str
    value: Optional[float] = None

@router.post("/track-event")
async def track_event(
    request: EventTrackRequest,
    current_user: CurrentUser = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Track event to Google Analytics 4"""
    return await analytics_service.track_event(
        event_name=request.event_name,
        user_id=current_user.id,
        properties=request.properties
    )

@router.get("/conversion-funnel")
async def get_conversion_funnel(
    days: int = Query(30, ge=1, le=365),
    current_user: CurrentUser = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get conversion funnel - REAL calculation"""
    return await analytics_service.get_conversion_funnel(
        user_id=current_user.id,
        days=days
    )

@router.get("/social-insights")
async def get_social_insights(
    current_user: CurrentUser = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get social media insights - REAL data"""
    return await analytics_service.get_social_insights()

@router.post("/track-conversion")
async def track_conversion(
    request: ConversionTrackRequest,
    current_user: CurrentUser = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Track conversion event"""
    return await analytics_service.track_conversion(
        lead_id=request.lead_id,
        conversion_type=request.conversion_type,
        value=request.value
    )
