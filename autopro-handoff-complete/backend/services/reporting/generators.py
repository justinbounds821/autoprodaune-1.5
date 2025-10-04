"""
Report Generators - Individual report generators for different time periods
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .models import ReportType, ReportFormat, AlertLevel, Report, ReportSection, Alert

logger = logging.getLogger(__name__)


class DailyReportGenerator:
    """Generator pentru rapoarte zilnice"""
    
    def __init__(self):
        self.report_type = ReportType.DAILY
    
    async def generate_report(self, data: Dict[str, Any]) -> Report:
        """Generează un raport zilnic"""
        today = datetime.now().date()
        period_start = datetime.combine(today, datetime.min.time())
        period_end = datetime.combine(today, datetime.max.time())
        
        sections = []
        
        # Secțiunea financiară
        financial_section = await self._generate_financial_section(data.get("financial", {}))
        sections.append(financial_section)
        
        # Secțiunea marketing
        marketing_section = await self._generate_marketing_section(data.get("marketing", {}))
        sections.append(marketing_section)
        
        # Secțiunea operațională
        operational_section = await self._generate_operational_section(data.get("operational", {}))
        sections.append(operational_section)
        
        # Generează alertele
        alerts = await self._generate_alerts(data)
        
        # Generează sumarul
        summary = await self._generate_summary(sections, alerts)
        
        report = Report(
            id=f"daily_report_{today.strftime('%Y%m%d')}",
            title=f"Raport Zilnic - {today.strftime('%d.%m.%Y')}",
            report_type=self.report_type,
            format=ReportFormat.HTML,
            generated_at=datetime.now(),
            period_start=period_start,
            period_end=period_end,
            sections=sections,
            summary=summary,
            alerts=alerts
        )
        
        logger.info(f"Generat raport zilnic cu {len(sections)} secțiuni și {len(alerts)} alerte")
        return report
    
    async def _generate_financial_section(self, financial_data: Dict[str, Any]) -> ReportSection:
        """Generează secțiunea financiară"""
        content = {
            "revenue_today": financial_data.get("revenue_today", 0),
            "costs_today": financial_data.get("costs_today", 0),
            "profit_today": financial_data.get("revenue_today", 0) - financial_data.get("costs_today", 0),
            "leads_today": financial_data.get("leads_today", 0),
            "conversions_today": financial_data.get("conversions_today", 0)
        }
        
        charts = [
            {
                "type": "bar",
                "title": "Venituri vs Costuri Zilnice",
                "data": {
                    "labels": ["Venituri", "Costuri", "Profit"],
                    "values": [content["revenue_today"], content["costs_today"], content["profit_today"]]
                }
            },
            {
                "type": "line",
                "title": "Trend Venituri (7 zile)",
                "data": financial_data.get("revenue_trend", [])
            }
        ]
        
        return ReportSection(
            title="📊 Financiar",
            content=content,
            charts=charts,
            summary=f"Profit zilnic: {content['profit_today']} RON din {content['leads_today']} leads noi"
        )
    
    async def _generate_marketing_section(self, marketing_data: Dict[str, Any]) -> ReportSection:
        """Generează secțiunea de marketing"""
        content = {
            "posts_today": marketing_data.get("posts_today", 0),
            "engagement_today": marketing_data.get("engagement_today", 0),
            "reach_today": marketing_data.get("reach_today", 0),
            "new_followers": marketing_data.get("new_followers", 0),
            "click_through_rate": marketing_data.get("ctr", 0)
        }
        
        charts = [
            {
                "type": "pie",
                "title": "Distribuția Engagement pe Platforme",
                "data": marketing_data.get("platform_engagement", {})
            }
        ]
        
        return ReportSection(
            title="📱 Marketing",
            content=content,
            charts=charts,
            summary=f"{content['posts_today']} postări cu {content['engagement_today']} interacțiuni"
        )
    
    async def _generate_operational_section(self, operational_data: Dict[str, Any]) -> ReportSection:
        """Generează secțiunea operațională"""
        content = {
            "response_time_avg": operational_data.get("avg_response_time", 0),
            "success_rate": operational_data.get("success_rate", 0),
            "uptime_percentage": operational_data.get("uptime", 0),
            "videos_generated": operational_data.get("videos_generated", 0),
            "bot_messages": operational_data.get("bot_messages", 0)
        }
        
        charts = [
            {
                "type": "gauge",
                "title": "Uptime Sistem",
                "data": {"value": content["uptime_percentage"], "max": 100}
            }
        ]
        
        return ReportSection(
            title="⚙️ Operațional",
            content=content,
            charts=charts,
            summary=f"Uptime: {content['uptime_percentage']:.1f}%, {content['videos_generated']} video-uri generate"
        )
    
    async def _generate_alerts(self, data: Dict[str, Any]) -> List[Alert]:
        """Generează alertele pentru raport"""
        alerts = []
        
        # Verifică KPI-uri critice
        financial_data = data.get("financial", {})
        if financial_data.get("revenue_today", 0) < 100:
            alerts.append(Alert(
                id="low_revenue_alert",
                title="Venituri Scăzute",
                message="Veniturile zilnice sunt sub pragul minim de 100 RON",
                level=AlertLevel.WARNING,
                category="financial",
                timestamp=datetime.now(),
                kpi_name="revenue_today",
                threshold=100,
                current_value=financial_data.get("revenue_today", 0)
            ))
        
        operational_data = data.get("operational", {})
        if operational_data.get("uptime", 100) < 99:
            alerts.append(Alert(
                id="uptime_alert",
                title="Uptime Scăzut",
                message="Uptime-ul sistemului este sub 99%",
                level=AlertLevel.CRITICAL,
                category="operational",
                timestamp=datetime.now(),
                kpi_name="uptime",
                threshold=99,
                current_value=operational_data.get("uptime", 0)
            ))
        
        return alerts
    
    async def _generate_summary(self, sections: List[ReportSection], alerts: List[Alert]) -> str:
        """Generează sumarul raportului"""
        critical_alerts = [a for a in alerts if a.level == AlertLevel.CRITICAL]
        warning_alerts = [a for a in alerts if a.level == AlertLevel.WARNING]
        
        summary = f"Raport zilnic generat cu {len(sections)} secțiuni principale. "
        
        if critical_alerts:
            summary += f"⚠️ {len(critical_alerts)} alerte critice necesită atenție imediată. "
        
        if warning_alerts:
            summary += f"⚠️ {len(warning_alerts)} avertismente de monitorizat. "
        
        if not alerts:
            summary += "✅ Toate indicatorii sunt în parametrii normali."
        
        return summary


class WeeklyReportGenerator:
    """Generator pentru rapoarte săptămânale"""
    
    def __init__(self):
        self.report_type = ReportType.WEEKLY
    
    async def generate_report(self, data: Dict[str, Any]) -> Report:
        """Generează un raport săptămânal"""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        sections = []
        
        # Secțiunea de performanță săptămânală
        performance_section = await self._generate_performance_section(data.get("weekly_performance", {}))
        sections.append(performance_section)
        
        # Secțiunea de tendințe
        trends_section = await self._generate_trends_section(data.get("trends", {}))
        sections.append(trends_section)
        
        # Secțiunea de recomandări
        recommendations_section = await self._generate_recommendations_section(data.get("recommendations", {}))
        sections.append(recommendations_section)
        
        # Generează alertele
        alerts = await self._generate_weekly_alerts(data)
        
        # Generează sumarul
        summary = await self._generate_weekly_summary(sections, alerts)
        
        report = Report(
            id=f"weekly_report_{week_start.strftime('%Y%m%d')}",
            title=f"Raport Săptămânal - {week_start.strftime('%d.%m.%Y')} - {week_end.strftime('%d.%m.%Y')}",
            report_type=self.report_type,
            format=ReportFormat.HTML,
            generated_at=datetime.now(),
            period_start=week_start,
            period_end=week_end,
            sections=sections,
            summary=summary,
            alerts=alerts
        )
        
        logger.info(f"Generat raport săptămânal cu {len(sections)} secțiuni")
        return report
    
    async def _generate_performance_section(self, performance_data: Dict[str, Any]) -> ReportSection:
        """Generează secțiunea de performanță"""
        content = {
            "total_revenue": performance_data.get("total_revenue", 0),
            "total_leads": performance_data.get("total_leads", 0),
            "conversion_rate": performance_data.get("conversion_rate", 0),
            "avg_response_time": performance_data.get("avg_response_time", 0),
            "customer_satisfaction": performance_data.get("satisfaction", 0)
        }
        
        charts = [
            {
                "type": "line",
                "title": "Venituri Săptămânale",
                "data": performance_data.get("revenue_trend", [])
            },
            {
                "type": "bar",
                "title": "Leads pe Zi",
                "data": performance_data.get("daily_leads", [])
            }
        ]
        
        return ReportSection(
            title="📈 Performanță Săptămânală",
            content=content,
            charts=charts,
            summary=f"Venituri totale: {content['total_revenue']} RON, {content['total_leads']} leads noi"
        )
    
    async def _generate_trends_section(self, trends_data: Dict[str, Any]) -> ReportSection:
        """Generează secțiunea de tendințe"""
        content = {
            "revenue_growth": trends_data.get("revenue_growth", 0),
            "lead_growth": trends_data.get("lead_growth", 0),
            "engagement_growth": trends_data.get("engagement_growth", 0),
            "top_performing_content": trends_data.get("top_content", []),
            "peak_hours": trends_data.get("peak_hours", [])
        }
        
        charts = [
            {
                "type": "heatmap",
                "title": "Activitate pe Ore",
                "data": trends_data.get("activity_heatmap", {})
            }
        ]
        
        return ReportSection(
            title="📊 Tendențe și Insights",
            content=content,
            charts=charts,
            summary=f"Creștere venituri: {content['revenue_growth']:.1f}%, creștere leads: {content['lead_growth']:.1f}%"
        )
    
    async def _generate_recommendations_section(self, recommendations_data: Dict[str, Any]) -> ReportSection:
        """Generează secțiunea de recomandări"""
        content = {
            "optimization_opportunities": recommendations_data.get("optimizations", []),
            "content_recommendations": recommendations_data.get("content", []),
            "budget_recommendations": recommendations_data.get("budget", []),
            "technical_improvements": recommendations_data.get("technical", [])
        }
        
        return ReportSection(
            title="💡 Recomandări",
            content=content,
            summary=f"{len(content['optimization_opportunities'])} oportunități de optimizare identificate"
        )
    
    async def _generate_weekly_alerts(self, data: Dict[str, Any]) -> List[Alert]:
        """Generează alertele săptămânale"""
        alerts = []
        
        # Verifică performanța săptămânală
        performance = data.get("weekly_performance", {})
        if performance.get("conversion_rate", 0) < 2:
            alerts.append(Alert(
                id="low_conversion_weekly",
                title="Rata de Conversie Scăzută",
                message="Rata de conversie săptămânală este sub 2%",
                level=AlertLevel.WARNING,
                category="marketing",
                timestamp=datetime.now(),
                kpi_name="conversion_rate",
                threshold=2,
                current_value=performance.get("conversion_rate", 0)
            ))
        
        return alerts
    
    async def _generate_weekly_summary(self, sections: List[ReportSection], alerts: List[Alert]) -> str:
        """Generează sumarul săptămânal"""
        performance_section = sections[0] if sections else None
        trends_section = sections[1] if len(sections) > 1 else None
        
        summary = "Raport săptămânal completat. "
        
        if performance_section:
            revenue = performance_section.content.get("total_revenue", 0)
            leads = performance_section.content.get("total_leads", 0)
            summary += f"Performanță: {revenue} RON venituri din {leads} leads. "
        
        if trends_section:
            revenue_growth = trends_section.content.get("revenue_growth", 0)
            summary += f"Tendințe: creștere venituri cu {revenue_growth:.1f}%. "
        
        if alerts:
            summary += f"Atenție: {len(alerts)} alerte necesită monitorizare."
        else:
            summary += "Toate indicatorii sunt în parametrii normali."
        
        return summary
