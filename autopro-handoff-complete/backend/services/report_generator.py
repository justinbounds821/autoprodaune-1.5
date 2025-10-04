"""
Report Generator - Wrapper compatibil pentru sistemul modular
"""

from .reporting import (
    ReportGenerator,
    ReportType,
    ReportFormat,
    AlertLevel,
    ReportSection,
    Alert,
    Report,
    DailyReportGenerator,
    WeeklyReportGenerator,
    ReportTemplates,
    ReportExporter
)

# Singleton instance
_report_generator = None

def get_report_generator() -> ReportGenerator:
    """Returnează instanța singleton a ReportGenerator"""
    global _report_generator
    if _report_generator is None:
        _report_generator = ReportGenerator()
    return _report_generator

# Funcții helper pentru generarea rapidă
async def generate_daily_report(data: dict) -> Report:
    """
    Funcție helper pentru generarea raportului zilnic
    
    Args:
        data: Datele pentru raport
        
    Returns:
        Raportul generat
    """
    generator = get_report_generator()
    return await generator.generate_report(ReportType.DAILY, data)

async def generate_weekly_report(data: dict) -> Report:
    """
    Funcție helper pentru generarea raportului săptămânal
    
    Args:
        data: Datele pentru raport
        
    Returns:
        Raportul generat
    """
    generator = get_report_generator()
    return await generator.generate_report(ReportType.WEEKLY, data)

__all__ = [
    "ReportGenerator",
    "ReportType",
    "ReportFormat",
    "AlertLevel",
    "ReportSection",
    "Alert",
    "Report",
    "DailyReportGenerator",
    "WeeklyReportGenerator",
    "ReportTemplates",
    "ReportExporter",
    "get_report_generator",
    "generate_daily_report",
    "generate_weekly_report"
]
