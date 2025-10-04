"""
Email Models - Data structures for email system
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class EmailType(Enum):
    """Tipurile de email-uri"""
    DAILY_REPORT = "daily_report"
    WEEKLY_REPORT = "weekly_report"
    MONTHLY_REPORT = "monthly_report"
    ALERT = "alert"
    SUMMARY = "summary"
    CUSTOM = "custom"


class EmailPriority(Enum):
    """Prioritatea email-urilor"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class EmailRecipient:
    """Reprezentarea unui destinatar"""
    email: str
    name: str
    role: str = "user"
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {
                "receive_reports": True,
                "receive_alerts": True,
                "report_frequency": "daily",
                "preferred_format": "html"
            }


@dataclass
class EmailTemplate:
    """Template pentru email-uri"""
    id: str
    subject: str
    html_body: str
    text_body: str
    email_type: EmailType
    variables: List[str] = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = []


@dataclass
class EmailMessage:
    """Reprezentarea unui mesaj email"""
    to: List[EmailRecipient]
    cc: List[EmailRecipient] = None
    bcc: List[EmailRecipient] = None
    subject: str = ""
    html_content: str = ""
    text_content: str = ""
    attachments: List[str] = None
    priority: EmailPriority = EmailPriority.NORMAL
    email_type: EmailType = EmailType.CUSTOM
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.cc is None:
            self.cc = []
        if self.bcc is None:
            self.bcc = []
        if self.attachments is None:
            self.attachments = []
        if self.metadata is None:
            self.metadata = {}


class EmailConfig:
    """Configurația pentru email"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        self.from_name = os.getenv("FROM_NAME", "AutoPro Daune")
        
        # Configurații pentru rate limiting
        self.max_emails_per_hour = int(os.getenv("MAX_EMAILS_PER_HOUR", "100"))
        self.max_emails_per_day = int(os.getenv("MAX_EMAILS_PER_DAY", "1000"))
