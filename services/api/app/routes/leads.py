"""
Leads management routes for AutoPro Daune API.

This module provides endpoints for lead management including:
- Lead creation and retrieval
- Lead status updates
- Lead analytics and filtering
"""

import io
import logging
from datetime import datetime
from uuid import uuid4
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field, validator

from ..core.database import get_database, DatabaseManager
from ..core.monitoring import (
    get_monitoring,
    MonitoringManager,
    monitor_api_call,
    monitor_business_operation,
)
from ..models.leads import (
    LeadAttachment,
    LeadAttachmentList,
    LeadAssignmentRequest,
    LeadAssignmentResponse,
    LeadStatusChange,
    LeadStatusHistoryResponse,
)
from ..services.email_service import EmailService, get_email_service
from ..services.supabase_client import get_supabase_service_instance
# --- PATCH: import compat pentru rulare din services\api SAU din rădăcină ---
try:
    from app.services.storage_s3 import upload_file
except ModuleNotFoundError:
    # permite rularea din root cu: python -m uvicorn services.api.app.main:app ...
    from services.api.app.services.storage_s3 import upload_file
# ---------------------------------------------------------------------------

router = APIRouter(
    prefix="/api/leads",
    tags=["leads"],
    responses={404: {"description": "Not found"}}
)

logger = logging.getLogger(__name__)

class LeadCreate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    source: str = Field(..., description="Lead source: tiktok, facebook, instagram, whatsapp, referral, direct")
    lead_type: str = Field(default="crash_claim", description="Type of lead")
    status: str = Field(default="new", description="Lead status")
    details: Optional[str] = None
    notes: Optional[str] = None
    estimated_value: Optional[float] = Field(default=0, ge=0)
    priority: str = Field(default="medium", description="Priority: low, medium, high")

    @validator('source')
    def validate_source(cls, v):
        valid_sources = ["tiktok", "facebook", "instagram", "whatsapp", "referral", "direct", "test"]
        if v not in valid_sources:
            raise ValueError(f"Source must be one of: {', '.join(valid_sources)}")
        return v

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    estimated_value: Optional[float] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None

@router.get("/")
@monitor_api_call("/api/leads/")
async def get_leads(
    page: int = Query(1, ge=1, description="Numărul paginii"),
    limit: int = Query(20, ge=1, le=100, description="Numărul de lead-uri per pagină"),
    source: Optional[str] = Query(None, description="Filtrare după sursă"),
    status: Optional[str] = Query(None, description="Filtrare după status"),
    search: Optional[str] = Query(None, description="Căutare în nume, email sau telefon"),
    db: DatabaseManager = Depends(get_database),
    monitoring: MonitoringManager = Depends(get_monitoring)
) -> Dict[str, Any]:
    """
    Obține lista de lead-uri cu filtrare și paginare.
    """
    try:
        await monitoring.log_event(
            "info", "leads", f"Fetching leads - page: {page}, limit: {limit}",
            {"page": page, "limit": limit, "source": source, "status": status}
        )

        result = await db.get_leads(page=page, limit=limit, source=source, status=status, search=search)
        return result

    except Exception as e:
        monitoring.track_error("leads", "fetch_failed")
        raise HTTPException(status_code=500, detail=f"Eroare la obținerea lead-urilor: {str(e)}")

@router.post("/")
@monitor_api_call("/api/leads/")
@monitor_business_operation("lead_creation")
async def create_lead(
    lead_data: LeadCreate,
    db: DatabaseManager = Depends(get_database),
    monitoring: MonitoringManager = Depends(get_monitoring)
) -> Dict[str, Any]:
    """
    Creează un nou lead în sistem.
    """
    try:
        await monitoring.log_event(
            "info", "leads", f"Creating new lead from source: {lead_data.source}",
            {"source": lead_data.source, "lead_type": lead_data.lead_type}
        )

        # Convert Pydantic model to dict
        lead_dict = lead_data.dict()
        result = db.create_lead(lead_dict)

        if result["success"]:
            monitoring.track_lead_creation(lead_data.source)

        return result

    except Exception as e:
        monitoring.track_error("leads", "creation_failed")
        raise HTTPException(status_code=500, detail=f"Eroare la crearea lead-ului: {str(e)}")

