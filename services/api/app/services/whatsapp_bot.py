"""
WhatsApp Business API client for AutoPro Daune.

This module provides a minimal wrapper around the WhatsApp Business
Cloud API to send outbound text messages. It relies on a Facebook
Graph access token and a phone number ID, both supplied via
environment variables or passed explicitly to the constructor.

The wrapper defines a single ``send_message`` method that sends a
message to a specified WhatsApp number. Additional message types can
be added as needed.
"""

from __future__ import annotations

import os
import requests
from typing import Optional, Dict, Any


class WhatsAppBot:
    """Client for sending messages via the WhatsApp Business API."""

    def __init__(self, access_token: Optional[str] = None, phone_number_id: Optional[str] = None, api_base: Optional[str] = None) -> None:
        self.access_token = access_token or os.getenv("WHATSAPP_ACCESS_TOKEN", "")
        self.phone_number_id = phone_number_id or os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        api_base_env = api_base or os.getenv("WHATSAPP_API_BASE", "https://graph.facebook.com/v18.0")
        self.api_base = api_base_env.rstrip("/") if api_base_env else "https://graph.facebook.com/v18.0"

        if not self.access_token:
            raise ValueError("WhatsApp access token is required")
        if not self.phone_number_id:
            raise ValueError("WhatsApp phone number ID is required")

        self.url = f"{self.api_base}/{self.phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def send_message(self, to: str, message: str) -> Dict[str, Any]:
        """Send a plain text message to a WhatsApp user.

        :param to: Destination WhatsApp number in international format
        :param message: Text body of the message
        :returns: JSON response from the API
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        response = requests.post(self.url, headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()