"""
Report Service - Main orchestrator for report generation
"""

import logging
from typing import Dict, Any
from .models import ReportType, ReportFormat, Report
from .generators import DailyReportGenerator, WeeklyReportGenerator
from .exporters import ReportExporter

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generator principal pentru rapoarte"""
    
    def __init__(self):
        self.daily_generator = DailyReportGenerator()
        self.weekly_generator = WeeklyReportGenerator()
        self.exporter = ReportExporter()
        
    async def generate_report(
        self,
        report_type: ReportType,
        data: Dict[str, Any],
        format: ReportFormat = ReportFormat.HTML
    ) -> Report:
        """
        Generează un raport de tipul specificat
        
        Args:
            report_type: Tipul raportului
            data: Datele pentru raport
            format: Formatul raportului
            
        Returns:
            Report generat
        """
        try:
            if report_type == ReportType.DAILY:
                report = await self.daily_generator.generate_report(data)
            elif report_type == ReportType.WEEKLY:
                report = await self.weekly_generator.generate_report(data)
            else:
                raise ValueError(f"Tipul de raport {report_type.value} nu este implementat")
            
            # Setează formatul
            report.format = format
            
            logger.info(f"Generat raport {report_type.value} cu ID {report.id}")
            return report
            
        except Exception as e:
            logger.error(f"Eroare la generarea raportului {report_type.value}: {str(e)}")
            raise
    
    async def save_report(self, report: Report, output_dir: str = "reports") -> str:
        """
        Salvează un raport pe disk
        
        Args:
            report: Raportul de salvat
            output_dir: Directorul de output
            
        Returns:
            Calea către fișierul salvat
        """
        try:
            return await self.exporter.export_report(report, report.format)
            
        except Exception as e:
            logger.error(f"Eroare la salvarea raportului: {str(e)}")
            raise
    
    async def generate_and_save(
        self,
        report_type: ReportType,
        data: Dict[str, Any],
        format: ReportFormat = ReportFormat.HTML
    ) -> str:
        """
        Generează și salvează un raport
        
        Args:
            report_type: Tipul raportului
            data: Datele pentru raport
            format: Formatul raportului
            
        Returns:
            Calea către fișierul salvat
        """
        report = await self.generate_report(report_type, data, format)
        return await self.save_report(report)
    
    def get_export_history(self) -> list:
        """Returnează istoricul exporturilor"""
        return self.exporter.get_export_history()
    
    def cleanup_old_reports(self, days: int = 30) -> int:
        """Șterge rapoartele vechi"""
        return self.exporter.cleanup_old_reports(days)
