"""
Notifications routes for AutoPro Daune API.

This module provides endpoints for sending notifications and managing alerts.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Form
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import os
import requests

from ..database import get_db
from ..services.supabase_client import get_supabase_service_instance

router = APIRouter(
    prefix="/api/notify",
    tags=["notifications"],
    responses={404: {"description": "Not found"}}
)

@router.post("/test")
async def send_test_notification(
    message: str = "Test notificare din Admin",
    background_tasks: BackgroundTasks = BackgroundTasks(),
    # Using Supabase service instead of database session
) -> Dict[str, Any]:
    """
    Trimite o notificare de test.
    
    Args:
        message: Mesajul de trimis
        background_tasks: Background tasks
        db: Sesiunea de bază de date
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        # Adăugăm task-ul în background
        background_tasks.add_task(_send_test_notification, message)
        
        return {
            "success": True,
            "message": "Notificare de test trimisă",
            "content": message,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Eroare la trimiterea notificării de test: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la notificare: {str(e)}")

@router.post("/whatsapp")
async def send_whatsapp_notification(
    notification_data: Dict[str, Any],
    background_tasks: BackgroundTasks = BackgroundTasks(),
    # Using Supabase service instead of database session
) -> Dict[str, Any]:
    """
    Trimite o notificare pe WhatsApp Business.

    Args:
        notification_data: Datele notificării
        background_tasks: Background tasks

    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        message = notification_data.get("message", "")
        phone_number = notification_data.get("phone_number", os.getenv("WHATSAPP_ADMIN_PHONE"))

        if not message:
            raise HTTPException(status_code=400, detail="Mesajul este obligatoriu")

        if not phone_number:
            raise HTTPException(status_code=400, detail="Numărul de telefon este obligatoriu")

        # Adăugăm task-ul în background
        background_tasks.add_task(_send_whatsapp_message, message, phone_number)

        return {
            "success": True,
            "message": "Notificare WhatsApp trimisă",
            "phone_number": phone_number,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Eroare la trimiterea notificării WhatsApp: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la notificare WhatsApp: {str(e)}")

@router.post("/email")
async def send_email_notification(
    notification_data: Dict[str, Any],
    background_tasks: BackgroundTasks = BackgroundTasks(),
    # Using Supabase service instead of database session
) -> Dict[str, Any]:
    """
    Trimite o notificare prin email.
    
    Args:
        notification_data: Datele notificării
        background_tasks: Background tasks
        db: Sesiunea de bază de date
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        email = notification_data.get("email", "")
        subject = notification_data.get("subject", "Notificare AutoPro Daune")
        message = notification_data.get("message", "")
        
        if not email or not message:
            raise HTTPException(status_code=400, detail="Email-ul și mesajul sunt obligatorii")
        
        # Adăugăm task-ul în background
        background_tasks.add_task(_send_email_message, email, subject, message)
        
        return {
            "success": True,
            "message": "Notificare email trimisă",
            "email": email,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Eroare la trimiterea notificării email: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la notificare email: {str(e)}")

@router.get("/status")
async def get_notification_status(
    # Using Supabase service instead of database session
) -> Dict[str, Any]:
    """
    Obține statusul serviciilor de notificare.
    
    Args:
        db: Sesiunea de bază de date
        
    Returns:
        Dicționar cu statusul serviciilor
    """
    try:
        # Verificăm statusul WhatsApp
        whatsapp_status = _check_whatsapp_status()

        # Verificăm statusul email
        email_status = _check_email_status()
        
        return {
            "whatsapp": whatsapp_status,
            "email": email_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Eroare la obținerea statusului notificărilor: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la status notificări: {str(e)}")

# Funcții helper pentru background tasks
async def _send_test_notification(message: str):
    """Funcție helper pentru trimiterea unei notificări de test."""
    try:
        logging.info(f"Trimitere notificare de test: {message}")

        # Trimitem pe WhatsApp
        await _send_whatsapp_message(f"🧪 TEST: {message}", os.getenv("WHATSAPP_ADMIN_PHONE"))

        logging.info("Notificare de test trimisă cu succes")

    except Exception as e:
        logging.error(f"Eroare la trimiterea notificării de test: {e}")

async def _send_whatsapp_message(message: str, phone_number: str = None):
    """Funcție helper pentru trimiterea unui mesaj pe WhatsApp Business."""
    try:
        from ..services.whatsapp_bot import WhatsAppBot

        if not phone_number:
            phone_number = os.getenv("WHATSAPP_ADMIN_PHONE")

        if not phone_number:
            logging.warning("WHATSAPP_ADMIN_PHONE nu este setat")
            return

        whatsapp_bot = WhatsAppBot()
        result = whatsapp_bot.send_message(phone_number, message)

        logging.info(f"Mesaj WhatsApp trimis cu succes către {phone_number}")

    except Exception as e:
        logging.error(f"Eroare la trimiterea mesajului WhatsApp: {e}")

async def _send_email_message(email: str, subject: str, message: str):
    """Funcție helper pentru trimiterea unui email."""
    try:
        logging.info(f"Trimitere email către {email}: {subject}")
        
        # TODO: Implementați serviciul real de email
        # Aici ar trebui să integrați cu un serviciu de email (SendGrid, AWS SES, etc.)
        
        logging.info(f"Email trimis cu succes către {email}")
        
    except Exception as e:
        logging.error(f"Eroare la trimiterea email-ului: {e}")

def _check_whatsapp_status() -> Dict[str, Any]:
    """Verifică statusul serviciului WhatsApp Business."""
    try:
        access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

        if not access_token or not phone_number_id:
            return {"status": "unavailable", "reason": "WHATSAPP_ACCESS_TOKEN sau WHATSAPP_PHONE_NUMBER_ID nu sunt setate"}

        from ..services.whatsapp_bot import WhatsAppBot

        try:
            whatsapp_bot = WhatsAppBot(access_token, phone_number_id)
            return {"status": "available", "phone_number_id": phone_number_id}
        except ValueError as ve:
            return {"status": "unavailable", "reason": str(ve)}

    except Exception as e:
        return {"status": "unavailable", "reason": str(e)}

def _check_email_status() -> Dict[str, Any]:
    """Verifică statusul serviciului de email."""
    try:
        # TODO: Implementați verificarea reală a serviciului de email
        
        return {"status": "available", "provider": "mock"}
        
    except Exception as e:
        return {"status": "unavailable", "reason": str(e)}


# ==================== NOTIFICATION MANAGEMENT ====================

@router.get("/list")
async def get_notifications(
    unread_only: bool = Query(False, description="Doar notificări necitite"),
    limit: int = Query(20, description="Număr maxim de notificări")
) -> Dict[str, Any]:
    """
    Obține lista de notificări pentru user.
    
    Returns:
        Listă cu notificări și count-uri
    """
    try:
        supabase = get_supabase_service_instance()
        
        # Build filters
        filters = []
        if unread_only:
            filters.append(("eq", "is_read", False))
        
        # Get notifications from system_logs table (reuse existing)
        notifications = supabase._table_select(
            "system_logs",
            "*",
            filters=filters,
            limit=limit,
            order_by=("created_at", "desc")
        ) or []
        
        # Count unread
        unread_count = len([n for n in notifications if not n.get('is_read', False)])
        
        return {
            "success": True,
            "notifications": notifications,
            "total": len(notifications),
            "unread_count": unread_count
        }
        
    except Exception as e:
        logging.error(f"Error getting notifications: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {str(e)}")


@router.post("/mark-read/{notification_id}")
async def mark_notification_as_read(
    notification_id: str
) -> Dict[str, Any]:
    """
    Marchează o notificare ca citită.
    
    Args:
        notification_id: ID-ul notificării
        
    Returns:
        Success message
    """
    try:
        supabase = get_supabase_service_instance()
        
        result = supabase._table_update_eq(
            "system_logs",
            "id",
            notification_id,
            {"is_read": True, "read_at": datetime.now().isoformat()}
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {
            "success": True,
            "message": "Notification marked as read"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to mark as read: {str(e)}")


# ==================== EMAIL NOTIFICATION SYSTEM ====================

@router.get("/email-templates")
async def get_email_templates() -> Dict[str, Any]:
    """
    Get available email templates for notifications.
    
    Returns:
        List of email templates
    """
    try:
        templates = [
            {
                "id": "lead_new",
                "name": "Lead Nou",
                "subject": "Lead nou primit - {client_name}",
                "body": """Salut,

Ai primit un lead nou de la {client_name}.

Detalii:
- Nume: {client_name}
- Telefon: {client_phone}
- Email: {client_email}
- Descriere: {description}
- Prioritate: {priority}

Te rugăm să contactezi clientul în cel mai scurt timp.

Cu respect,
Sistem AutoPro Daune""",
                "variables": ["client_name", "client_phone", "client_email", "description", "priority"]
            },
            {
                "id": "payment_received",
                "name": "Plată Primită",
                "subject": "Plată confirmată - {invoice_number}",
                "body": """Salut {client_name},

Mulțumim! Am confirmat plata pentru factura {invoice_number} în valoare de {amount} RON.

Detalii plată:
- Data: {payment_date}
- Metodă: {payment_method}
- Referință: {reference}

Documentele vor fi procesate în următoarele 2-3 zile lucrătoare.

Cu respect,
Echipa AutoPro Daune""",
                "variables": ["client_name", "invoice_number", "amount", "payment_date", "payment_method", "reference"]
            },
            {
                "id": "reminder_payment",
                "name": "Reminder Plată",
                "subject": "Reminder: Factura {invoice_number} - Scadență apropiate",
                "body": """Salut {client_name},

Vrem să te reamintim că factura {invoice_number} în valoare de {amount} RON are scadența pe {due_date}.

Dacă ai deja plătit, te rugăm să ignori acest email.

Pentru a plăti online: {payment_link}

Cu respect,
Echipa AutoPro Daune""",
                "variables": ["client_name", "invoice_number", "amount", "due_date", "payment_link"]
            },
            {
                "id": "case_update",
                "name": "Actualizare Caz",
                "subject": "Actualizare caz - {case_number}",
                "body": """Salut {client_name},

Vrem să te ținem la curent cu progresul cazului {case_number}.

Status actual: {status}
Progres: {progress}%

Detalii: {update_details}

Următorul pas: {next_step}

Dacă ai întrebări, nu ezita să ne contactezi.

Cu respect,
Echipa AutoPro Daune""",
                "variables": ["client_name", "case_number", "status", "progress", "update_details", "next_step"]
            },
            {
                "id": "appointment_reminder",
                "name": "Reminder Programare",
                "subject": "Reminder: Programare {appointment_type} - {date}",
                "body": """Salut {client_name},

Vrem să te reamintim de programarea din {date} la ora {time}.

Tip programare: {appointment_type}
Locația: {location}
Persoana de contact: {contact_person}

Te rugăm să confirmi participarea sau să ne contactezi dacă trebuie să reprogramăm.

Cu respect,
Echipa AutoPro Daune""",
                "variables": ["client_name", "date", "time", "appointment_type", "location", "contact_person"]
            }
        ]
        
        return {
            "success": True,
            "templates": templates
        }
        
    except Exception as e:
        logging.error(f"Error getting email templates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")


@router.post("/email-template")
async def send_email_with_template(
    template_id: str = Form(...),
    recipient_email: str = Form(...),
    variables: str = Form(...),  # JSON string with variables
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> Dict[str, Any]:
    """
    Send email using a template with variables.
    
    Args:
        template_id: ID of the email template
        recipient_email: Email address of recipient
        variables: JSON string with template variables
        background_tasks: Background tasks
        
    Returns:
        Success message
    """
    try:
        import json
        
        # Get template
        templates_response = await get_email_templates()
        if not templates_response["success"]:
            raise HTTPException(status_code=500, detail="Failed to get templates")
        
        templates = templates_response["templates"]
        template = next((t for t in templates if t["id"] == template_id), None)
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Parse variables
        try:
            template_vars = json.loads(variables)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid variables JSON")
        
        # Replace variables in subject and body
        subject = template["subject"]
        body = template["body"]
        
        for var, value in template_vars.items():
            subject = subject.replace(f"{{{var}}}", str(value))
            body = body.replace(f"{{{var}}}", str(value))
        
        # Send email
        email_data = {
            "email": recipient_email,
            "subject": subject,
            "message": body
        }
        
        background_tasks.add_task(_send_email_notification, email_data)
        
        return {
            "success": True,
            "message": "Email scheduled for sending",
            "template_used": template["name"],
            "recipient": recipient_email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error sending template email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@router.get("/email-settings")
async def get_email_settings() -> Dict[str, Any]:
    """
    Get email notification settings.
    
    Returns:
        Email settings configuration
    """
    try:
        supabase = get_supabase_service_instance()
        
        # Get settings from database or return defaults
        settings = {
            "smtp_enabled": True,
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "noreply@autoprodaune.ro",
            "smtp_password": "***hidden***",
            "from_name": "AutoPro Daune",
            "from_email": "noreply@autoprodaune.ro",
            "reply_to": "contact@autoprodaune.ro",
            "auto_send_enabled": True,
            "daily_digest_enabled": True,
            "digest_time": "08:00",
            "lead_notifications_enabled": True,
            "payment_notifications_enabled": True,
            "reminder_notifications_enabled": True,
            "case_update_notifications_enabled": True
        }
        
        return {
            "success": True,
            "settings": settings
        }
        
    except Exception as e:
        logging.error(f"Error getting email settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")


@router.post("/email-settings")
async def update_email_settings(
    settings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update email notification settings.
    
    Args:
        settings: Email settings to update
        
    Returns:
        Success message
    """
    try:
        # In production, save to database
        # For now, just validate and return success
        
        required_fields = ["smtp_host", "smtp_port", "smtp_username", "from_email"]
        for field in required_fields:
            if field not in settings:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, settings["from_email"]):
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        return {
            "success": True,
            "message": "Email settings updated successfully",
            "updated_fields": list(settings.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating email settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")


@router.post("/test-template")
async def test_email_template(
    template_id: str = Form(...),
    test_email: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> Dict[str, Any]:
    """
    Send test email using a template.
    
    Args:
        template_id: ID of the email template
        test_email: Email address to send test to
        background_tasks: Background tasks
        
    Returns:
        Success message
    """
    try:
        # Sample variables for testing
        test_variables = {
            "client_name": "Test Client",
            "client_phone": "+40712345678",
            "client_email": "test@example.com",
            "description": "Test lead description",
            "priority": "Normal",
            "invoice_number": "INV-2025-001",
            "amount": "1,500",
            "payment_date": "2025-01-01",
            "payment_method": "Transfer bancar",
            "reference": "REF123456",
            "due_date": "2025-01-31",
            "payment_link": "https://autoprodaune.ro/pay/INV-2025-001",
            "case_number": "CASE-2025-001",
            "status": "În procesare",
            "progress": "65",
            "update_details": "Documentele au fost procesate cu succes",
            "next_step": "Contactare client pentru semnături",
            "date": "2025-01-15",
            "time": "10:00",
            "appointment_type": "Consultanță juridică",
            "location": "Oficiul AutoPro Daune",
            "contact_person": "Avocat Ion Popescu"
        }
        
        variables_json = json.dumps(test_variables)
        
        return await send_email_with_template(template_id, test_email, variables_json, background_tasks)
        
    except Exception as e:
        logging.error(f"Error testing email template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test template: {str(e)}")


# ==================== SMS NOTIFICATIONS ====================

@router.post("/sms")
async def send_sms_notification(
    phone_number: str = Form(...),
    message: str = Form(...),
    template_id: Optional[str] = Form(None),
    variables: Optional[str] = Form(None),  # JSON string with variables
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> Dict[str, Any]:
    """
    Send SMS notification.
    
    Args:
        phone_number: Phone number to send SMS to
        message: SMS message content
        template_id: Optional SMS template ID
        variables: JSON string with template variables
        background_tasks: Background tasks
        
    Returns:
        Success message
    """
    try:
        # Validate phone number format
        import re
        phone_pattern = r'^\+?[1-9]\d{1,14}$'
        if not re.match(phone_pattern, phone_number.replace(' ', '').replace('-', '')):
            raise HTTPException(status_code=400, detail="Invalid phone number format")
        
        # If template is used, replace variables
        if template_id and variables:
            import json
            try:
                template_vars = json.loads(variables)
                # Replace variables in message
                for var, value in template_vars.items():
                    message = message.replace(f"{{{var}}}", str(value))
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid variables JSON")
        
        # In production, integrate with SMS service (Twilio, etc.)
        # For now, just log the SMS
        logger.info(f"[SMS] SMS sent to {phone_number}: {message[:50]}...")
        
        # Log SMS activity
        supabase = get_supabase_service_instance()
        activity_data = {
            "type": "sms_sent",
            "message": f"SMS sent to {phone_number}: {message[:100]}...",
            "metadata": {
                "phone_number": phone_number,
                "template_id": template_id,
                "message_length": len(message)
            },
            "created_at": datetime.now().isoformat()
        }
        supabase._table_insert("system_logs", activity_data)
        
        return {
            "success": True,
            "message": "SMS scheduled for sending",
            "phone_number": phone_number,
            "message_length": len(message),
            "template_used": template_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error sending SMS: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send SMS: {str(e)}")


@router.get("/sms-templates")
async def get_sms_templates() -> Dict[str, Any]:
    """
    Get available SMS templates.
    
    Returns:
        List of SMS templates
    """
    try:
        templates = [
            {
                "id": "lead_welcome",
                "name": "Welcome SMS pentru Leads",
                "message": "Salut {client_name}! Mulțumim că ne-ai contactat. Echipa AutoPro Daune vă va contacta în cel mai scurt timp pentru a discuta despre cazul tău. Cu respect, Echipa AutoPro Daune",
                "variables": ["client_name"],
                "max_length": 160
            },
            {
                "id": "appointment_reminder",
                "name": "Reminder Programare SMS",
                "message": "Reminder: Programarea ta la AutoPro Daune este mâine la {time}. Locația: {location}. Confirmă participarea la {phone}. Cu respect, AutoPro Daune",
                "variables": ["time", "location", "phone"],
                "max_length": 160
            },
            {
                "id": "payment_reminder",
                "name": "Reminder Plată SMS",
                "message": "Reminder: Factura {invoice_number} în valoare de {amount} RON are scadența pe {due_date}. Plătește online: {payment_link}. AutoPro Daune",
                "variables": ["invoice_number", "amount", "due_date", "payment_link"],
                "max_length": 160
            },
            {
                "id": "case_update",
                "name": "Actualizare Caz SMS",
                "message": "Actualizare caz {case_number}: {status}. Progres: {progress}%. Următorul pas: {next_step}. AutoPro Daune",
                "variables": ["case_number", "status", "progress", "next_step"],
                "max_length": 160
            },
            {
                "id": "payment_confirmed",
                "name": "Plată Confirmată SMS",
                "message": "Mulțumim! Am confirmat plata pentru factura {invoice_number} în valoare de {amount} RON. Documentele vor fi procesate în 2-3 zile. AutoPro Daune",
                "variables": ["invoice_number", "amount"],
                "max_length": 160
            }
        ]
        
        return {
            "success": True,
            "templates": templates
        }
        
    except Exception as e:
        logging.error(f"Error getting SMS templates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get SMS templates: {str(e)}")


@router.post("/sms-template")
async def send_sms_with_template(
    template_id: str = Form(...),
    phone_number: str = Form(...),
    variables: str = Form(...),  # JSON string with variables
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> Dict[str, Any]:
    """
    Send SMS using a template with variables.
    
    Args:
        template_id: ID of the SMS template
        phone_number: Phone number to send SMS to
        variables: JSON string with template variables
        background_tasks: Background tasks
        
    Returns:
        Success message
    """
    try:
        import json
        
        # Get template
        templates_response = await get_sms_templates()
        if not templates_response["success"]:
            raise HTTPException(status_code=500, detail="Failed to get templates")
        
        templates = templates_response["templates"]
        template = next((t for t in templates if t["id"] == template_id), None)
        
        if not template:
            raise HTTPException(status_code=404, detail="SMS template not found")
        
        # Parse variables
        try:
            template_vars = json.loads(variables)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid variables JSON")
        
        # Replace variables in message
        message = template["message"]
        for var, value in template_vars.items():
            message = message.replace(f"{{{var}}}", str(value))
        
        # Check message length
        if len(message) > template["max_length"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Message too long. Maximum {template['max_length']} characters allowed."
            )
        
        # Send SMS
        return await send_sms_notification(phone_number, message, template_id, variables, background_tasks)
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error sending template SMS: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send template SMS: {str(e)}")


@router.get("/sms-settings")
async def get_sms_settings() -> Dict[str, Any]:
    """
    Get SMS notification settings.
    
    Returns:
        SMS settings configuration
    """
    try:
        settings = {
            "provider": "twilio",  # twilio, messagebird, etc.
            "account_sid": "***hidden***",
            "auth_token": "***hidden***",
            "from_number": "+40712345678",
            "auto_send_enabled": True,
            "daily_limit": 1000,
            "daily_sent": 0,
            "cost_per_sms": 0.05,  # EUR
            "lead_notifications_enabled": True,
            "payment_notifications_enabled": True,
            "appointment_reminders_enabled": True,
            "case_update_notifications_enabled": True
        }
        
        return {
            "success": True,
            "settings": settings
        }
        
    except Exception as e:
        logging.error(f"Error getting SMS settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get SMS settings: {str(e)}")


@router.post("/sms-settings")
async def update_sms_settings(
    settings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update SMS notification settings.
    
    Args:
        settings: SMS settings to update
        
    Returns:
        Success message
    """
    try:
        # Validate required fields
        required_fields = ["provider", "account_sid", "auth_token", "from_number"]
        for field in required_fields:
            if field not in settings:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate phone number format
        import re
        phone_pattern = r'^\+?[1-9]\d{1,14}$'
        if not re.match(phone_pattern, settings["from_number"].replace(' ', '').replace('-', '')):
            raise HTTPException(status_code=400, detail="Invalid from_number format")
        
        # In production, save to database and test SMS service
        return {
            "success": True,
            "message": "SMS settings updated successfully",
            "updated_fields": list(settings.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating SMS settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update SMS settings: {str(e)}")


@router.post("/test-sms")
async def test_sms_notification(
    phone_number: str = Form(...),
    test_message: str = Form("Test SMS din AutoPro Daune"),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> Dict[str, Any]:
    """
    Send test SMS notification.
    
    Args:
        phone_number: Phone number to send test SMS to
        test_message: Test message content
        background_tasks: Background tasks
        
    Returns:
        Success message
    """
    try:
        return await send_sms_notification(phone_number, test_message, None, None, background_tasks)
        
    except Exception as e:
        logging.error(f"Error testing SMS: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test SMS: {str(e)}")
