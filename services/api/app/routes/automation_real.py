"""
REAL Automation Routes - AutoPro Daune
Scheduled tasks, cron jobs, automated posting
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from ..middleware.jwt_auth import get_current_user, get_current_admin, CurrentUser
from ..services.automation_service_real import get_automation_service, AutomationService

router = APIRouter(prefix="/api/automation", tags=["automation-real"])

@router.get("/status")
async def get_automation_status(
    current_user: CurrentUser = Depends(get_current_user),
    automation_service: AutomationService = Depends(get_automation_service)
):
    """Get automation status - REAL from database"""
    return await automation_service.get_automation_status()

@router.post("/execute")
async def execute_automation(
    current_user: CurrentUser = Depends(get_current_admin),  # Admin only
    automation_service: AutomationService = Depends(get_automation_service)
):
    """Manually trigger automation - REAL execution"""
    return await automation_service.execute_daily_automation(current_user.id)

@router.get("/logs")
async def get_automation_logs(
    limit: int = Query(50, ge=1, le=500),
    task_type: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
    automation_service: AutomationService = Depends(get_automation_service)
):
    """Get automation logs - REAL from database"""
    logs = await automation_service.get_automation_logs(
        limit=limit,
        task_type=task_type
    )
    
    return {
        "logs": logs,
        "total": len(logs)
    }