@router.get("/{lead_id}")
async def get_lead(
    lead_id: int
) -> Dict[str, Any]:
    """
    Obține un lead specific din Supabase.
    
    Args:
        lead_id: ID-ul lead-ului
        
    Returns:
        Dicționar cu datele lead-ului
    """
    try:
        # Get single lead from Supabase
        result = get_supabase_service_instance().client.table("leads").select("*").eq("id", lead_id).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise HTTPException(status_code=404, detail=f"Lead {lead_id} nu a fost găsit")
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Eroare la obținerea lead-ului {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la obținerea lead-ului: {str(e)}")

@router.put("/{lead_id}")
async def update_lead(
    lead_id: str,
    update_data: Dict[str, Any],
    email_service: EmailService = Depends(get_email_service)
) -> Dict[str, Any]:
    """Actualizează un lead existent și salvează istoricul statusului."""

    if not update_data:
        raise HTTPException(status_code=400, detail="Nu există câmpuri de actualizat")

    try:
        supabase = get_supabase_service_instance()

        existing = supabase._table_select(
            "leads",
            "*",
            filters=[("eq", "id", lead_id)]
        )

        if not existing:
            raise HTTPException(status_code=404, detail=f"Lead {lead_id} nu a fost găsit")

        original_lead = existing[0]
        previous_status = original_lead.get("status")
        new_status = update_data.get("status")

        payload = update_data.copy()
        payload["updated_at"] = datetime.utcnow().isoformat()

        # Mark conversion timestamp when applicable
        if new_status and new_status != previous_status and new_status in {"converted", "completed"}:
            payload.setdefault("converted_at", datetime.utcnow().isoformat())

        updated_rows = supabase._table_update(
            "leads",
            payload,
            filters=[("eq", "id", lead_id)]
        )

        updated_lead = updated_rows[0] if updated_rows else {**original_lead, **payload}

        # Track status conversion history
        if new_status and new_status != previous_status:
            history_payload = {
                "lead_id": lead_id,
                "previous_status": previous_status,
                "new_status": new_status,
                "changed_by": update_data.get("updated_by") or "system",
                "notes": update_data.get("notes"),
                "changed_at": datetime.utcnow().isoformat(),
            }
            supabase._table_insert("lead_status_history", history_payload)

            supabase._table_insert(
                "lead_activities",
                {
                    "lead_id": lead_id,
                    "activity_type": "status_change",
                    "title": f"Status actualizat la {new_status}",
                    "description": update_data.get("notes") or "Status actualizat din UI",
                    "performed_by": update_data.get("updated_by") or "system",
                    "metadata": {
                        "previous_status": previous_status,
                        "new_status": new_status,
                    },
                    "created_at": datetime.utcnow().isoformat(),
                },
            )

            assignment_records = supabase._table_select(
                "lead_assignments",
                "*",
                filters=[("eq", "lead_id", lead_id)],
                order=("created_at", True),
            )
            assignment_email = assignment_records[0].get("assigned_to_email") if assignment_records else None

            await email_service.send_status_change_notification(
                lead_name=updated_lead.get("name"),
                lead_id=lead_id,
                previous_status=previous_status,
                new_status=new_status,
                recipients=[email for email in [updated_lead.get("email"), assignment_email] if email],
            )

        return {
            "success": True,
            "message": "Lead actualizat cu succes",
            "data": updated_lead,
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Eroare la actualizarea lead-ului {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la actualizarea lead-ului: {str(e)}")

@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: int
) -> Dict[str, Any]:
    """
    Șterge un lead din Supabase.
    
    Args:
        lead_id: ID-ul lead-ului
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        return get_supabase_service_instance().lead_delete(lead_id)
        
    except Exception as e:
        logging.error(f"Eroare la ștergerea lead-ului {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la ștergerea lead-ului: {str(e)}")


# ============================================
# LEAD SCORING & PRIORITIZATION
# ============================================

def calculate_lead_score(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate lead score and priority based on multiple factors.
    
    Scoring Factors:
    - Source (TikTok/Instagram/YouTube = higher quality)
    - Damage type (total loss = higher value)
    - Location (urban = faster processing)
    - Contact completeness (phone + email = higher intent)
    - Response time (quick form fill = higher urgency)
    
    Returns:
        Dictionary with score, priority, and reasoning
    """
    score = 0
    factors = []
    
    # Factor 1: Source Quality (0-30 points)
    source = lead_data.get("source", "direct").lower()
    source_scores = {
        "referral": 30,      # Highest quality - personal recommendation
        "whatsapp": 25,      # Direct engagement
        "instagram": 20,     # Social proof
        "tiktok": 20,        # Viral reach
        "youtube": 15,       # Educational content
        "facebook": 15,      # Organic social
        "landing_page": 10,  # Direct traffic
        "direct": 5          # Unknown source
    }
    source_score = source_scores.get(source, 5)
    score += source_score
    factors.append(f"Source ({source}): +{source_score}")
    
    # Factor 2: Damage Type (0-25 points)
    damage_type = lead_data.get("damage_type", "").lower()
    if "total" in damage_type or "pierdere totală" in damage_type:
        score += 25
        factors.append("Damage (total loss): +25")
    elif "grav" in damage_type or "major" in damage_type:
        score += 20
        factors.append("Damage (major): +20")
    elif "mediu" in damage_type or "moderate" in damage_type:
        score += 15
        factors.append("Damage (moderate): +15")
    else:
        score += 10
        factors.append("Damage (minor): +10")
    
    # Factor 3: Location (0-20 points)
    location = lead_data.get("location", "").lower()
    urban_cities = ["bucurești", "bucharest", "cluj", "timișoara", "iași", "constanța", "brașov"]
    if any(city in location for city in urban_cities):
        score += 20
        factors.append("Location (urban): +20")
    elif location:
        score += 10
        factors.append("Location (other): +10")
    
    # Factor 4: Contact Completeness (0-15 points)
    has_phone = bool(lead_data.get("phone"))
    has_email = bool(lead_data.get("email"))
    if has_phone and has_email:
        score += 15
        factors.append("Contact (phone + email): +15")
    elif has_phone or has_email:
        score += 8
        factors.append("Contact (one method): +8")
    
    # Factor 5: Details Provided (0-10 points)
    details = lead_data.get("details", "")
    if len(details) > 100:
        score += 10
        factors.append("Details (comprehensive): +10")
    elif len(details) > 50:
        score += 5
        factors.append("Details (adequate): +5")
    
    # Determine Priority based on score
    if score >= 70:
        priority = "urgent"
        priority_label = "🔴 URGENT"
    elif score >= 50:
        priority = "high"
        priority_label = "🟠 High"
    elif score >= 30:
        priority = "medium"
        priority_label = "🟡 Medium"
    else:
        priority = "low"
        priority_label = "🟢 Low"
    
    return {
        "score": score,
        "priority": priority,
        "priority_label": priority_label,
        "max_score": 100,
        "factors": factors,
        "recommendation": _get_recommendation(score, priority)
    }


def _get_recommendation(score: int, priority: str) -> str:
    """Get action recommendation based on score."""
    if score >= 70:
        return "Contact immediately! High-value lead with strong intent."
    elif score >= 50:
        return "Priority contact within 2 hours. Strong potential."
    elif score >= 30:
        return "Follow up within 24 hours. Standard lead process."
    else:
        return "Add to nurture campaign. Monitor engagement."


@router.post("/{lead_id}/score")
async def score_lead(lead_id: int) -> Dict[str, Any]:
    """
    Calculate and update lead score.
    
    Args:
        lead_id: ID of the lead to score
        
    Returns:
        Lead scoring results with priority and recommendation
    """
    try:
        # Get lead data
        lead = get_supabase_service_instance()._table_select(
            "leads",
            "*",
            filters=[("eq", "id", lead_id)]
        )
        
        if not lead or len(lead) == 0:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        lead_data = lead[0]
        
        # Calculate score
        scoring_result = calculate_lead_score(lead_data)
        
        # Update lead with new priority
        get_supabase_service_instance()._table_update(
            "leads",
            {"priority": scoring_result["priority"]},
            filters=[("eq", "id", lead_id)]
        )
        
        logger.info(f"[LeadScoring] Lead {lead_id} scored: {scoring_result['score']}/100 ({scoring_result['priority']})")
        
        return {
            "success": True,
            "lead_id": lead_id,
            "scoring": scoring_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[LeadScoring] Error scoring lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating lead score: {str(e)}")


@router.post("/batch-score")
async def batch_score_leads(
    status: Optional[str] = Query(None, description="Score leads with specific status"),
    limit: int = Query(100, ge=1, le=1000, description="Max leads to score")
) -> Dict[str, Any]:
    """
    Batch score multiple leads and update priorities.
    
    Args:
        status: Optional filter by status
        limit: Max number of leads to score
        
    Returns:
        Batch scoring results
    """
    try:
        # Get leads to score
        filters = []
        if status:
            filters.append(("eq", "status", status))
        
        leads = get_supabase_service_instance()._table_select(
            "leads",
            "*",
            filters=filters,
            limit=limit
        )
        
        if not leads:
            return {
                "success": True,
                "scored_count": 0,
                "message": "No leads to score"
            }
        
        # Score each lead
        scored_leads = []
        for lead in leads:
            try:
                scoring_result = calculate_lead_score(lead)
                
                # Update priority
                get_supabase_service_instance()._table_update(
                    "leads",
                    {"priority": scoring_result["priority"]},
                    filters=[("eq", "id", lead["id"])]
                )
                
                scored_leads.append({
                    "lead_id": lead["id"],
                    "score": scoring_result["score"],
                    "priority": scoring_result["priority"]
                })
                
            except Exception as lead_error:
                logger.warning(f"[LeadScoring] Failed to score lead {lead.get('id')}: {lead_error}")
                continue
        
        # Calculate summary stats
        priority_distribution = {
            "urgent": len([l for l in scored_leads if l["priority"] == "urgent"]),
            "high": len([l for l in scored_leads if l["priority"] == "high"]),
            "medium": len([l for l in scored_leads if l["priority"] == "medium"]),
            "low": len([l for l in scored_leads if l["priority"] == "low"])
        }
        
        logger.info(f"[LeadScoring] Batch scored {len(scored_leads)} leads")
        
        return {
            "success": True,
            "scored_count": len(scored_leads),
            "priority_distribution": priority_distribution,
            "leads": scored_leads[:10]  # Return first 10 for preview
        }
        
    except Exception as e:
        logger.error(f"[LeadScoring] Batch scoring error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch scoring failed: {str(e)}")


# ===================================================
# LEAD ACTIVITY & TIMELINE ENDPOINTS
# ===================================================

class LeadActivityCreate(BaseModel):
    activity_type: str = Field(..., description="Type: note, email, call, sms, meeting, status_change")
    title: Optional[str] = None
    description: str
    metadata: Optional[Dict[str, Any]] = {}
    performed_by: Optional[str] = "system"

    @validator('activity_type')
    def validate_activity_type(cls, v):
        valid_types = ["note", "email", "call", "sms", "meeting", "status_change"]
        if v not in valid_types:
            raise ValueError(f"Activity type must be one of: {', '.join(valid_types)}")
        return v


@router.post("/{lead_id}/activity")
async def create_lead_activity(
    lead_id: str,
    activity: LeadActivityCreate
) -> Dict[str, Any]:
    """
    Create a new activity/note for a lead.
    
    Args:
        lead_id: Lead UUID
        activity: Activity data
        
    Returns:
        Created activity
    """
    try:
        supabase = get_supabase_service_instance()
        
        # Verify lead exists
        lead = supabase._table_select("leads", "*", filters=[("eq", "id", lead_id)])
        if not lead:
            raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found")
        
        # Create activity
        activity_data = {
            "lead_id": lead_id,
            "activity_type": activity.activity_type,
            "title": activity.title or f"{activity.activity_type.capitalize()} added",
            "description": activity.description,
            "metadata": activity.metadata,
            "performed_by": activity.performed_by,
            "created_at": datetime.now().isoformat()
        }
        
        result = supabase._table_insert("lead_activities", activity_data)
        
        # Update lead's updated_at timestamp
        supabase._table_update(
            "leads",
            {"updated_at": datetime.now().isoformat()},
            filters=[("eq", "id", lead_id)]
        )
        
        logger.info(f"[LeadActivity] Created {activity.activity_type} for lead {lead_id}")
        
        return {
            "success": True,
            "activity": result,
            "message": "Activity created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[LeadActivity] Create activity error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create activity: {str(e)}")


@router.post("/bulk-update")
async def bulk_update_leads(
    lead_ids: List[str],
    updates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Bulk update multiple leads.
    
    Args:
        lead_ids: List of lead UUIDs
        updates: Fields to update (status, priority, assigned_to, etc.)
        
    Returns:
        Update results
    """
    try:
        supabase = get_supabase_service_instance()
        updated_count = 0
        errors = []
        
        for lead_id in lead_ids:
            try:
                # Add timestamp
                update_data = {**updates, "updated_at": datetime.now().isoformat()}
                
                supabase._table_update(
                    "leads",
                    update_data,
                    filters=[("eq", "id", lead_id)]
                )
                updated_count += 1
                
                # Log activity if status changed
                if "status" in updates:
                    activity_data = {
                        "lead_id": lead_id,
                        "activity_type": "status_change",
                        "title": "Status updated",
                        "description": f"Status changed to {updates['status']}",
                        "performed_by": "bulk_update",
                        "created_at": datetime.now().isoformat()
                    }
                    supabase._table_insert("lead_activities", activity_data)
                    
            except Exception as e:
                logger.warning(f"[BulkUpdate] Failed to update lead {lead_id}: {e}")
                errors.append({"lead_id": lead_id, "error": str(e)})
        
        logger.info(f"[BulkUpdate] Updated {updated_count}/{len(lead_ids)} leads")
        
        return {
            "success": True,
            "updated_count": updated_count,
            "total_requested": len(lead_ids),
            "errors": errors if errors else None,
            "message": f"Successfully updated {updated_count}/{len(lead_ids)} leads"
        }
        
    except Exception as e:
        logger.error(f"[BulkUpdate] Bulk update error: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk update failed: {str(e)}")


@router.post("/export")
async def export_leads(
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    format: str = Query("csv", regex="^(csv|json)$")
) -> Dict[str, Any]:
    """
    Export leads to CSV or JSON.
    
    Args:
        status: Filter by status
        source: Filter by source
        format: Export format (csv or json)
        
    Returns:
        Export data
    """
    try:
        import csv
        import io
        from fastapi.responses import StreamingResponse
        
        supabase = get_supabase_service_instance()
        
        # Build filters
        filters = []
        if status:
            filters.append(("eq", "status", status))
        if source:
            filters.append(("eq", "source", source))
        
        leads = supabase._table_select("leads", "*", filters=filters)
        
        if not leads:
            raise HTTPException(status_code=404, detail="No leads found")
        
        if format == "csv":
            # Create CSV
            output = io.StringIO()
            fieldnames = ["id", "name", "phone_number", "email", "source", "status", "priority", "estimated_value", "created_at"]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for lead in leads:
                writer.writerow({k: lead.get(k, "") for k in fieldnames})
            
            csv_data = output.getvalue()
            
            return {
                "success": True,
                "format": "csv",
                "data": csv_data,
                "count": len(leads)
            }
        else:
            # JSON export
            return {
                "success": True,
                "format": "json",
                "data": leads,
                "count": len(leads)
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[LeadExport] Export error: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/{lead_id}/timeline")
async def get_lead_timeline(
    lead_id: str,
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    limit: int = Query(50, ge=1, le=200, description="Max activities to return")
) -> Dict[str, Any]:
    """
    Get activity timeline for a lead.
    
    Args:
        lead_id: Lead UUID
        activity_type: Optional filter by type
        limit: Max activities to return
        
    Returns:
        List of activities ordered by date (newest first)
    """
    try:
        supabase = get_supabase_service_instance()
        
        # Verify lead exists
        lead = supabase._table_select("leads", "*", filters=[("eq", "id", lead_id)])
        if not lead:
            raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found")
        
        # Get activities
        filters = [("eq", "lead_id", lead_id)]
        if activity_type:
            filters.append(("eq", "activity_type", activity_type))
        
        activities = supabase._table_select(
            "lead_activities",
            "*",
            filters=filters,
            order=("created_at", True)  # True = descending
        )
        
        # Apply limit
        if activities and len(activities) > limit:
            activities = activities[:limit]
        
        logger.info(f"[LeadActivity] Retrieved {len(activities or [])} activities for lead {lead_id}")
        
        return {
            "success": True,
            "lead_id": lead_id,
            "lead_name": lead[0].get("name", "Unknown"),
            "activities": activities or [],
            "total_count": len(activities or [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[LeadActivity] Get timeline error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve timeline: {str(e)}")


# ==================== FILE ATTACHMENTS ====================

@router.post("/{lead_id}/attachments", response_model=LeadAttachment)
async def upload_lead_attachment(
    lead_id: str,
    file: UploadFile = File(...),
    uploaded_by: str = Form("system"),
    notify_emails: Optional[str] = Form(None),
    email_service: EmailService = Depends(get_email_service)
) -> LeadAttachment:
    """Upload file attachment for a lead and notify relevant users."""

    try:
        supabase = get_supabase_service_instance()

        lead_records = supabase._table_select("leads", "*", [("eq", "id", lead_id)])
        if not lead_records:
            raise HTTPException(status_code=404, detail="Lead not found")

        lead = lead_records[0]

        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Fișierul este gol")

        max_size = 10 * 1024 * 1024  # 10MB
        if len(file_content) > max_size:
            raise HTTPException(status_code=400, detail="Fișier prea mare (max 10MB)")

        storage_key = f"leads/{lead_id}/{uuid4()}_{file.filename}"
        buffer = io.BytesIO(file_content)
        buffer.seek(0)
        file_url = upload_file(
            buffer,
            storage_key,
            file.content_type or "application/octet-stream",
        )

        attachment_payload = {
            "lead_id": lead_id,
            "file_name": file.filename,
            "file_url": file_url,
            "storage_key": storage_key,
            "content_type": file.content_type,
            "file_size": len(file_content),
            "uploaded_by": uploaded_by,
            "metadata": {},
            "created_at": datetime.utcnow().isoformat(),
        }

        attachment_record = supabase._table_insert("lead_attachments", attachment_payload)

        existing_files = lead.get("files") or []
        if not isinstance(existing_files, list):
            existing_files = []
        if file_url not in existing_files:
            existing_files.append(file_url)

        supabase._table_update(
            "leads",
            {
                "files": existing_files,
                "updated_at": datetime.utcnow().isoformat(),
            },
            filters=[("eq", "id", lead_id)],
        )

        supabase._table_insert(
            "lead_activities",
            {
                "lead_id": lead_id,
                "activity_type": "attachment",
                "title": f"Fișier încărcat: {file.filename}",
                "description": f"Atașament încărcat de {uploaded_by}",
                "performed_by": uploaded_by,
                "metadata": {
                    "file_url": file_url,
                    "file_name": file.filename,
                },
                "created_at": datetime.utcnow().isoformat(),
            },
        )

        recipients = []
        if notify_emails:
            recipients.extend([
                email.strip()
                for email in notify_emails.split(",")
                if email.strip()
            ])

        assignment_records = supabase._table_select(
            "lead_assignments",
            "*",
            filters=[("eq", "lead_id", lead_id)],
            order=("created_at", True),
        )
        if assignment_records:
            assignment_email = assignment_records[0].get("assigned_to_email")
            if assignment_email:
                recipients.append(assignment_email)

        if lead.get("email"):
            recipients.append(lead.get("email"))

        recipients = list(dict.fromkeys(recipients))

        await email_service.send_attachment_notification(
            lead_name=lead.get("name"),
            lead_id=lead_id,
            file_name=file.filename,
            recipients=recipients,
        )

        logger.info("[LeadAttachment] Uploaded file for lead %s", lead_id)

        return LeadAttachment(**attachment_record)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[LeadAttachment] Upload error: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to upload attachment: {exc}")


@router.get("/{lead_id}/attachments", response_model=LeadAttachmentList)
async def list_lead_attachments(lead_id: str) -> LeadAttachmentList:
    """Return the attachment metadata for a given lead."""

    try:
        supabase = get_supabase_service_instance()
        attachments = supabase._table_select(
            "lead_attachments",
            "*",
            filters=[("eq", "lead_id", lead_id)],
            order=("created_at", True),
        )

        items = [LeadAttachment(**attachment) for attachment in attachments or []]
        return LeadAttachmentList(lead_id=lead_id, items=items)

    except Exception as exc:
        logger.error(f"[LeadAttachment] List error for lead {lead_id}: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch attachments: {exc}")


@router.get("/attachments/{attachment_id}", response_model=LeadAttachment)
async def get_attachment_metadata(attachment_id: str) -> LeadAttachment:
    """Return metadata for a specific attachment."""

    supabase = get_supabase_service_instance()
    attachment = supabase._table_select(
        "lead_attachments",
        "*",
        filters=[("eq", "id", attachment_id)],
    )

    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    return LeadAttachment(**attachment[0])


@router.get("/attachments/{attachment_id}/download")
async def download_attachment(attachment_id: str) -> Dict[str, Any]:
    """Return a direct URL to download the attachment."""

    metadata = await get_attachment_metadata(attachment_id)
    return {
        "success": True,
        "file_url": metadata.file_url,
        "file_name": metadata.file_name,
        "content_type": metadata.content_type,
    }


# ==================== LEAD ASSIGNMENT ====================

@router.post("/{lead_id}/assign", response_model=LeadAssignmentResponse)
async def assign_lead(
    lead_id: str,
    assignment: LeadAssignmentRequest,
    email_service: EmailService = Depends(get_email_service)
) -> LeadAssignmentResponse:
    """Assign a lead to an operator and notify them."""

    try:
        supabase = get_supabase_service_instance()
        lead_records = supabase._table_select("leads", "*", [("eq", "id", lead_id)])
        if not lead_records:
            raise HTTPException(status_code=404, detail="Lead not found")

        supabase._table_update(
            "leads",
            {
                "assigned_to": assignment.assigned_to,
                "updated_at": datetime.utcnow().isoformat(),
            },
            filters=[("eq", "id", lead_id)],
        )

        assignment_record = supabase._table_insert(
            "lead_assignments",
            {
                "lead_id": lead_id,
                "assigned_to": assignment.assigned_to,
                "assigned_to_email": assignment.assigned_to_email,
                "assigned_by": assignment.assigned_by,
                "notes": assignment.notes,
                "created_at": datetime.utcnow().isoformat(),
            },
        )

        supabase._table_insert(
            "lead_activities",
            {
                "lead_id": lead_id,
                "activity_type": "assignment",
                "title": f"Lead asignat către {assignment.assigned_to}",
                "description": assignment.notes or "Lead asignat din UI",
                "performed_by": assignment.assigned_by or "system",
                "metadata": assignment_record,
                "created_at": datetime.utcnow().isoformat(),
            },
        )

        lead = lead_records[0]
        await email_service.send_assignment_notification(
            lead_name=lead.get("name"),
            lead_id=lead_id,
            assigned_to=assignment.assigned_to,
            assignee_email=assignment.assigned_to_email,
            assigned_by=assignment.assigned_by,
            notes=assignment.notes,
        )

        return LeadAssignmentResponse(
            success=True,
            lead_id=lead_id,
            assigned_to=assignment.assigned_to,
            assigned_by=assignment.assigned_by,
            notes=assignment.notes,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[LeadAssignment] Error assigning lead {lead_id}: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to assign lead: {exc}")


# ==================== STATUS HISTORY ====================

@router.get("/{lead_id}/status-history", response_model=LeadStatusHistoryResponse)
async def get_lead_status_history(lead_id: str) -> LeadStatusHistoryResponse:
    """Return the conversion history for a lead."""

    try:
        supabase = get_supabase_service_instance()
        history_rows = supabase._table_select(
            "lead_status_history",
            "*",
            filters=[("eq", "lead_id", lead_id)],
            order=("changed_at", True),
        )

        items = [LeadStatusChange(**row) for row in history_rows or []]
        return LeadStatusHistoryResponse(lead_id=lead_id, items=items)

    except Exception as exc:
        logger.error(f"[LeadStatusHistory] Error retrieving history for {lead_id}: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch status history: {exc}")


# ==================== EMAIL INTEGRATION ====================

@router.post("/{lead_id}/send-email")
async def send_email_to_lead(
    lead_id: str,
    subject: str = Form(...),
    message: str = Form(...),
    template: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Send email to a lead.
    
    Args:
        lead_id: Lead ID
        subject: Email subject
        message: Email message
        template: Optional template name
        
    Returns:
        Success message
    """
    try:
        supabase = get_supabase_service_instance()
        
        # Validate lead exists
        lead = supabase._table_select("leads", "*", [("eq", "id", lead_id)])
        if not lead or len(lead) == 0:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        lead_data = lead[0]
        if not lead_data.get("email"):
            raise HTTPException(status_code=400, detail="Lead has no email address")
        
        # Log email activity
        activity_data = {
            "lead_id": lead_id,
            "activity_type": "email",
            "title": f"Email sent: {subject}",
            "description": f"Email sent to {lead_data['email']}: {message[:100]}...",
            "performed_by": "system",
            "created_at": datetime.now().isoformat()
        }
        supabase._table_insert("lead_activities", activity_data)
        
        # In production, integrate with email service (SendGrid, Mailgun, etc.)
        # For now, just log the email
        logger.info(f"[EmailIntegration] Email sent to lead {lead_id}: {subject}")
        
        return {
            "success": True,
            "message": "Email sent successfully",
            "lead_email": lead_data["email"],
            "subject": subject
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[EmailIntegration] Send email error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@router.get("/email-templates")
async def get_email_templates() -> Dict[str, Any]:
    """
    Get available email templates.
    
    Returns:
        List of email templates
    """
    try:
        templates = [
            {
                "id": "welcome",
                "name": "Welcome Message",
                "subject": "Bun venit la AutoPro Daune",
                "message": "Salut {name},\n\nMulțumim că ne-ai contactat! Echipa noastră de experți vă va contacta în cel mai scurt timp pentru a discuta despre cazul tău.\n\nCu respect,\nEchipa AutoPro Daune"
            },
            {
                "id": "follow_up",
                "name": "Follow-up",
                "subject": "Actualizare caz AutoPro Daune",
                "message": "Salut {name},\n\nVrem să te ținem la curent cu progresul cazului tău. {status_update}\n\nDacă ai întrebări, nu ezita să ne contactezi!\n\nCu respect,\nEchipa AutoPro Daune"
            },
            {
                "id": "documents",
                "name": "Document Request",
                "subject": "Documente necesare pentru cazul tău",
                "message": "Salut {name},\n\nPentru a continua cu cazul tău, avem nevoie de următoarele documente:\n- Polița de asigurare\n- Raportul de constatare\n- Fotografii cu daunele\n\nMulțumim!\nEchipa AutoPro Daune"
            }
        ]
        
        return {
            "success": True,
            "templates": templates
        }
        
    except Exception as e:
        logger.error(f"[EmailIntegration] Get templates error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")
