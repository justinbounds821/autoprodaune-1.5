"""Notification service with email, SMS and preference management."""

from __future__ import annotations

import asyncio
import logging
import os
import smtplib
from contextlib import contextmanager
from email.message import EmailMessage
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

try:  # pragma: no cover - optional dependency
    from twilio.base.exceptions import TwilioRestException
    from twilio.rest import Client as TwilioClient
except Exception:  # pragma: no cover - import guard
    TwilioClient = None
    TwilioRestException = Exception

from ..models.automation import NotificationPreference

logger = logging.getLogger(__name__)


class NotificationService:
    """Service responsible for delivering email/SMS and storing preferences."""

    def __init__(self, db: Session, smtp_settings: Optional[Dict[str, Any]] = None):
        self.db = db
        self.smtp_settings = smtp_settings or {
            "host": os.getenv("SMTP_HOST", "localhost"),
            "port": int(os.getenv("SMTP_PORT", "25")),
            "username": os.getenv("SMTP_USERNAME"),
            "password": os.getenv("SMTP_PASSWORD"),
            "use_tls": os.getenv("SMTP_USE_TLS", "false").lower() in {"1", "true", "yes"},
            "from_email": os.getenv("SMTP_FROM_EMAIL", "noreply@autoprodaune.local"),
        }
        self._twilio_client: Optional[TwilioClient] = None

        if TwilioClient and os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN"):
            try:
                self._twilio_client = TwilioClient(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
                logger.info("Twilio client initializat")
            except Exception as exc:  # pragma: no cover - runtime config errors
                logger.warning("Nu s-a putut inițializa Twilio client: %s", exc)

    # ------------------------------------------------------------------
    # Preference management
    # ------------------------------------------------------------------
    def list_preferences(self, user_id: str) -> List[Dict[str, Any]]:
        preferences = (
            self.db.query(NotificationPreference)
            .filter(NotificationPreference.user_id == user_id)
            .order_by(NotificationPreference.channel)
            .all()
        )
        return [pref.as_dict() for pref in preferences]

    def upsert_preference(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        preference = (
            self.db.query(NotificationPreference)
            .filter(
                NotificationPreference.user_id == payload["user_id"],
                NotificationPreference.channel == payload["channel"],
            )
            .first()
        )

        if preference is None:
            preference = NotificationPreference(**payload)
            self.db.add(preference)
        else:
            for key, value in payload.items():
                setattr(preference, key, value)

        self.db.commit()
        self.db.refresh(preference)
        return preference.as_dict()

    def delete_preference(self, user_id: str, channel: str) -> None:
        preference = (
            self.db.query(NotificationPreference)
            .filter(
                NotificationPreference.user_id == user_id,
                NotificationPreference.channel == channel,
            )
            .first()
        )
        if preference:
            self.db.delete(preference)
            self.db.commit()

    # ------------------------------------------------------------------
    # Email helpers
    # ------------------------------------------------------------------
    async def send_email_async(self, data: Dict[str, Any]) -> None:
        recipients = self._resolve_recipients(data)
        if not recipients:
            logger.info("Nu există destinatari email pentru notificare")
            return

        payload = dict(data)
        await asyncio.get_event_loop().run_in_executor(
            None, self.send_email, payload, recipients
        )

    def send_email(self, data: Dict[str, Any], recipients: Optional[List[str]] = None) -> None:
        recipients = recipients or self._resolve_recipients(data)
        if not recipients:
            logger.info("Nu există destinatari email pentru notificare")
            return

        message = EmailMessage()
        message["Subject"] = data.get("subject", "Notificare AutoPro Daune")
        message["From"] = data.get("from_email", self.smtp_settings.get("from_email"))
        message["To"] = ", ".join(recipients)
        body = data.get("body") or data.get("message") or ""
        if data.get("html"):
            message.add_alternative(data["html"], subtype="html")
            if body:
                message.set_content(body)
        else:
            message.set_content(body)

        with self._smtp_connection() as server:
            server.send_message(message)
            logger.info("Email trimis către %s", recipients)

    @contextmanager
    def _smtp_connection(self):
        host = self.smtp_settings["host"]
        port = self.smtp_settings["port"]
        use_tls = self.smtp_settings["use_tls"]

        server = smtplib.SMTP(host, port, timeout=30)
        try:
            if use_tls:
                server.starttls()
            if self.smtp_settings.get("username"):
                server.login(self.smtp_settings["username"], self.smtp_settings.get("password"))
            yield server
        finally:
            try:
                server.quit()
            except Exception:  # pragma: no cover - defensive
                server.close()

    # ------------------------------------------------------------------
    # SMS helpers
    # ------------------------------------------------------------------
    async def send_sms_async(self, data: Dict[str, Any]) -> None:
        await asyncio.get_event_loop().run_in_executor(None, self.send_sms, data)

    def send_sms(self, data: Dict[str, Any]) -> None:
        if not self._twilio_client:
            logger.warning("Twilio nu este configurat, SMS-urile nu pot fi trimise")
            return

        from_number = data.get("from") or os.getenv("TWILIO_PHONE_NUMBER")
        to_number = data.get("to") or data.get("phone") or data.get("phone_number")
        body = data.get("body") or data.get("message")

        if not to_number or not body:
            logger.warning("SMS invalid - lipsesc destinația sau mesajul")
            return

        try:
            self._twilio_client.messages.create(body=body, from_=from_number, to=to_number)
            logger.info("SMS trimis către %s", to_number)
        except TwilioRestException as exc:  # pragma: no cover - depends on Twilio
            logger.error("Eroare la trimiterea SMS-ului: %s", exc)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _resolve_recipients(self, data: Dict[str, Any]) -> List[str]:
        explicit = data.get("to") or data.get("email")
        if isinstance(explicit, str):
            return [explicit]
        if isinstance(explicit, list):
            return explicit

        user_id = data.get("user_id")
        if not user_id:
            fallback = os.getenv("ADMIN_NOTIFICATION_EMAIL")
            return [fallback] if fallback else []

        preferences = (
            self.db.query(NotificationPreference)
            .filter(
                NotificationPreference.user_id == user_id,
                NotificationPreference.channel == "email",
                NotificationPreference.enabled.is_(True),
            )
            .all()
        )
        return [pref.destination for pref in preferences if pref.destination]

    def notify_admins(self, title: str, message: str) -> None:
        admin_email = os.getenv("ADMIN_NOTIFICATION_EMAIL")
        if admin_email:
            try:
                self.send_email({"to": admin_email, "subject": title, "body": message})
            except Exception:  # pragma: no cover - defensive
                logger.exception("Nu s-a putut trimite notificarea de eroare către admin")


__all__ = ["NotificationService"]

