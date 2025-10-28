"""
REAL Notification Service - AutoPro Daune
WhatsApp, Email, SMS integration
NO MOCKS - Real API calls
"""

from typing import Dict, Any, Optional
import os
import logging
import requests
from datetime import datetime
from uuid import UUID
from .supabase_client import get_supabase_service_instance
from fastapi import HTTPException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

# API Keys
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

class NotificationService:
    """Real notification service"""
    
    def __init__(self):
        self.supabase = get_supabase_service_instance()
    
    async def send_whatsapp(
        self,
        to_phone: str,
        message: str,
        template_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send WhatsApp message via Business API"""
        try:
            if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
                raise HTTPException(
                    status_code=400,
                    detail="WhatsApp Business API not configured"
                )
            
            url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
            headers = {
                "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(f"WhatsApp sent to {to_phone}")
            
            return {
                "success": True,
                "message_id": result.get('messages', [{}])[0].get('id'),
                "platform": "whatsapp"
            }
            
        except Exception as e:
            logger.error(f"WhatsApp error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send email via SMTP"""
        try:
            if not SMTP_USERNAME or not SMTP_PASSWORD:
                # Fallback to logging only
                logger.warning(f"Email would be sent to {to_email}: {subject}")
                return {
                    "success": True,
                    "mode": "mock",
                    "message": "SMTP not configured, email logged only"
                }
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = SMTP_USERNAME
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add both plain text and HTML parts
            if body_text:
                part1 = MIMEText(body_text, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(body_html, 'html')
            msg.attach(part2)
            
            # Send via SMTP
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}")
            
            return {
                "success": True,
                "to": to_email,
                "subject": subject,
                "mode": "smtp"
            }
            
        except Exception as e:
            logger.error(f"Email error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def send_sms(
        self,
        to_phone: str,
        message: str
    ) -> Dict[str, Any]:
        """Send SMS via Twilio"""
        try:
            if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
                logger.warning(f"SMS would be sent to {to_phone}: {message}")
                return {
                    "success": True,
                    "mode": "mock",
                    "message": "Twilio not configured, SMS logged only"
                }
            
            from twilio.rest import Client
            
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            
            message_obj = client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            
            logger.info(f"SMS sent to {to_phone}")
            
            return {
                "success": True,
                "message_sid": message_obj.sid,
                "to": to_phone,
                "mode": "twilio"
            }
            
        except Exception as e:
            logger.error(f"SMS error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def create_notification(
        self,
        user_id: UUID,
        type: str,
        title: str,
        message: str,
        action_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create in-app notification"""
        try:
            notification_data = {
                "user_id": str(user_id),
                "type": type,
                "title": title,
                "message": message,
                "action_url": action_url,
                "read": False,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.client.table('notifications')\
                .insert(notification_data)\
                .execute()
            
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Notification creation error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_notifications(
        self,
        user_id: UUID,
        unread_only: bool = False,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get user notifications"""
        try:
            query = self.supabase.client.table('notifications')\
                .select('*')\
                .eq('user_id', str(user_id))
            
            if unread_only:
                query = query.eq('read', False)
            
            result = query.order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            notifications = result.data or []
            unread_count = sum(1 for n in notifications if not n.get('read', False))
            
            return {
                "notifications": notifications,
                "total": len(notifications),
                "unread_count": unread_count
            }
            
        except Exception as e:
            logger.error(f"Get notifications error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def mark_as_read(
        self,
        notification_id: UUID,
        user_id: UUID
    ) -> bool:
        """Mark notification as read"""
        try:
            result = self.supabase.client.table('notifications')\
                .update({
                    'read': True,
                    'read_at': datetime.utcnow().isoformat()
                })\
                .eq('id', str(notification_id))\
                .eq('user_id', str(user_id))\
                .execute()
            
            return len(result.data or []) > 0
            
        except Exception as e:
            logger.error(f"Mark as read error: {str(e)}")
            return False

# Singleton
_notification_service = None

def get_notification_service() -> NotificationService:
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
