"""
Report Exporters - Export reports to different formats
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
from .models import Report, ReportFormat
from .templates import ReportTemplates


class ReportExporter:
    """Exportator pentru rapoarte în diferite formate"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    async def export_report(self, report: Report, format: ReportFormat = None) -> str:
        """Exportă un raport în format specificat"""
        if format is None:
            format = report.format
        
        if format == ReportFormat.JSON:
            return await self._export_json(report)
        elif format == ReportFormat.HTML:
            return await self._export_html(report)
        elif format == ReportFormat.CSV:
            return await self._export_csv(report)
        else:
            raise ValueError(f"Format {format.value} nu este suportat")
    
    async def _export_json(self, report: Report) -> str:
        """Exportă raportul ca JSON"""
        report_data = {
            "id": report.id,
            "title": report.title,
            "report_type": report.report_type.value,
            "generated_at": report.generated_at.isoformat(),
            "period_start": report.period_start.isoformat(),
            "period_end": report.period_end.isoformat(),
            "sections": [
                {
                    "title": section.title,
                    "content": section.content,
                    "charts": section.charts,
                    "summary": section.summary
                }
                for section in report.sections
            ],
            "alerts": [
                {
                    "id": alert.id,
                    "title": alert.title,
                    "message": alert.message,
                    "level": alert.level.value,
                    "category": alert.category,
                    "timestamp": alert.timestamp.isoformat(),
                    "kpi_name": alert.kpi_name,
                    "threshold": alert.threshold,
                    "current_value": alert.current_value,
                    "resolved": alert.resolved
                }
                for alert in report.alerts
            ],
            "summary": report.summary,
            "metadata": report.metadata
        }
        
        filename = f"{report.id}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    async def _export_html(self, report: Report) -> str:
        """Exportă raportul ca HTML"""
        html_content = ReportTemplates.get_html_template(report)
        
        filename = f"{report.id}.html"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    async def _export_csv(self, report: Report) -> str:
        """Exportă raportul ca CSV"""
        import csv
        
        filename = f"{report.id}.csv"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Raport', report.title])
            writer.writerow(['Generat la', report.generated_at.strftime('%d.%m.%Y %H:%M')])
            writer.writerow(['Perioada', f"{report.period_start.strftime('%d.%m.%Y')} - {report.period_end.strftime('%d.%m.%Y')}"])
            writer.writerow([])
            
            # Secțiuni
            for section in report.sections:
                writer.writerow([section.title])
                writer.writerow(['Metrică', 'Valoare'])
                for key, value in section.content.items():
                    writer.writerow([key.replace('_', ' ').title(), value])
                writer.writerow([])
            
            # Alerte
            if report.alerts:
                writer.writerow(['ALERTE'])
                writer.writerow(['Nivel', 'Titlu', 'Mesaj', 'Categorie'])
                for alert in report.alerts:
                    writer.writerow([alert.level.value, alert.title, alert.message, alert.category])
                writer.writerow([])
            
            # Sumar
            writer.writerow(['SUMAR', report.summary])
        
        return str(filepath)
    
    async def export_text(self, report: Report) -> str:
        """Exportă raportul ca text simplu"""
        text_content = ReportTemplates.get_text_template(report)
        
        filename = f"{report.id}.txt"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        return str(filepath)
    
    def get_export_history(self) -> List[Dict[str, Any]]:
        """Returnează istoricul exporturilor"""
        history = []
        
        for file_path in self.output_dir.glob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                history.append({
                    "filename": file_path.name,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime),
                    "modified": datetime.fromtimestamp(stat.st_mtime)
                })
        
        return sorted(history, key=lambda x: x["created"], reverse=True)
    
    def cleanup_old_reports(self, days: int = 30):
        """Șterge rapoartele vechi"""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        deleted_count = 0
        
        for file_path in self.output_dir.glob("*"):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_date:
                file_path.unlink()
                deleted_count += 1
        
        return deleted_count
