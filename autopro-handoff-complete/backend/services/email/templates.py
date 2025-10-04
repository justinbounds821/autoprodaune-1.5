"""
Email Templates - HTML and text templates for various email types
"""

from .models import EmailTemplate, EmailType


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
