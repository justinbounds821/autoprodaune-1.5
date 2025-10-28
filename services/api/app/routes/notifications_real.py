"""
REAL Notification Routes - AutoPro Daune
WhatsApp, Email, SMS, In-app notifications
"""

from fastapi import APIRouter, Depends
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from ..middleware.jwt_auth import get_current_user, CurrentUser
from ..services.notification_service_real import get_notification_service, NotificationService

router = APIRouter(prefix="/api/notifications", tags=["notifications-real"])

class WhatsAppRequest(BaseModel):
    to_phone: str
    message: str

class EmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    body_html: str
    body_text: Optional[str] = None

class SMSRequest(BaseModel):
    to_phone: str
    message: str

class NotificationCreate(BaseModel):
    type: str
    title: str
    message: str
    action_url: Optional[str] = None

@router.post("/whatsapp")
async def send_whatsapp(
    request: WhatsAppRequest,
    current_user: CurrentUser = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Send WhatsApp message - REAL Business API"""
    return await notification_service.send_whatsapp(
        to_phone=request.to_phone,
        message=request.message
    )

@router.post("/email")
async def send_email(
    request: EmailRequest,
    current_user: CurrentUser = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Send email - REAL SMTP"""
    return await notification_service.send_email(
        to_email=request.to_email,
        subject=request.subject,
        body_html=request.body_html,
        body_text=request.body_text
    )

@router.post("/sms")
async def send_sms(
    request: SMSRequest,
    current_user: CurrentUser = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Send SMS - REAL Twilio API"""
    return await notification_service.send_sms(
        to_phone=request.to_phone,
        message=request.message
    )

@router.post("/create")
async def create_notification(
    request: NotificationCreate,
    current_user: CurrentUser = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Create in-app notification"""
    return await notification_service.create_notification(
        user_id=current_user.id,
        type=request.type,
        title=request.title,
        message=request.message,
        action_url=request.action_url
    )

@router.get("")
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user: CurrentUser = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Get user notifications"""
    return await notification_service.get_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit
    )

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Mark notification as read"""
    success = await notification_service.mark_as_read(
        notification_id=notification_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"success": True, "message": "Notification marked as read"}
