"""
REAL Lead Management Routes - AutoPro Daune
All routes use LeadService and require authentication
NO MOCKS - All data from database
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from ..middleware.jwt_auth import get_current_user, CurrentUser
from ..services.lead_service_real import get_lead_service, LeadService
from ..models.complete_models import Lead, LeadCreate, LeadUpdate, Activity, ActivityCreate
from fastapi.responses import StreamingResponse
import io

router = APIRouter(prefix="/api/leads", tags=["leads-real"])

@router.post("", response_model=Lead, status_code=201)
async def create_lead(
    lead_data: LeadCreate,
    current_user: CurrentUser = Depends(get_current_user),
    lead_service: LeadService = Depends(get_lead_service)
):
    """
    Create new lead - REAL implementation with auth
    Calculates score automatically
    """
    return await lead_service.create_lead(
        user_id=current_user.id,
        lead_data=lead_data
    )

@router.get("", response_model=dict)
async def list_leads(
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None, ge=0, le=100),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
    lead_service: LeadService = Depends(get_lead_service)
):
    """
    List leads with filters and pagination
    Returns: {leads: [...], total: N}
    """
    return await lead_service.list_leads(
        user_id=current_user.id,
        status=status,
        source=source,
        priority=priority,
        min_score=min_score,
        search=search,
        limit=limit,
        offset=offset
    )

@router.get("/{lead_id}", response_model=Lead)
async def get_lead(
    lead_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    lead_service: LeadService = Depends(get_lead_service)
):
    """Get single lead by ID"""
    return await lead_service.get_lead(
        lead_id=lead_id,
        user_id=current_user.id
    )

@router.put("/{lead_id}", response_model=Lead)
async def update_lead(
    lead_id: UUID,
    update_data: LeadUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    lead_service: LeadService = Depends(get_lead_service)
):
    """
    Update lead - recalculates score if needed
    Logs status changes to timeline
    """
    return await lead_service.update_lead(
        lead_id=lead_id,
        user_id=current_user.id,
        update_data=update_data
    )

@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: UUID,
    hard_delete: bool = Query(False),
    current_user: CurrentUser = Depends(get_current_user),
    lead_service: LeadService = Depends(get_lead_service)
):
    """
    Delete lead (soft by default, hard if specified)
    """
    success = await lead_service.delete_lead(
        lead_id=lead_id,
        user_id=current_user.id,
        hard_delete=hard_delete
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return {
        "success": True,
        "message": f"Lead {'permanently deleted' if hard_delete else 'marked as deleted'}"
    }

@router.get("/{lead_id}/timeline", response_model=List[Activity])
async def get_lead_timeline(
    lead_id: UUID,
    limit: int = Query(100, ge=1, le=1000),
    current_user: CurrentUser = Depends(get_current_user),
    lead_service: LeadService = Depends(get_lead_service)
):
    """Get lead activity timeline"""
    # Verify user owns this lead
    await lead_service.get_lead(lead_id=lead_id, user_id=current_user.id)
    
    return await lead_service.get_timeline(
        lead_id=lead_id,
        limit=limit
    )

@router.post("/{lead_id}/activity", response_model=Activity, status_code=201)
async def add_lead_activity(
    lead_id: UUID,
    activity_data: ActivityCreate,
    current_user: CurrentUser = Depends(get_current_user),
    lead_service: LeadService = Depends(get_lead_service)
):
    """Add activity to lead timeline"""
    # Verify user owns this lead
    await lead_service.get_lead(lead_id=lead_id, user_id=current_user.id)
    
    return await lead_service.add_activity(
        lead_id=lead_id,
        user_id=current_user.id,
        activity_type=activity_data.activity_type,
        title=activity_data.title,
        description=activity_data.description
    )

@router.post("/bulk-update")
async def bulk_update_leads(
    lead_ids: List[UUID],
    new_status: str,
    current_user: CurrentUser = Depends(get_current_user),
    lead_service: LeadService = Depends(get_lead_service)
):
    """
    Bulk update lead status
    Returns: {success_count, failed_count}
    """
    result = await lead_service.bulk_update_status(
        lead_ids=lead_ids,
        user_id=current_user.id,
        new_status=new_status
    )
    
    return {
        "success": True,
        "message": f"Updated {result['success_count']} leads",
        **result
    }

@router.get("/export/csv")
async def export_leads_csv(
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    lead_service: LeadService = Depends(get_lead_service)
):
    """
    Export leads to CSV
    Returns: CSV file download
    """
    csv_content = await lead_service.export_to_csv(
        user_id=current_user.id,
        status=status,
        source=source
    )
    
    # Return as downloadable file
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=leads_export_{current_user.id}.csv"
        }
    )

@router.get("/statistics/dashboard")
async def get_lead_statistics(
    days: int = Query(30, ge=1, le=365),
    current_user: CurrentUser = Depends(get_current_user),
    lead_service: LeadService = Depends(get_lead_service)
):
    """
    Get lead statistics for dashboard
    REAL calculations from database
    """
    return await lead_service.get_statistics(
        user_id=current_user.id,
        days=days
    )
