"""High level helpers for sending transactional emails related to leads."""
from __future__ import annotations

import logging
from typing import Iterable, Optional

from .email import (
    EmailConfig,
    EmailMessage,
    EmailPriority,
    EmailRecipient,
    EmailSender,
    EmailType,
)

logger = logging.getLogger(__name__)


class EmailService:
    """Wrapper around :class:`EmailSender` with lead specific helpers."""

    def __init__(self) -> None:
        self._config = EmailConfig()
        self._sender = EmailSender(self._config)

    async def send_assignment_notification(
        self,
        *,
        lead_name: str,
        lead_id: str,
        assigned_to: str,
        assignee_email: Optional[str],
        assigned_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> bool:
        """Notify the assignee that a new lead was allocated to them."""

        if not assignee_email:
            logger.debug("Assignment notification skipped because no email was provided")
            return False

        subject = f"Ai primit un lead nou - {lead_name or 'Lead fără nume'}"
        assigned_by_label = assigned_by or "sistem"
        text_content = (
            f"Salut {assigned_to},\n\n"
            f"Lead-ul \"{lead_name or 'N/A'}\" (ID: {lead_id}) a fost asignat către tine de {assigned_by_label}.\n"
        )
        if notes:
            text_content += f"\nNotițe: {notes}\n"
        text_content += "\nSucces!\nAutoPro Daune"

        html_content = (
            f"<p>Salut <strong>{assigned_to}</strong>,</p>"
            f"<p>Lead-ul <strong>{lead_name or 'N/A'}</strong> (ID: {lead_id}) a fost asignat către tine de {assigned_by_label}.</p>"
        )
        if notes:
            html_content += f"<p><strong>Notițe:</strong> {notes}</p>"
        html_content += "<p>Succes!<br/>AutoPro Daune</p>"

        message = EmailMessage(
            to=[EmailRecipient(email=assignee_email, name=assigned_to or assignee_email)],
            subject=subject,
            text_content=text_content,
            html_content=html_content,
            email_type=EmailType.ALERT,
            priority=EmailPriority.HIGH,
        )

        logger.debug(
            "Sending assignment notification for lead %s to %s", lead_id, assignee_email
        )
        return await self._sender.send_email(message)

    async def send_status_change_notification(
        self,
        *,
        lead_name: str,
        lead_id: str,
        previous_status: Optional[str],
        new_status: str,
        recipients: Iterable[str],
    ) -> bool:
        """Notify stakeholders that a lead changed its status."""

        recipient_list = [EmailRecipient(email=email, name=email) for email in recipients if email]
        if not recipient_list:
            logger.debug("Skipping status change notification – no recipients provided")
            return False

        subject = f"Lead {lead_name or lead_id} a trecut la statusul '{new_status}'"
        text_content = (
            f"Salut,\n\nLead-ul '{lead_name or lead_id}' (ID: {lead_id}) a fost actualizat la statusul "
            f"'{new_status}'."
        )
        if previous_status:
            text_content += f" Status anterior: {previous_status}."
        text_content += "\n\nEchipa AutoPro Daune"

        html_content = (
            f"<p>Salut,</p><p>Lead-ul <strong>{lead_name or lead_id}</strong> (ID: {lead_id}) a fost actualizat "
            f"la statusul <strong>{new_status}</strong>.</p>"
        )
        if previous_status:
            html_content += f"<p>Status anterior: <strong>{previous_status}</strong></p>"
        html_content += "<p>Echipa AutoPro Daune</p>"

        message = EmailMessage(
            to=recipient_list,
            subject=subject,
            text_content=text_content,
            html_content=html_content,
            email_type=EmailType.ALERT,
            priority=EmailPriority.NORMAL,
        )

        logger.debug(
            "Sending status change notification for lead %s to %s", lead_id, [r.email for r in recipient_list]
        )
        return await self._sender.send_email(message)

    async def send_attachment_notification(
        self,
        *,
        lead_name: str,
        lead_id: str,
        file_name: str,
        recipients: Iterable[str],
    ) -> bool:
        """Notify that a new attachment has been uploaded for a lead."""

        recipient_list = [EmailRecipient(email=email, name=email) for email in recipients if email]
        if not recipient_list:
            logger.debug("Skipping attachment notification – no recipients provided")
            return False

        subject = f"Lead {lead_name or lead_id}: fișier nou încărcat"
        text_content = (
            f"Salut,\n\nA fost încărcat fișierul '{file_name}' pentru lead-ul {lead_name or lead_id} (ID: {lead_id})."
            "\n\nEchipa AutoPro Daune"
        )
        html_content = (
            f"<p>Salut,</p>"
            f"<p>A fost încărcat fișierul <strong>{file_name}</strong> pentru lead-ul "
            f"<strong>{lead_name or lead_id}</strong> (ID: {lead_id}).</p>"
            "<p>Echipa AutoPro Daune</p>"
        )

        message = EmailMessage(
            to=recipient_list,
            subject=subject,
            text_content=text_content,
            html_content=html_content,
            email_type=EmailType.ALERT,
            priority=EmailPriority.NORMAL,
        )

        logger.debug(
            "Sending attachment notification for lead %s to %s", lead_id, [r.email for r in recipient_list]
        )
        return await self._sender.send_email(message)


def get_email_service() -> EmailService:
    """Return a singleton instance for re-use across requests."""

    global _email_service
    try:
        service = _email_service
    except NameError:  # pragma: no cover - executed only once
        service = None

    if service is None:
        service = EmailService()
        _email_service = service
    return service
