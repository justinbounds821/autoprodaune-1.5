"""
FAZA 2.5: Automation Alias Routes
Aliniere rute "automation" (FE cere /api/automation/*)

Backendul are deja working-automation. Adaugăm alias (SRP: doar mapare, fără duplicare logică).
Acoperă gap-ul "/api/automation/{logs|settings|toggle|trigger}" fără să atingi motorul.
Regulă: adaptor, nu rescrii engine-ul.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict
from .working_automation import automation_state, trigger_manual_post

router = APIRouter(prefix="/api/automation", tags=["automation-alias"])

class ToggleRequest(BaseModel):
    enabled: bool

class SettingsRequest(BaseModel):
    schedule: dict | None = None
    daily_target: int | None = None

@router.get("/status")
async def status() -> Dict[str, Any]:
    """Get automation status - aliased from working-automation"""
    return {
        "automation_active": automation_state["active"],
        "daily_target": automation_state["daily_target"],
        "posts_today": automation_state["posts_today"],
        "next_scheduled_post": automation_state["next_scheduled_post"],
        "schedule": automation_state["schedule"],
        "last_action": automation_state["recent_actions"][-1]
            if automation_state["recent_actions"] else None,
    }

@router.post("/toggle")
async def toggle(req: ToggleRequest):
    """Toggle automation - aliased from working-automation"""
    automation_state["active"] = bool(req.enabled)
    automation_state["recent_actions"].append({"action":"toggle","active":req.enabled})
    return {"ok": True, "active": automation_state["active"]}

@router.post("/trigger")
async def trigger():
    """Trigger manual post - aliased from working-automation"""
    return await trigger_manual_post()

@router.post("/settings")
async def settings(req: SettingsRequest):
    """Update automation settings - aliased from working-automation"""
    if req.schedule: 
        automation_state["schedule"] = req.schedule
    if req.daily_target is not None: 
        automation_state["daily_target"] = int(req.daily_target)
    
    automation_state["recent_actions"].append({"action":"settings_update"})
    
    return {"ok": True, "settings":{
        "schedule": automation_state["schedule"],
        "daily_target": automation_state["daily_target"],
    }}

@router.get("/logs")
async def logs():
    """Get automation logs - aliased from working-automation"""
    return {"items": automation_state["recent_actions"][-100:]}
