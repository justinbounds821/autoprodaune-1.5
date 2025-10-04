"""
Email Reporter - Main orchestrator for email operations
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .models import EmailConfig, EmailRecipient, EmailMessage, EmailType, EmailPriority
from .templates import EmailTemplates
from .sender import EmailSender

logger = logging.getLogger(__name__)


class EmailReporter:
    """Reporter principal pentru email-uri"""
    
    def __init__(self):
        self.config = EmailConfig()
        self.templates = EmailTemplates()
        self.sender = EmailSender(self.config)
        self.recipients = self._load_recipients()
        self.email_queue = []
        
    def _load_recipients(self) -> List[EmailRecipient]:
        """Încarcă lista de destinatari"""
        # În implementarea reală, ar citi din baza de date
        # Aici simulăm cu date
        return [
            EmailRecipient(
                email="admin@autoprodane.ro",
                name="Administrator",
                role="admin",
                preferences={
                    "receive_reports": True,
                    "receive_alerts": True,
                    "report_frequency": "daily",
                    "preferred_format": "html"
                }
            ),
            EmailRecipient(
                email="manager@autoprodane.ro",
                name="Manager",
                role="manager",
                preferences={
                    "receive_reports": True,
                    "receive_alerts": True,
                    "report_frequency": "daily",
                    "preferred_format": "html"
                }
            )
        ]
    
    async def send_daily_report(self, report_data: Dict[str, Any]) -> bool:
        """
        Trimite raportul zilnic
        
        Args:
            report_data: Datele pentru raport
            
        Returns:
            True dacă email-ul a fost trimis cu succes
        """
        try:
            template = self.templates.get_daily_report_template()
            
            # Pregătește datele pentru template
            template_data = {
                "date": datetime.now().strftime("%d.%m.%Y"),
                "summary": report_data.get("summary", "Raport zilnic completat"),
                "revenue": report_data.get("revenue", 0),
                "leads": report_data.get("leads", 0),
                "posts": report_data.get("posts", 0),
                "videos": report_data.get("videos", 0),
                "alerts_section": self.sender.format_alerts_html(report_data.get("alerts", [])),
                "top_performers": self.sender.format_top_performers_html(report_data.get("top_performers", []))
            }
            
            # Generează conținutul email-ului
            subject = template.subject.format(**template_data)
            html_content = template.html_body.format(**template_data)
            text_content = template.text_body.format(**template_data)
            
            # Creează mesajul
            message = EmailMessage(
                to=self.recipients,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                email_type=EmailType.DAILY_REPORT,
                priority=EmailPriority.NORMAL
            )
            
            # Trimite email-ul
            success = await self.sender.send_email(message)
            
            if success:
                logger.info("Raport zilnic trimis cu succes")
            else:
                logger.error("Eroare la trimiterea raportului zilnic")
            
            return success
            
        except Exception as e:
            logger.error(f"Eroare la trimiterea raportului zilnic: {str(e)}")
            return False
    
    async def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        Trimite o alertă
        
        Args:
            alert_data: Datele pentru alertă
            
        Returns:
            True dacă alerta a fost trimisă cu succes
        """
        try:
            template = self.templates.get_alert_template()
            
            # Pregătește datele pentru template
            template_data = {
                "alert_title": alert_data.get("title", "Alertă Sistem"),
                "alert_message": alert_data.get("message", "Alertă generată de sistem"),
                "kpi_name": alert_data.get("kpi_name", "N/A"),
                "current_value": alert_data.get("current_value", "N/A"),
                "threshold": alert_data.get("threshold", "N/A"),
                "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M")
            }
            
            # Generează conținutul email-ului
            subject = template.subject.format(**template_data)
            html_content = template.html_body.format(**template_data)
            text_content = template.text_body.format(**template_data)
            
            # Determină prioritatea pe baza nivelului de alertă
            alert_level = alert_data.get("level", "normal")
            priority_map = {
                "critical": EmailPriority.URGENT,
                "warning": EmailPriority.HIGH,
                "info": EmailPriority.NORMAL,
                "success": EmailPriority.LOW
            }
            priority = priority_map.get(alert_level, EmailPriority.NORMAL)
            
            # Creează mesajul
            message = EmailMessage(
                to=self.recipients,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                email_type=EmailType.ALERT,
                priority=priority
            )
            
            # Trimite email-ul
            success = await self.sender.send_email(message)
            
            if success:
                logger.info(f"Alertă {alert_level} trimisă cu succes")
            else:
                logger.error("Eroare la trimiterea alertei")
            
            return success
            
        except Exception as e:
            logger.error(f"Eroare la trimiterea alertei: {str(e)}")
            return False
    
    async def send_weekly_summary(self, summary_data: Dict[str, Any]) -> bool:
        """
        Trimite sumarul săptămânal
        
        Args:
            summary_data: Datele pentru sumar
            
        Returns:
            True dacă sumarul a fost trimis cu succes
        """
        try:
            template = self.templates.get_weekly_summary_template()
            
            # Calculează perioada săptămânii
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            week_period = f"{week_start.strftime('%d.%m')} - {week_end.strftime('%d.%m.%Y')}"
            
            # Pregătește datele pentru template
            template_data = {
                "week_period": week_period,
                "total_revenue": summary_data.get("total_revenue", 0),
                "conversion_rate": summary_data.get("conversion_rate", 0),
                "growth": summary_data.get("growth", 0),
                "achievements": self.sender.format_achievements_html(summary_data.get("achievements", [])),
                "next_goals": self.sender.format_goals_html(summary_data.get("next_goals", [])),
                "next_week_focus": summary_data.get("next_week_focus", "Continuarea strategiei actuale")
            }
            
            # Generează conținutul email-ului
            subject = template.subject.format(**template_data)
            html_content = template.html_body.format(**template_data)
            text_content = template.text_body.format(**template_data)
            
            # Creează mesajul
            message = EmailMessage(
                to=self.recipients,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                email_type=EmailType.WEEKLY_REPORT,
                priority=EmailPriority.NORMAL
            )
            
            # Trimite email-ul
            success = await self.sender.send_email(message)
            
            if success:
                logger.info("Sumar săptămânal trimis cu succes")
            else:
                logger.error("Eroare la trimiterea sumarului săptămânal")
            
            return success
            
        except Exception as e:
            logger.error(f"Eroare la trimiterea sumarului săptămânal: {str(e)}")
            return False
