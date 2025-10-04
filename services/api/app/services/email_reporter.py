"""
Email Reporter - Wrapper compatibil pentru sistemul modular
"""

from .email import (
    EmailReporter,
    EmailType,
    EmailPriority,
    EmailRecipient,
    EmailTemplate,
    EmailMessage,
    EmailConfig
)

# Singleton instance
_email_reporter = None

def get_email_reporter() -> EmailReporter:
    """Returnează instanța singleton a EmailReporter"""
    global _email_reporter
    if _email_reporter is None:
        _email_reporter = EmailReporter()
    return _email_reporter

# Funcții helper pentru trimiterea rapidă
async def send_daily_report_email(report_data: dict) -> bool:
    """
    Funcție helper pentru trimiterea raportului zilnic
    
    Args:
        report_data: Datele pentru raport
        
    Returns:
        True dacă email-ul a fost trimis cu succes
    """
    reporter = get_email_reporter()
    return await reporter.send_daily_report(report_data)

async def send_alert_email(alert_data: dict) -> bool:
    """
    Funcție helper pentru trimiterea alertei
    
    Args:
        alert_data: Datele pentru alertă
        
    Returns:
        True dacă email-ul a fost trimis cu succes
    """
    reporter = get_email_reporter()
    return await reporter.send_alert(alert_data)

__all__ = [
    "EmailReporter",
    "EmailType", 
    "EmailPriority",
    "EmailRecipient",
    "EmailTemplate", 
    "EmailMessage",
    "EmailConfig",
    "get_email_reporter",
    "send_daily_report_email",
    "send_alert_email"
]
