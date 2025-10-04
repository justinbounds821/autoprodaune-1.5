"""
Email Reporter - Serviciu pentru trimiterea email-urilor cu rapoarte și alerte
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import asyncio
import aiohttp

# Configurează logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class EmailTemplates:
    """Template-uri pentru email-uri"""
    
    @staticmethod
    def get_daily_report_template() -> EmailTemplate:
        """Template pentru raportul zilnic"""
        return EmailTemplate(
            id="daily_report",
            subject="📊 Raport Zilnic AutoPro Daune - {date}",
            html_body="""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;">
                        <h1 style="margin: 0; font-size: 28px;">📊 Raport Zilnic AutoPro Daune</h1>
                        <p style="margin: 10px 0 0 0; font-size: 16px;">{date}</p>
                    </div>
                    
                    <div style="margin: 30px 0;">
                        <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">📋 Sumar Executiv</h2>
                        <p style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea;">
                            {summary}
                        </p>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0;">
                        <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; text-align: center;">
                            <h3 style="margin: 0 0 10px 0; color: #4caf50;">💰 Venituri</h3>
                            <p style="font-size: 24px; font-weight: bold; margin: 0; color: #2e7d32;">{revenue} RON</p>
                        </div>
                        <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; text-align: center;">
                            <h3 style="margin: 0 0 10px 0; color: #2196f3;">👥 Leads Noi</h3>
                            <p style="font-size: 24px; font-weight: bold; margin: 0; color: #1565c0;">{leads}</p>
                        </div>
                        <div style="background: #fff3e0; padding: 20px; border-radius: 8px; text-align: center;">
                            <h3 style="margin: 0 0 10px 0; color: #ff9800;">📱 Postări</h3>
                            <p style="font-size: 24px; font-weight: bold; margin: 0; color: #ef6c00;">{posts}</p>
                        </div>
                        <div style="background: #fce4ec; padding: 20px; border-radius: 8px; text-align: center;">
                            <h3 style="margin: 0 0 10px 0; color: #e91e63;">🎬 Video-uri</h3>
                            <p style="font-size: 24px; font-weight: bold; margin: 0; color: #ad1457;">{videos}</p>
                        </div>
                    </div>
                    
                    {alerts_section}
                    
                    <div style="margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <h2 style="color: #667eea; margin: 0 0 15px 0;">📈 Top Performers</h2>
                        <ul style="margin: 0; padding-left: 20px;">
                            {top_performers}
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0; padding: 20px; background: #667eea; color: white; border-radius: 8px;">
                        <p style="margin: 0; font-size: 14px;">
                            Generat automat de sistemul AutoPro Daune<br>
                            Pentru întrebări, contactează echipa de suport
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """,
            text_body="""
            Raport Zilnic AutoPro Daune - {date}
            
            Sumar: {summary}
            
            Metrici cheie:
            - Venituri: {revenue} RON
            - Leads noi: {leads}
            - Postări: {posts}
            - Video-uri generate: {videos}
            
            {alerts_text}
            
            Top Performers:
            {top_performers_text}
            
            ---
            Generat automat de sistemul AutoPro Daune
            """,
            email_type=EmailType.DAILY_REPORT,
            variables=["date", "summary", "revenue", "leads", "posts", "videos", "alerts_section", "top_performers"]
        )
    
    @staticmethod
    def get_alert_template() -> EmailTemplate:
        """Template pentru alerte"""
        return EmailTemplate(
            id="alert",
            subject="🚨 ALERTĂ AutoPro Daune - {alert_title}",
            html_body="""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: #ffebee; border: 2px solid #f44336; padding: 20px; border-radius: 8px; text-align: center;">
                        <h1 style="margin: 0; color: #d32f2f;">🚨 ALERTĂ SISTEM</h1>
                        <h2 style="margin: 10px 0; color: #c62828;">{alert_title}</h2>
                    </div>
                    
                    <div style="margin: 30px 0;">
                        <h3 style="color: #d32f2f;">Detalii:</h3>
                        <p style="background: #fff3e0; padding: 15px; border-radius: 5px; border-left: 4px solid #ff9800;">
                            {alert_message}
                        </p>
                    </div>
                    
                    <div style="background: #f5f5f5; padding: 20px; border-radius: 8px;">
                        <h3 style="margin: 0 0 15px 0;">Informații Tehnice:</h3>
                        <ul style="margin: 0; padding-left: 20px;">
                            <li><strong>KPI:</strong> {kpi_name}</li>
                            <li><strong>Valoare Actuală:</strong> {current_value}</li>
                            <li><strong>Prag:</strong> {threshold}</li>
                            <li><strong>Timpul:</strong> {timestamp}</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <p style="margin: 0; font-size: 14px; color: #666;">
                            Această alertă a fost generată automat de sistemul AutoPro Daune
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """,
            text_body="""
            ALERTĂ AutoPro Daune - {alert_title}
            
            {alert_message}
            
            Informații:
            - KPI: {kpi_name}
            - Valoare actuală: {current_value}
            - Prag: {threshold}
            - Timp: {timestamp}
            
            ---
            Alertă automată generată de sistemul AutoPro Daune
            """,
            email_type=EmailType.ALERT,
            variables=["alert_title", "alert_message", "kpi_name", "current_value", "threshold", "timestamp"]
        )
    
    @staticmethod
    def get_weekly_summary_template() -> EmailTemplate:
        """Template pentru sumarul săptămânal"""
        return EmailTemplate(
            id="weekly_summary",
            subject="📈 Sumar Săptămânal AutoPro Daune - {week_period}",
            html_body="""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #4caf50 0%, #45a049 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;">
                        <h1 style="margin: 0; font-size: 28px;">📈 Sumar Săptămânal</h1>
                        <p style="margin: 10px 0 0 0; font-size: 16px;">{week_period}</p>
                    </div>
                    
                    <div style="margin: 30px 0;">
                        <h2 style="color: #4caf50; border-bottom: 2px solid #4caf50; padding-bottom: 10px;">🎯 Performanță Săptămânală</h2>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                            <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; text-align: center;">
                                <h3 style="margin: 0; color: #4caf50;">💰 Venituri Totale</h3>
                                <p style="font-size: 20px; font-weight: bold; margin: 5px 0; color: #2e7d32;">{total_revenue} RON</p>
                            </div>
                            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; text-align: center;">
                                <h3 style="margin: 0; color: #2196f3;">📊 Rata Conversie</h3>
                                <p style="font-size: 20px; font-weight: bold; margin: 5px 0; color: #1565c0;">{conversion_rate}%</p>
                            </div>
                            <div style="background: #fff3e0; padding: 15px; border-radius: 8px; text-align: center;">
                                <h3 style="margin: 0; color: #ff9800;">📈 Creștere</h3>
                                <p style="font-size: 20px; font-weight: bold; margin: 5px 0; color: #ef6c00;">{growth}%</p>
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin: 30px 0;">
                        <h2 style="color: #4caf50; border-bottom: 2px solid #4caf50; padding-bottom: 10px;">🏆 Realizări Săptămânale</h2>
                        <ul style="margin: 0; padding-left: 20px;">
                            {achievements}
                        </ul>
                    </div>
                    
                    <div style="margin: 30px 0;">
                        <h2 style="color: #4caf50; border-bottom: 2px solid #4caf50; padding-bottom: 10px;">🎯 Obiective Următoare</h2>
                        <ul style="margin: 0; padding-left: 20px;">
                            {next_goals}
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0; padding: 20px; background: #4caf50; color: white; border-radius: 8px;">
                        <p style="margin: 0; font-size: 14px;">
                            Săptămâna viitoare: {next_week_focus}
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """,
            text_body="""
            Sumar Săptămânal AutoPro Daune - {week_period}
            
            Performanță:
            - Venituri totale: {total_revenue} RON
            - Rata de conversie: {conversion_rate}%
            - Creștere: {growth}%
            
            Realizări:
            {achievements_text}
            
            Obiective următoare:
            {next_goals_text}
            
            Focus săptămâna viitoare: {next_week_focus}
            
            ---
            Generat automat de sistemul AutoPro Daune
            """,
            email_type=EmailType.WEEKLY_REPORT,
            variables=["week_period", "total_revenue", "conversion_rate", "growth", "achievements", "next_goals", "next_week_focus"]
        )

class EmailReporter:
    """Reporter principal pentru email-uri"""
    
    def __init__(self):
        self.config = EmailConfig()
        self.templates = EmailTemplates()
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
                "alerts_section": self._format_alerts_html(report_data.get("alerts", [])),
                "top_performers": self._format_top_performers_html(report_data.get("top_performers", []))
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
            success = await self._send_email(message)
            
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
            success = await self._send_email(message)
            
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
                "achievements": self._format_achievements_html(summary_data.get("achievements", [])),
                "next_goals": self._format_goals_html(summary_data.get("next_goals", [])),
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
            success = await self._send_email(message)
            
            if success:
                logger.info("Sumar săptămânal trimis cu succes")
            else:
                logger.error("Eroare la trimiterea sumarului săptămânal")
            
            return success
            
        except Exception as e:
            logger.error(f"Eroare la trimiterea sumarului săptămânal: {str(e)}")
            return False
    
    async def _send_email(self, message: EmailMessage) -> bool:
        """
        Trimite un email
        
        Args:
            message: Mesajul de trimis
            
        Returns:
            True dacă email-ul a fost trimis cu succes
        """
        try:
            if not self.config.smtp_username or not self.config.smtp_password:
                logger.warning("SMTP credentials nu sunt configurate")
                return False
            
            # Creează mesajul MIME
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config.from_name} <{self.config.from_email}>"
            msg['Subject'] = message.subject
            
            # Adaugă destinatarii
            to_emails = [recipient.email for recipient in message.to]
            msg['To'] = ", ".join(to_emails)
            
            if message.cc:
                cc_emails = [recipient.email for recipient in message.cc]
                msg['Cc'] = ", ".join(cc_emails)
            
            # Adaugă conținutul
            text_part = MIMEText(message.text_content, 'plain', 'utf-8')
            html_part = MIMEText(message.html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Adaugă atașamentele
            for attachment_path in message.attachments:
                if os.path.exists(attachment_path):
                    with open(attachment_path, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(attachment_path)}'
                        )
                        msg.attach(part)
            
            # Conectează la serverul SMTP și trimite email-ul
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                server.login(self.config.smtp_username, self.config.smtp_password)
                
                # Trimite email-ul
                all_recipients = to_emails.copy()
                if message.cc:
                    all_recipients.extend([recipient.email for recipient in message.cc])
                if message.bcc:
                    all_recipients.extend([recipient.email for recipient in message.bcc])
                
                server.sendmail(self.config.from_email, all_recipients, msg.as_string())
            
            logger.info(f"Email trimis cu succes către {len(all_recipients)} destinatari")
            return True
            
        except Exception as e:
            logger.error(f"Eroare la trimiterea email-ului: {str(e)}")
            return False
    
    def _format_alerts_html(self, alerts: List[Dict[str, Any]]) -> str:
        """Formatează alertele pentru HTML"""
        if not alerts:
            return "<p style='color: #4caf50; font-weight: bold;'>✅ Nu există alerte active</p>"
        
        html = "<div style='margin: 20px 0;'>"
        for alert in alerts:
            level = alert.get("level", "info")
            color_map = {
                "critical": "#f44336",
                "warning": "#ff9800",
                "info": "#2196f3",
                "success": "#4caf50"
            }
            color = color_map.get(level, "#2196f3")
            
            html += f"""
            <div style='background: {color}20; border-left: 4px solid {color}; padding: 15px; margin: 10px 0; border-radius: 4px;'>
                <h4 style='margin: 0 0 10px 0; color: {color};'>{alert.get('title', 'Alertă')}</h4>
                <p style='margin: 0;'>{alert.get('message', '')}</p>
            </div>
            """
        
        html += "</div>"
        return html
    
    def _format_top_performers_html(self, performers: List[Dict[str, Any]]) -> str:
        """Formatează top performerii pentru HTML"""
        if not performers:
            return "<li>Nu există date disponibile</li>"
        
        html = ""
        for performer in performers:
            html += f"<li>{performer.get('name', 'N/A')}: {performer.get('value', 0)} {performer.get('unit', '')}</li>"
        
        return html
    
    def _format_achievements_html(self, achievements: List[str]) -> str:
        """Formatează realizările pentru HTML"""
        if not achievements:
            return "<li>Nu există realizări înregistrate</li>"
        
        html = ""
        for achievement in achievements:
            html += f"<li>{achievement}</li>"
        
        return html
    
    def _format_goals_html(self, goals: List[str]) -> str:
        """Formatează obiectivele pentru HTML"""
        if not goals:
            return "<li>Nu există obiective definite</li>"
        
        html = ""
        for goal in goals:
            html += f"<li>{goal}</li>"
        
        return html

# Singleton instance
_email_reporter = None

def get_email_reporter() -> EmailReporter:
    """Returnează instanța singleton a EmailReporter"""
    global _email_reporter
    if _email_reporter is None:
        _email_reporter = EmailReporter()
    return _email_reporter

# Funcții helper pentru trimiterea rapidă
async def send_daily_report_email(report_data: Dict[str, Any]) -> bool:
    """
    Funcție helper pentru trimiterea raportului zilnic
    
    Args:
        report_data: Datele pentru raport
        
    Returns:
        True dacă email-ul a fost trimis cu succes
    """
    reporter = get_email_reporter()
    return await reporter.send_daily_report(report_data)

async def send_alert_email(alert_data: Dict[str, Any]) -> bool:
    """
    Funcție helper pentru trimiterea unei alerte
    
    Args:
        alert_data: Datele pentru alertă
        
    Returns:
        True dacă alerta a fost trimisă cu succes
    """
    reporter = get_email_reporter()
    return await reporter.send_alert(alert_data)
