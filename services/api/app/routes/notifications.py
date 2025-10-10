"""Notification routes including email, SMS and preference management."""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.automation import NotificationPreferencePayload, NotificationPreferenceResponse
from ..services.notifications import NotificationService

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(db)


@router.get("/preferences/{user_id}", response_model=Dict[str, List[NotificationPreferenceResponse]])
async def list_preferences(
    user_id: str, service: NotificationService = Depends(get_notification_service)
) -> Dict[str, Any]:
    preferences = service.list_preferences(user_id)
    return {
        "preferences": [NotificationPreferenceResponse.parse_obj(_format_preference(pref)) for pref in preferences]
    }


@router.put("/preferences", response_model=NotificationPreferenceResponse)
async def upsert_preference(
    payload: NotificationPreferencePayload, service: NotificationService = Depends(get_notification_service)
) -> NotificationPreferenceResponse:
    preference = service.upsert_preference(payload.dict(by_alias=False))
    return NotificationPreferenceResponse.parse_obj(_format_preference(preference))


@router.delete("/preferences/{user_id}/{channel}", status_code=204)
async def delete_preference(
    user_id: str, channel: str, service: NotificationService = Depends(get_notification_service)
) -> None:
    service.delete_preference(user_id, channel)


@router.post("/email", response_model=Dict[str, Any])
async def send_email(
    payload: Dict[str, Any], service: NotificationService = Depends(get_notification_service)
) -> Dict[str, Any]:
    try:
        await service.send_email_async(payload)
        return {"success": True, "message": "Email programat"}
    except Exception as exc:  # pragma: no cover - runtime errors
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/sms", response_model=Dict[str, Any])
async def send_sms(
    payload: Dict[str, Any], service: NotificationService = Depends(get_notification_service)
) -> Dict[str, Any]:
    try:
        await service.send_sms_async(payload)
        return {"success": True, "message": "SMS programat"}
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/test", response_model=Dict[str, Any])
async def send_test_notification(
    service: NotificationService = Depends(get_notification_service),
) -> Dict[str, Any]:
    await service.send_email_async({"subject": "Test notificare", "body": "Funcția de notificări funcționează."})
    return {"success": True, "message": "Notificare de test trimisă"}


def _format_preference(preference: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": preference["id"],
        "userId": preference.get("user_id"),
        "channel": preference.get("channel"),
        "destination": preference.get("destination"),
        "enabled": preference.get("enabled", True),
        "quietHoursStart": preference.get("quiet_hours_start"),
        "quietHoursEnd": preference.get("quiet_hours_end"),
        "preferences": preference.get("preferences", {}),
        "updatedAt": preference.get("updated_at"),
    }


