"""
WhatsApp Business webhook and outbound messaging routes for AutoPro Daune API.

These endpoints integrate the WhatsApp Business API with the rest of
the system. Incoming messages are accepted via the ``/webhook``
endpoint and can be parsed to create leads or referrals in the
database. Outgoing messages can be sent via the ``/send`` endpoint
using the ``WhatsAppBot`` wrapper.

The webhook payload format follows the structure documented by
Facebook's Graph API for WhatsApp. If the payload cannot be parsed
the message is ignored. You should configure your Meta App's
Webhook URL to point to this endpoint.
"""

from __future__ import annotations

from fastapi import APIRouter, Request, HTTPException, Body
from typing import Dict, Any
import logging
import json

from ..services.whatsapp_bot import WhatsAppBot
from ..services.supabase_client import supabase_service

router = APIRouter(
    prefix="/api/whatsapp",
    tags=["whatsapp"],
    responses={404: {"description": "Not found"}},
)


async def _safe_json(request: Request):
    """Întoarce payload-ul ca dict. Acceptă JSON veritabil sau string JSON."""
    try:
        data = await request.json()
    except Exception:
        body = await request.body()
        try:
            data = json.loads(body.decode("utf-8", errors="ignore"))
        except Exception as exc:
            logging.error(f"Failed to parse WhatsApp webhook payload: {exc}")
            return None

    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception as exc:
            logging.error(f"Payload is string but not JSON: {exc}")
            return None
    return data or {}


@router.post("/webhook")
async def whatsapp_webhook(request: Request) -> dict:
    """Handle incoming WhatsApp webhook events."""
    data = await _safe_json(request)
    if not isinstance(data, dict):
        # răspunde 200 ca să nu reîncerce Facebook, dar loghează
        logging.error("Webhook payload not dict; skipping lead creation/ack")
        return {"success": True, "note": "ignored non-JSON payload"}

    try:
        entry = (data.get("entry") or [{}])[0]
        changes = (entry.get("changes") or [{}])[0]
        value = changes.get("value") or {}
        messages = value.get("messages") or []
        contacts = value.get("contacts") or []

        from_number = messages[0]["from"] if messages else None
        text_body = (messages[0].get("text") or {}).get("body") if messages else None
        contact_name = (contacts[0].get("profile") or {}).get("name") if contacts else "WhatsApp User"

        if not from_number or not text_body:
            return {"success": True, "note": "no message content"}

        # Create a new lead in Supabase
        try:
            supabase_service.lead_create({
                "name": contact_name,
                "phone": from_number,
                "details": text_body,
                "source": "whatsapp",
            })
        except Exception as e:
            logging.warning(f"Error creating lead from WhatsApp message: {e}")

        # ACK non-blocking
        try:
            bot = WhatsAppBot()
            if from_number:
                bot.send_message(to=from_number, message="✅ Am primit mesajul tău. Revenim în scurt timp.")
        except Exception as e:
            logging.warning(f"Failed to send WhatsApp acknowledgement: {e}")

        return {"success": True}
    except Exception as exc:
        logging.error(f"Unexpected error handling WhatsApp webhook: {exc}")
        return {"success": True, "note": "handled with warnings"}  # păstrează 200


@router.post("/send")
async def whatsapp_send(data: dict = Body(...)) -> dict:
    """
    Send an outbound WhatsApp message to a user.
    
    Body minim: {"to":"+407...","message":"text"}
    """
    to = data.get("to")
    message = data.get("message")
    if not to or not message:
        raise HTTPException(status_code=400, detail="Missing 'to' or 'message'")

    try:
        bot = WhatsAppBot()
        resp = bot.send_message(to=to, message=message)
        return {"success": True, "response": resp}
    except Exception as http_err:
        # propagă statusul real de la Graph (ex: 401/400)
        import requests
        if isinstance(http_err, requests.HTTPError):
            status = http_err.response.status_code if http_err.response is not None else 502
            logging.error(f"Failed to send WhatsApp message: {http_err}")
            raise HTTPException(status_code=status, detail=http_err.response.text if http_err.response is not None else str(http_err))
        else:
            logging.error(f"Failed to send WhatsApp message: {http_err}")
            raise HTTPException(status_code=500, detail="Internal error while sending WhatsApp message")