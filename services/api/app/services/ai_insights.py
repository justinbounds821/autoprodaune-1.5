"""AI-powered predictive analytics service for AutoPro Daune."""
from __future__ import annotations

import hashlib
import json
import math
import statistics
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, Iterable, List, Optional

from sqlalchemy.orm import Session

from ..models.financial import CampaignMetrics, FinancialMetrics


@dataclass
class Insight:
    """Dataclass representing a single AI insight."""

    id: str
    type: str
    impact: str
    title: str
    description: str
    confidence: float
    category: str
    data: Dict[str, float]
    created_at: datetime


class AIInsightsService:
    """Service responsible for generating predictive analytics insights."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_predictive_insights(
        self,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        platform: Optional[str] = None,
        min_confidence: Optional[float] = None,
    ) -> Dict[str, object]:
        """Generate predictive insights for the dashboard."""

        window_end = end_date or date.today()
        window_start = start_date or (window_end - timedelta(days=60))

        financial_metrics = self._fetch_financial_metrics(window_start, window_end)
        campaign_metrics = self._fetch_campaign_metrics(window_start, window_end, platform)

        insights: List[Insight] = []
        insights.extend(self._build_financial_insights(financial_metrics))
        insights.extend(self._build_campaign_insights(campaign_metrics))

        if min_confidence is not None:
            insights = [ins for ins in insights if ins.confidence >= min_confidence]

        metrics = self._compute_summary_metrics(insights)

        return {
            "insights": [self._serialize_insight(insight) for insight in insights],
            "metrics": metrics,
            "context": {
                "window": {
                    "start": window_start.isoformat(),
                    "end": window_end.isoformat(),
                },
                "source_counts": {
                    "financial_metrics": len(financial_metrics),
                    "campaign_metrics": len(campaign_metrics),
                },
            },
        }

    def generate_report(self, insight_ids: Iterable[str], insights: List[Dict[str, object]]) -> Dict[str, object]:
        """Generate a natural language report for the requested insights."""

        lookup = {ins["id"]: ins for ins in insights}
        selected = [lookup[i] for i in insight_ids if i in lookup]
        if not selected:
            return {
                "title": "Raport AI", 
                "summary": "Nu au fost găsite insight-uri pentru generarea raportului.",
                "insights": [],
            }

        summary_lines: List[str] = []
        for insight in selected:
            summary_lines.append(
                f"• ({insight['impact']}) {insight['title']}: {insight['description']}"
            )

        return {
            "title": "Raport AI personalizat",
            "summary": "\n".join(summary_lines),
            "insights": selected,
        }

    # ------------------------------------------------------------------
    # Financial insights
    # ------------------------------------------------------------------
    def _build_financial_insights(self, metrics: List[FinancialMetrics]) -> List[Insight]:
        if not metrics:
            return []

        revenue_series = [self._to_float(m.total_revenue) for m in metrics]
        cost_series = [self._to_float(m.total_costs) for m in metrics]
        profit_series = [self._to_float(m.net_profit) for m in metrics]

        insights: List[Insight] = []

        growth_rate, forecast = self._linear_trend(revenue_series)
        if growth_rate is not None and forecast is not None:
            data = {
                "growth_rate": growth_rate,
                "forecast_value": forecast,
                "current": revenue_series[-1],
            }
            insights.append(
                Insight(
                    id=self._generate_id("rev-trend", data),
                    type="prediction",
                    impact=self._classify_impact(growth_rate),
                    title="Creștere proiectată a veniturilor",
                    description=
                        f"Veniturile au un trend de {growth_rate:.1f}% pe intervalul analizat."
                        f" Predicția pentru următoarea perioadă este {forecast:,.0f} EUR.",
                    confidence=self._confidence_from_points(revenue_series),
                    category="financial",
                    data=data,
                    created_at=datetime.utcnow(),
                )
            )

        burn_rate, future_cost = self._linear_trend(cost_series)
        if burn_rate is not None and future_cost is not None:
            impact = "critical" if burn_rate > 5 else ("high" if burn_rate > 0 else "medium")
            data = {
                "trend": burn_rate,
                "forecast_value": future_cost,
                "current": cost_series[-1],
            }
            insights.append(
                Insight(
                    id=self._generate_id("cost-trend", data),
                    type="trend",
                    impact=impact,
                    title="Tendință costuri operaționale",
                    description=
                        f"Costurile au variat cu un trend de {burn_rate:.1f}% și pot ajunge la {future_cost:,.0f} EUR."
                        " Recomandăm monitorizarea atentă a bugetului.",
                    confidence=self._confidence_from_points(cost_series),
                    category="financial",
                    data=data,
                    created_at=datetime.utcnow(),
                )
            )

        avg_margin = self._safe_average(
            [self._percentage(p, r) for p, r in zip(profit_series, revenue_series)]
        )
        if avg_margin is not None:
            trend, _ = self._linear_trend(profit_series)
            impact = "high" if avg_margin >= 15 else "medium"
            data = {
                "avg_margin": avg_margin,
                "trend": trend or 0.0,
                "current_profit": profit_series[-1],
            }
            insights.append(
                Insight(
                    id=self._generate_id("margin", data),
                    type="recommendation",
                    impact=impact if (trend or 0) >= 0 else "critical",
                    title="Analiză marjă de profit",
                    description=
                        f"Marja medie de profit este {avg_margin:.1f}% în perioada evaluată."
                        " Ajustați mixul de campanii pentru a menține marja peste 20%.",
                    confidence=self._confidence_from_points(profit_series),
                    category="financial",
                    data=data,
                    created_at=datetime.utcnow(),
                )
            )

        return insights

    # ------------------------------------------------------------------
    # Campaign insights
    # ------------------------------------------------------------------
    def _build_campaign_insights(self, metrics: List[CampaignMetrics]) -> List[Insight]:
        if not metrics:
            return []

        insights: List[Insight] = []

        platform_groups: Dict[str, List[CampaignMetrics]] = {}
        for metric in metrics:
            platform_groups.setdefault(metric.platform, []).append(metric)

        for platform, records in platform_groups.items():
            roi_values = [self._to_float(record.roi_percentage) for record in records]
            conv_rates = [self._to_float(record.conversion_rate) for record in records]
            spend_values = [self._to_float(record.total_spent) for record in records]

            roi_avg = self._safe_average(roi_values) or 0.0
            roi_trend, _ = self._linear_trend(roi_values)
            spend_trend, spend_forecast = self._linear_trend(spend_values)
            summary_data = {
                "platform": platform,
                "avg_roi": roi_avg,
                "trend": roi_trend or 0.0,
                "forecast_spend": spend_forecast or spend_values[-1],
            }

            insights.append(
                Insight(
                    id=self._generate_id(f"roi-{platform}", summary_data),
                    type="prediction",
                    impact="high" if roi_avg >= 20 else "medium",
                    title=f"ROI proiectat pentru {platform}",
                    description=
                        f"ROI-ul mediu pe {platform} este {roi_avg:.1f}% cu un trend de {roi_trend or 0:.1f}%."
                        " Continuă optimizarea campaniei pentru a depăși 25%.",
                    confidence=self._confidence_from_points(roi_values),
                    category="leads",
                    data=summary_data,
                    created_at=datetime.utcnow(),
                )
            )

            best_conversion = max(conv_rates) if conv_rates else 0.0
            conversion_data = {
                "platform": platform,
                "max_conversion_rate": best_conversion,
                "spend_trend": spend_trend or 0.0,
            }
            insights.append(
                Insight(
                    id=self._generate_id(f"conv-{platform}", conversion_data),
                    type="recommendation",
                    impact="high" if best_conversion >= 5 else "medium",
                    title=f"Optimizare conversie {platform}",
                    description=
                        f"Rata maximă de conversie atinsă este {best_conversion:.1f}%."
                        " Scalează creativul și bugetul campaniilor cu performanță ridicată.",
                    confidence=self._confidence_from_points(conv_rates),
                    category="operations",
                    data=conversion_data,
                    created_at=datetime.utcnow(),
                )
            )

        return insights

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _fetch_financial_metrics(
        self, start: date, end: date
    ) -> List[FinancialMetrics]:
        return (
            self.db.query(FinancialMetrics)
            .filter(FinancialMetrics.date >= start)
            .filter(FinancialMetrics.date <= end)
            .order_by(FinancialMetrics.date.asc())
            .all()
        )

    def _fetch_campaign_metrics(
        self, start: date, end: date, platform: Optional[str]
    ) -> List[CampaignMetrics]:
        query = (
            self.db.query(CampaignMetrics)
            .filter(CampaignMetrics.period_start <= end)
            .filter(CampaignMetrics.period_end >= start)
        )
        if platform:
            query = query.filter(CampaignMetrics.platform == platform)
        return query.order_by(CampaignMetrics.period_start.asc()).all()

    @staticmethod
    def _serialize_insight(insight: Insight) -> Dict[str, object]:
        return {
            "id": insight.id,
            "type": insight.type,
            "impact": insight.impact,
            "title": insight.title,
            "description": insight.description,
            "confidence": round(insight.confidence, 1),
            "category": insight.category,
            "data": insight.data,
            "created_at": insight.created_at.isoformat(),
        }

    @staticmethod
    def _compute_summary_metrics(insights: List[Insight]) -> Dict[str, object]:
        total = len(insights)
        high_conf = sum(1 for ins in insights if ins.confidence >= 80)
        critical = sum(1 for ins in insights if ins.impact == "critical")
        categories: Dict[str, int] = {}
        for insight in insights:
            categories[insight.category] = categories.get(insight.category, 0) + 1
        return {
            "total_insights": total,
            "high_confidence_insights": high_conf,
            "critical_alerts": critical,
            "categories": categories,
        }

    @staticmethod
    def _linear_trend(series: List[float]) -> (Optional[float], Optional[float]):
        cleaned = [value for value in series if value is not None]
        if len(cleaned) < 2:
            return None, None

        x_values = list(range(len(cleaned)))
        mean_x = statistics.fmean(x_values)
        mean_y = statistics.fmean(cleaned)

        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, cleaned))
        denominator = sum((x - mean_x) ** 2 for x in x_values)
        if denominator == 0:
            return None, None

        slope = numerator / denominator
        intercept = mean_y - slope * mean_x
        next_index = len(cleaned)
        forecast = intercept + slope * next_index

        first = cleaned[0]
        last = cleaned[-1]
        if first == 0:
            growth_rate = 0.0
        else:
            growth_rate = ((last - first) / abs(first)) * 100

        return growth_rate, max(forecast, 0.0)

    @staticmethod
    def _classify_impact(value: float) -> str:
        if value >= 15:
            return "high"
        if value >= 5:
            return "medium"
        if value <= -5:
            return "critical"
        return "low"

    @staticmethod
    def _confidence_from_points(values: List[float]) -> float:
        count = len([v for v in values if v is not None])
        if count == 0:
            return 0.0
        base = min(1.0, count / 12)
        return round(60 + base * 40, 2)

    @staticmethod
    def _safe_average(values: List[Optional[float]]) -> Optional[float]:
        filtered: List[float] = []
        for value in values:
            if value is None:
                continue
            if isinstance(value, (int, float)) and math.isnan(value):
                continue
            if isinstance(value, (int, float)) and math.isinf(value):
                continue
            filtered.append(float(value))
        if not filtered:
            return None
        return statistics.fmean(filtered)

    @staticmethod
    def _percentage(numerator: float, denominator: float) -> Optional[float]:
        if denominator in (0, None):
            return None
        try:
            return (numerator / denominator) * 100
        except ZeroDivisionError:
            return None

    @staticmethod
    def _to_float(value: Optional[Decimal]) -> float:
        if value is None:
            return 0.0
        if isinstance(value, Decimal):
            return float(value)
        return float(value)

    @staticmethod
    def _generate_id(prefix: str, payload: Optional[Dict[str, object]] = None) -> str:
        base = prefix
        if payload:
            try:
                base += json.dumps(payload, sort_keys=True, default=str)
            except TypeError:
                base += str(payload)
        digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:8]
        return f"{prefix}-{digest}"
