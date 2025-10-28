"""
Lead management REST API endpoints
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field, validator
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/workspace/microservices/autopro-common")
from autopro_common import get_db_session, get_logger, get_metrics, get_redis

from app.models.lead import Lead, LeadActivity, LeadStatus, LeadPriority, LeadSource
from app.services.lead_service import LeadService
from app.services.scoring_service import LeadScoringService

router = APIRouter(prefix="/leads", tags=["leads"])
logger = get_logger(__name__)


# ============== Request/Response Models ==============

class LeadCreate(BaseModel):
    """Lead creation schema"""
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    source: str = Field(..., description="Lead source")
    lead_type: str = Field(default="crash_claim")
    status: str = Field(default="new")
    details: Optional[str] = None
    notes: Optional[str] = None
    estimated_value: Optional[float] = Field(default=0, ge=0)
    priority: str = Field(default="medium")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('source')
    def validate_source(cls, v):
        valid_sources = [s.value for s in LeadSource]
        if v not in valid_sources:
            raise ValueError(f"Source must be one of: {', '.join(valid_sources)}")
        return v


class LeadUpdate(BaseModel):
    """Lead update schema"""
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    estimated_value: Optional[float] = None
    assigned_to: Optional[str] = None


class LeadActivityCreate(BaseModel):
    """Lead activity creation schema"""
    activity_type: str = Field(..., description="note, email, call, sms, meeting, status_change")
    title: Optional[str] = None
    description: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    performed_by: Optional[str] = "system"


# ============== Endpoints ==============

@router.post("/", status_code=201)
async def create_lead(
    lead_data: LeadCreate,
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Create a new lead
    
    Args:
        lead_data: Lead creation data
        session: Database session
        
    Returns:
        Created lead data
    """
    try:
        logger.info(f"Creating lead from source: {lead_data.source}")
        
        # Create lead using service
        lead_service = LeadService(session)
        lead = await lead_service.create_lead(lead_data.dict())
        
        # Track metrics
        metrics = get_metrics()
        metrics.track_business_event("lead_created")
        metrics.track_business_event(f"lead_from_{lead_data.source}")
        
        # Publish event to message queue
        try:
            from autopro_common import get_producer
            producer = get_producer()
            await producer.publish("lead.created", {
                "lead_id": lead.id,
                "source": lead.source,
                "priority": lead.priority,
                "timestamp": datetime.utcnow().isoformat(),
            })
        except Exception as e:
            logger.warning(f"Failed to publish lead.created event: {e}")
        
        logger.info(f"Lead created successfully: ID={lead.id}")
        
        return {
            "success": True,
            "message": "Lead created successfully",
            "data": lead.to_dict(),
        }
        
    except Exception as e:
        logger.error(f"Failed to create lead: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create lead: {str(e)}")


@router.get("/")
async def get_leads(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    source: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Get leads with filtering and pagination
    
    Args:
        page: Page number
        limit: Items per page
        source: Filter by source
        status: Filter by status
        priority: Filter by priority
        search: Search in name, email, phone
        session: Database session
        
    Returns:
        Paginated leads list
    """
    try:
        offset = (page - 1) * limit
        
        # Build query
        query = select(Lead)
        
        # Apply filters
        if source:
            query = query.where(Lead.source == source)
        if status:
            query = query.where(Lead.status == status)
        if priority:
            query = query.where(Lead.priority == priority)
        if search:
            query = query.where(
                or_(
                    Lead.name.ilike(f"%{search}%"),
                    Lead.email.ilike(f"%{search}%"),
                    Lead.phone_number.ilike(f"%{search}%"),
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Lead.created_at.desc()).offset(offset).limit(limit)
        
        # Execute query
        result = await session.execute(query)
        leads = result.scalars().all()
        
        return {
            "success": True,
            "data": [lead.to_dict() for lead in leads],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit,
            },
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch leads: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch leads: {str(e)}")


@router.get("/{lead_id}")
async def get_lead(
    lead_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Get a specific lead by ID
    
    Args:
        lead_id: Lead ID
        session: Database session
        
    Returns:
        Lead data
    """
    try:
        lead_service = LeadService(session)
        lead = await lead_service.get_lead(lead_id)
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return {
            "success": True,
            "data": lead.to_dict(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch lead: {str(e)}")


@router.put("/{lead_id}")
async def update_lead(
    lead_id: int,
    update_data: LeadUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Update a lead
    
    Args:
        lead_id: Lead ID
        update_data: Update data
        session: Database session
        
    Returns:
        Updated lead data
    """
    try:
        lead_service = LeadService(session)
        lead = await lead_service.update_lead(lead_id, update_data.dict(exclude_unset=True))
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Track status change
        if update_data.status:
            metrics = get_metrics()
            metrics.track_business_event(f"lead_status_{update_data.status}")
        
        logger.info(f"Lead {lead_id} updated successfully")
        
        return {
            "success": True,
            "message": "Lead updated successfully",
            "data": lead.to_dict(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update lead: {str(e)}")


@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Delete a lead
    
    Args:
        lead_id: Lead ID
        session: Database session
        
    Returns:
        Success message
    """
    try:
        lead_service = LeadService(session)
        success = await lead_service.delete_lead(lead_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        logger.info(f"Lead {lead_id} deleted successfully")
        
        return {
            "success": True,
            "message": "Lead deleted successfully",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete lead: {str(e)}")


@router.post("/{lead_id}/activities")
async def create_activity(
    lead_id: int,
    activity_data: LeadActivityCreate,
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Create a new activity for a lead
    
    Args:
        lead_id: Lead ID
        activity_data: Activity data
        session: Database session
        
    Returns:
        Created activity data
    """
    try:
        lead_service = LeadService(session)
        activity = await lead_service.create_activity(lead_id, activity_data.dict())
        
        if not activity:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        logger.info(f"Activity created for lead {lead_id}: {activity_data.activity_type}")
        
        return {
            "success": True,
            "message": "Activity created successfully",
            "data": activity.to_dict(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create activity: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create activity: {str(e)}")


@router.get("/{lead_id}/timeline")
async def get_timeline(
    lead_id: int,
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Get activity timeline for a lead
    
    Args:
        lead_id: Lead ID
        limit: Max activities to return
        session: Database session
        
    Returns:
        Activity timeline
    """
    try:
        query = (
            select(LeadActivity)
            .where(LeadActivity.lead_id == lead_id)
            .order_by(LeadActivity.created_at.desc())
            .limit(limit)
        )
        
        result = await session.execute(query)
        activities = result.scalars().all()
        
        return {
            "success": True,
            "lead_id": lead_id,
            "activities": [activity.to_dict() for activity in activities],
            "total_count": len(activities),
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch timeline for lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch timeline: {str(e)}")


@router.post("/bulk-update")
async def bulk_update(
    lead_ids: List[int],
    updates: Dict[str, Any],
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Bulk update multiple leads
    
    Args:
        lead_ids: List of lead IDs
        updates: Fields to update
        session: Database session
        
    Returns:
        Update results
    """
    try:
        lead_service = LeadService(session)
        updated_count = await lead_service.bulk_update(lead_ids, updates)
        
        logger.info(f"Bulk updated {updated_count}/{len(lead_ids)} leads")
        
        return {
            "success": True,
            "updated_count": updated_count,
            "total_requested": len(lead_ids),
            "message": f"Successfully updated {updated_count}/{len(lead_ids)} leads",
        }
        
    except Exception as e:
        logger.error(f"Failed to bulk update leads: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk update failed: {str(e)}")
