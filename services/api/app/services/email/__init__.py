"""
Email Services Package
Modular email reporting and notification system
"""

from .models import (
    EmailType,
    EmailPriority, 
    EmailRecipient,
    EmailTemplate,
    EmailMessage,
    EmailConfig
)
from .templates import EmailTemplates
from .sender import EmailSender
from .reporter import EmailReporter

__all__ = [
    "EmailType",
    "EmailPriority",
    "EmailRecipient", 
    "EmailTemplate",
    "EmailMessage",
    "EmailConfig",
    "EmailTemplates",
    "EmailSender",
    "EmailReporter",
]
