"""
Report Templates - HTML and text templates for reports
"""

from typing import Dict, Any, List
from .models import Report, ReportSection, Alert, AlertLevel


class ReportTemplates:
    """Template-uri pentru rapoarte"""
    
    @staticmethod
    def get_html_template(report: Report) -> str:
        """Generează template HTML pentru raport"""
        html = f"""
        <!DOCTYPE html>
        <html lang="ro">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{report.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .alert {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .alert-critical {{ background-color: #ffebee; border-left: 4px solid #f44336; }}
                .alert-warning {{ background-color: #fff3e0; border-left: 4px solid #ff9800; }}
                .alert-info {{ background-color: #e3f2fd; border-left: 4px solid #2196f3; }}
                .alert-success {{ background-color: #e8f5e8; border-left: 4px solid #4caf50; }}
                .summary {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
                .chart {{ margin: 10px 0; padding: 10px; background-color: #fafafa; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report.title}</h1>
                <p>Generat la: {report.generated_at.strftime('%d.%m.%Y %H:%M')}</p>
                <p>Perioada: {report.period_start.strftime('%d.%m.%Y')} - {report.period_end.strftime('%d.%m.%Y')}</p>
            </div>
            
            {ReportTemplates._generate_sections_html(report.sections)}
            
            {ReportTemplates._generate_alerts_html(report.alerts)}
            
            <div class="summary">
                <h3>📋 Sumar</h3>
                <p>{report.summary}</p>
            </div>
        </body>
        </html>
        """
        return html
    
    @staticmethod
    def _generate_sections_html(sections: List[ReportSection]) -> str:
        """Generează HTML pentru secțiuni"""
        html = ""
        for section in sections:
            html += f"""
            <div class="section">
                <h2>{section.title}</h2>
                <p>{section.summary}</p>
                {ReportTemplates._generate_content_html(section.content)}
                {ReportTemplates._generate_charts_html(section.charts)}
            </div>
            """
        return html
    
    @staticmethod
    def _generate_content_html(content: Dict[str, Any]) -> str:
        """Generează HTML pentru conținut"""
        html = "<ul>"
        for key, value in content.items():
            html += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
        html += "</ul>"
        return html
    
    @staticmethod
    def _generate_charts_html(charts: List[Dict[str, Any]]) -> str:
        """Generează HTML pentru grafice"""
        if not charts:
            return ""
        
        html = "<div class='charts'>"
        for chart in charts:
            html += f"""
            <div class="chart">
                <h4>{chart.get('title', 'Chart')}</h4>
                <p>Tip: {chart.get('type', 'unknown')}</p>
                <p>Date: {chart.get('data', {})}</p>
            </div>
            """
        html += "</div>"
        return html
    
    @staticmethod
    def _generate_alerts_html(alerts: List[Alert]) -> str:
        """Generează HTML pentru alerte"""
        if not alerts:
            return ""
        
        html = "<div class='alerts'><h3>🚨 Alerte</h3>"
        for alert in alerts:
            level_class = f"alert-{alert.level.value}"
            html += f"""
            <div class="alert {level_class}">
                <h4>{alert.title}</h4>
                <p>{alert.message}</p>
                <small>Categorie: {alert.category} | {alert.timestamp.strftime('%d.%m.%Y %H:%M')}</small>
            </div>
            """
        html += "</div>"
        return html
    
    @staticmethod
    def get_text_template(report: Report) -> str:
        """Generează template text pentru raport"""
        text = f"""
{report.title}
{'=' * len(report.title)}

Generat la: {report.generated_at.strftime('%d.%m.%Y %H:%M')}
Perioada: {report.period_start.strftime('%d.%m.%Y')} - {report.period_end.strftime('%d.%m.%Y')}

"""
        
        # Adaugă secțiunile
        for section in report.sections:
            text += f"""
{section.title}
{'-' * len(section.title)}

{section.summary}

"""
            for key, value in section.content.items():
                text += f"{key.replace('_', ' ').title()}: {value}\n"
            text += "\n"
        
        # Adaugă alertele
        if report.alerts:
            text += "ALERTE:\n"
            text += "-" * 20 + "\n"
            for alert in report.alerts:
                text += f"[{alert.level.value.upper()}] {alert.title}\n"
                text += f"{alert.message}\n"
                text += f"Categorie: {alert.category}\n\n"
        
        # Adaugă sumarul
        text += f"""
SUMAR:
{report.summary}
"""
        
        return text
