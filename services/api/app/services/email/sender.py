"""
Email Sender - Core email sending functionality
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any
from .models import EmailMessage, EmailConfig

logger = logging.getLogger(__name__)


class EmailSender:
    """Handles email sending functionality"""
    
    def __init__(self, config: EmailConfig):
        self.config = config
    
    async def send_email(self, message: EmailMessage) -> bool:
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
    
    def format_alerts_html(self, alerts: List[Dict[str, Any]]) -> str:
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
    
    def format_top_performers_html(self, performers: List[Dict[str, Any]]) -> str:
        """Formatează top performerii pentru HTML"""
        if not performers:
            return "<li>Nu există date disponibile</li>"
        
        html = ""
        for performer in performers:
            html += f"<li>{performer.get('name', 'N/A')}: {performer.get('value', 0)} {performer.get('unit', '')}</li>"
        
        return html
    
    def format_achievements_html(self, achievements: List[str]) -> str:
        """Formatează realizările pentru HTML"""
        if not achievements:
            return "<li>Nu există realizări înregistrate</li>"
        
        html = ""
        for achievement in achievements:
            html += f"<li>{achievement}</li>"
        
        return html
    
    def format_goals_html(self, goals: List[str]) -> str:
        """Formatează obiectivele pentru HTML"""
        if not goals:
            return "<li>Nu există obiective definite</li>"
        
        html = ""
        for goal in goals:
            html += f"<li>{goal}</li>"
        
        return html
