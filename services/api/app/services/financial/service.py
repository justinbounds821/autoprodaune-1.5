from __future__ import annotations
from typing import Any, Dict, Optional, List, Tuple
from collections import defaultdict
from statistics import mean, pstdev
from datetime import datetime, timezone
import json
import logging

from .utils import period_bounds, normalize_provider

logger = logging.getLogger(__name__)

# === ADAPTEAZĂ DACĂ E CAZUL ===
COSTS_TABLE    = "api_costs"            # tabelul existent
REVENUE_TABLE  = "revenues"
CREDIT_TABLE   = "credit_balances"
ALERTS_TABLE   = "budget_alerts"
COST_CATEGORY_TABLE = "cost_categories"
INVOICE_TABLE = "invoices"

DEFAULT_COST_CATEGORIES = [
    {
        "slug": "ai_automation",
        "name": "AI & Automation",
        "description": "Costuri pentru modele AI, generare video și automatizări",
        "budget_cap": 2500.0,
        "color": "#2563eb",
    },
    {
        "slug": "marketing",
        "name": "Marketing & Paid Media",
        "description": "Campanii plătite, reclame și funnel automation",
        "budget_cap": 1800.0,
        "color": "#f97316",
    },
    {
        "slug": "operations",
        "name": "Operațional",
        "description": "Licențe, infrastructură, suport și tool-uri back-office",
        "budget_cap": 1200.0,
        "color": "#16a34a",
    },
    {
        "slug": "referrals",
        "name": "Referral Rewards",
        "description": "Bonusuri și comisioane pentru parteneri și clienți",
        "budget_cap": 1500.0,
        "color": "#9333ea",
    },
]

class FinancialService:
    """
    Fațadă pe Supabase pentru tracking costuri/revenue + analytics.
    Folosește supabase_service deja existent în proiect.
    """

    def __init__(self, supabase_service):
        self.db = supabase_service

    # ----------------- HELPERE INTERNE -----------------
    def _prepare_period_filters(
        self,
        period: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[str], List[Tuple[str, str, Any]]]:
        """Returnează start/end ISO și filtre pentru interogările Supabase."""

        if date_from and date_to:
            start = f"{date_from}T00:00:00Z"
            end = f"{date_to}T23:59:59Z"
        else:
            start, end = period_bounds(period)

        filters: List[Tuple[str, str, Any]] = []
        if start:
            filters.append(("gte", "timestamp", start))
        if end:
            filters.append(("lte", "timestamp", end))
        return start, end, filters

    @staticmethod
    def _parse_metadata(raw: Any) -> Dict[str, Any]:
        """Normalizează metadata venită fie ca dict, fie ca JSON string."""

        if not raw:
            return {}
        if isinstance(raw, dict):
            return raw
        if isinstance(raw, str):
            try:
                data = json.loads(raw)
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass
        return {}

    @staticmethod
    def _safe_div(numerator: float, denominator: float) -> float:
        return numerator / denominator if denominator else 0.0

    def _build_daily_series(
        self,
        costs: List[Dict[str, Any]],
        revenues: List[Dict[str, Any]],
    ) -> List[Dict[str, float]]:
        """Agregă costuri/venituri pe zile pentru grafice și forecast."""

        daily = defaultdict(lambda: {"revenue": 0.0, "costs": 0.0})

        for cost in costs:
            try:
                amount = float(cost.get("cost") or cost.get("amount") or 0.0)
            except (TypeError, ValueError):
                amount = 0.0
            timestamp = cost.get("timestamp") or ""
            day = timestamp[:10] if timestamp else datetime.now(timezone.utc).date().isoformat()
            daily[day]["costs"] += amount

        for rev in revenues:
            try:
                amount = float(rev.get("amount") or 0.0)
            except (TypeError, ValueError):
                amount = 0.0
            timestamp = rev.get("timestamp") or ""
            day = timestamp[:10] if timestamp else datetime.now(timezone.utc).date().isoformat()
            daily[day]["revenue"] += amount

        series = []
        for day in sorted(daily.keys()):
            revenue = daily[day]["revenue"]
            costs_val = daily[day]["costs"]
            series.append(
                {
                    "date": day,
                    "revenue": round(revenue, 2),
                    "costs": round(costs_val, 2),
                    "profit": round(revenue - costs_val, 2),
                }
            )
        return series

    def _get_cost_category(self, cost: Dict[str, Any]) -> str:
        meta = self._parse_metadata(cost.get("metadata") or cost.get("meta"))
        category = (
            meta.get("category")
            or meta.get("cost_category")
            or cost.get("operation")
            or cost.get("provider")
            or "other"
        )
        return str(category).strip() or "other"

    def _get_revenue_category(self, revenue: Dict[str, Any]) -> str:
        meta = self._parse_metadata(revenue.get("metadata") or revenue.get("meta"))
        category = meta.get("category") or meta.get("revenue_category") or revenue.get("source")
        return str(category or "other").strip() or "other"

    # ----------------- COSTURI API -----------------

    # ----------------- COSTURI API -----------------
    def track_api_cost(self, *, provider: str, amount: float, currency: str = "EUR",
                       operation: str = "unknown", meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        provider = normalize_provider(provider)
        return self.db.financial_add_event(
            kind="cost", 
            amount=amount, 
            provider=provider, 
            operation=operation,
            extra_data=meta or {}
        )

    def update_api_cost(self, cost_id: Any, **fields) -> Dict[str, Any]:
        if "provider" in fields:
            fields["provider"] = normalize_provider(fields["provider"])
        fields["timestamp"] = datetime.now(timezone.utc).isoformat()
        return self.db._table_update_eq(COSTS_TABLE, "id", cost_id, fields)

    def delete_api_cost(self, cost_id: Any) -> bool:
        return bool(self.db._table_delete_eq(COSTS_TABLE, "id", cost_id))

    # ----------------- VENITURI -----------------
    def track_revenue(self, *, source: str, amount: float, currency: str = "EUR",
                      provider: Optional[str] = None, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        provider = normalize_provider(provider) or source
        return self.db.financial_add_event(
            kind="revenue", 
            amount=amount, 
            provider=provider,
            operation="revenue",
            extra_data=meta or {}
        )

    def update_revenue(self, revenue_id: Any, **fields) -> Dict[str, Any]:
        if "provider" in fields:
            fields["provider"] = normalize_provider(fields["provider"])
        fields["timestamp"] = datetime.now(timezone.utc).isoformat()
        return self.db._table_update_eq(REVENUE_TABLE, "id", revenue_id, fields)

    def delete_revenue(self, revenue_id: Any) -> bool:
        return bool(self.db._table_delete_eq(REVENUE_TABLE, "id", revenue_id))

    # ----------------- CREDIT BALANCE -----------------
    def get_credit_balance(self, provider: str = None) -> Dict[str, Any] | None:
        filters = []
        if provider:
            filters.append(("eq", "provider", normalize_provider(provider)))
        rows = self.db._table_select(CREDIT_TABLE, "*", filters=filters, limit=1) or []
        return rows[0] if rows else None

    def update_credit_balance(self, provider: str, new_balance: float, credit_type: str = "credits") -> Dict[str, Any]:
        provider = normalize_provider(provider)
        payload = {
            "provider": provider,
            "credit_type": credit_type,
            "current_balance": float(new_balance),
            "total_allocated": new_balance,  # simplificat
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        existing = self.get_credit_balance(provider)
        if existing:
            return self.db._table_update_eq(CREDIT_TABLE, "provider", provider, payload)
        else:
            return self.db._table_insert(CREDIT_TABLE, payload)

    # ----------------- ALERTARE BUGET -----------------
    def create_budget_alert(self, *, alert_name: str, threshold: float, alert_type: str = "budget", 
                           message: str = None, meta: Dict[str, Any] | None = None):
        row = {
            "alert_name": alert_name,
            "alert_type": alert_type,
            "threshold_value": float(threshold),
            "message": message,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "current_value": 0,
            "is_triggered": 0,
        }
        return self.db._table_insert(ALERTS_TABLE, row)

    def get_budget_alerts(self, *, provider: str | None = None) -> List[Dict[str, Any]]:
        flt = []
        if provider:
            flt.append(("eq", "alert_name", provider))  # căutare în numele alertei
        rows = self.db._table_select(ALERTS_TABLE, "*", filters=flt) or []
        # sortare după updated_at desc
        rows.sort(key=lambda r: r.get("updated_at") or r.get("created_at") or "", reverse=True)
        return rows

    # ----------------- ANALITICE -----------------
    def roi_analysis(self, period: str = "7d", date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        start, end, filters = self._prepare_period_filters(period, date_from, date_to)

        costs = self.db._table_select(COSTS_TABLE, "*", filters=filters) or []
        revs = self.db._table_select(REVENUE_TABLE, "*", filters=filters) or []

        total_cost = sum(float(c.get("cost", 0) or 0.0) for c in costs)
        total_rev = sum(float(r.get("amount", 0) or 0.0) for r in revs)
        net_profit = total_rev - total_cost
        roi = ((total_rev - total_cost) / total_cost * 100.0) if total_cost > 0 else 0.0

        cost_by_category: Dict[str, float] = defaultdict(float)
        cost_by_provider: Dict[str, float] = defaultdict(float)
        revenue_by_category: Dict[str, float] = defaultdict(float)
        revenue_by_source: Dict[str, float] = defaultdict(float)

        for cost in costs:
            amount = float(cost.get("cost") or cost.get("amount") or 0.0)
            provider = normalize_provider(cost.get("provider") or "Other")
            category = self._get_cost_category(cost)
            cost_by_category[category] += amount
            cost_by_provider[provider or "Other"] += amount

        for rev in revs:
            amount = float(rev.get("amount") or 0.0)
            source = rev.get("source") or rev.get("provider") or "Other"
            category = self._get_revenue_category(rev)
            revenue_by_source[source] += amount
            revenue_by_category[category] += amount

        daily_series = self._build_daily_series(costs, revs)
        if daily_series:
            cost_change = self._safe_div(
                daily_series[-1]["costs"] - daily_series[0]["costs"],
                abs(daily_series[0]["costs"]) or 1.0,
            ) * 100.0
            revenue_change = self._safe_div(
                daily_series[-1]["revenue"] - daily_series[0]["revenue"],
                abs(daily_series[0]["revenue"]) or 1.0,
            ) * 100.0
            profit_change = self._safe_div(
                daily_series[-1]["profit"] - daily_series[0]["profit"],
                abs(daily_series[0]["profit"]) or 1.0,
            ) * 100.0
        else:
            cost_change = revenue_change = profit_change = 0.0

        return {
            "period": period if not date_from else "custom",
            "start_date": start[:10] if start else None,  # YYYY-MM-DD
            "end_date": end[:10] if end else None,        # YYYY-MM-DD
            "total_costs": round(total_cost, 2),
            "total_revenue": round(total_rev, 2),
            "net_profit": round(net_profit, 2),
            "roi_percentage": round(roi, 2),
            "cost_breakdown": {
                "by_category": {k: round(v, 2) for k, v in cost_by_category.items()},
                "by_provider": {k: round(v, 2) for k, v in cost_by_provider.items()},
            },
            "revenue_breakdown": {
                "by_category": {k: round(v, 2) for k, v in revenue_by_category.items()},
                "by_source": {k: round(v, 2) for k, v in revenue_by_source.items()},
            },
            "timeline": daily_series,
            "cost_change_percentage": round(cost_change, 2),
            "revenue_change_percentage": round(revenue_change, 2),
            "profit_change_percentage": round(profit_change, 2),
            "roi_change_percentage": 0.0,
            "recommendations": self._recommendations(roi, total_cost, total_rev, net_profit)
        }

    def profit_loss_between(self, period: str = "30d") -> Dict[str, Any]:
        return self.profit_loss_report(period=period)

    def dashboard(self, period: str = "7d", date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        analysis = self.roi_analysis(period=period, date_from=date_from, date_to=date_to)
        alerts = self.get_budget_alerts()

        timeline = analysis.get("timeline", []) or []
        avg_profit = mean([row["profit"] for row in timeline]) if timeline else 0.0

        top_costs = sorted(
            (analysis.get("cost_breakdown", {}).get("by_provider", {}) or {}).items(),
            key=lambda item: item[1],
            reverse=True,
        )
        top_revenue = sorted(
            (analysis.get("revenue_breakdown", {}).get("by_source", {}) or {}).items(),
            key=lambda item: item[1],
            reverse=True,
        )

        analysis.update(
            {
                "profit_margin": round(self._safe_div(analysis.get("net_profit", 0.0), analysis.get("total_revenue", 0.0)) * 100, 2),
                "average_daily_profit": round(avg_profit, 2),
                "top_cost_providers": [
                    {"provider": provider, "amount": round(amount, 2)}
                    for provider, amount in top_costs[:5]
                ],
                "top_revenue_sources": [
                    {"source": source, "amount": round(amount, 2)}
                    for source, amount in top_revenue[:5]
                ],
                "active_alerts": alerts[:5],
                "cost_categories": analysis.get("cost_breakdown", {}).get("by_category", {}),
                "revenue_categories": analysis.get("revenue_breakdown", {}).get("by_category", {}),
            }
        )

        return analysis

    # ----------------- AGREGĂRI AVANSATE -----------------

    def financial_breakdown(
        self,
        period: str = "30d",
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        start, end, filters = self._prepare_period_filters(period, date_from, date_to)
        costs = self.db._table_select(COSTS_TABLE, "*", filters=filters) or []
        revs = self.db._table_select(REVENUE_TABLE, "*", filters=filters) or []

        cost_by_category: Dict[str, float] = defaultdict(float)
        cost_by_provider: Dict[str, float] = defaultdict(float)
        revenue_by_category: Dict[str, float] = defaultdict(float)
        revenue_by_source: Dict[str, float] = defaultdict(float)

        for cost in costs:
            amount = float(cost.get("cost") or cost.get("amount") or 0.0)
            cost_by_category[self._get_cost_category(cost)] += amount
            cost_by_provider[normalize_provider(cost.get("provider") or "Other") or "Other"] += amount

        for rev in revs:
            amount = float(rev.get("amount") or 0.0)
            revenue_by_category[self._get_revenue_category(rev)] += amount
            revenue_by_source[rev.get("source") or rev.get("provider") or "Other"] += amount

        daily_series = self._build_daily_series(costs, revs)

        cumulative_profit = 0.0
        timeline = []
        for entry in daily_series:
            cumulative_profit += entry["profit"]
            enriched = dict(entry)
            enriched["cumulative_profit"] = round(cumulative_profit, 2)
            timeline.append(enriched)

        total_cost = sum(cost_by_category.values())
        total_revenue = sum(revenue_by_category.values())
        profit = total_revenue - total_cost

        top_cost_items = sorted(costs, key=lambda c: float(c.get("cost") or 0.0), reverse=True)[:10]
        top_revenue_items = sorted(revs, key=lambda r: float(r.get("amount") or 0.0), reverse=True)[:10]

        return {
            "period": period if not date_from else "custom",
            "start_date": start[:10] if start else None,
            "end_date": end[:10] if end else None,
            "costs": {
                "total": round(total_cost, 2),
                "by_category": {k: round(v, 2) for k, v in cost_by_category.items()},
                "by_provider": {k: round(v, 2) for k, v in cost_by_provider.items()},
                "top": [
                    {
                        "id": item.get("id"),
                        "provider": item.get("provider"),
                        "operation": item.get("operation"),
                        "category": self._get_cost_category(item),
                        "amount": round(float(item.get("cost") or 0.0), 2),
                        "timestamp": item.get("timestamp"),
                    }
                    for item in top_cost_items
                ],
            },
            "revenue": {
                "total": round(total_revenue, 2),
                "by_category": {k: round(v, 2) for k, v in revenue_by_category.items()},
                "by_source": {k: round(v, 2) for k, v in revenue_by_source.items()},
                "top": [
                    {
                        "id": item.get("id"),
                        "source": item.get("source"),
                        "category": self._get_revenue_category(item),
                        "amount": round(float(item.get("amount") or 0.0), 2),
                        "timestamp": item.get("timestamp"),
                    }
                    for item in top_revenue_items
                ],
            },
            "timeline": timeline,
            "profitability": {
                "net_profit": round(profit, 2),
                "roi": round(self._safe_div(profit, total_cost) * 100, 2),
                "profit_margin": round(self._safe_div(profit, total_revenue) * 100, 2),
            },
        }

    def financial_forecast(
        self,
        period: str = "60d",
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        start, end, filters = self._prepare_period_filters(period, date_from, date_to)
        costs = self.db._table_select(COSTS_TABLE, "*", filters=filters) or []
        revs = self.db._table_select(REVENUE_TABLE, "*", filters=filters) or []

        series = self._build_daily_series(costs, revs)
        if not series:
            return {
                "period": period if not date_from else "custom",
                "start_date": start[:10] if start else None,
                "end_date": end[:10] if end else None,
                "averages": {"revenue": 0.0, "costs": 0.0, "profit": 0.0},
                "growth_rates": {"revenue": 0.0, "costs": 0.0, "profit": 0.0},
                "forecasts": {},
                "confidence": 0.35,
                "series": series,
            }

        revenue_values = [row["revenue"] for row in series]
        cost_values = [row["costs"] for row in series]
        profit_values = [row["profit"] for row in series]

        avg_revenue = mean(revenue_values)
        avg_cost = mean(cost_values)
        avg_profit = mean(profit_values)

        def average_change(values: List[float]) -> float:
            if len(values) < 2:
                return 0.0
            deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
            return mean(deltas)

        revenue_change = average_change(revenue_values)
        cost_change = average_change(cost_values)
        profit_change = average_change(profit_values)

        def project_future(last_value: float, avg_delta: float, days: int) -> float:
            total = 0.0
            current = last_value
            for _ in range(days):
                current = max(current + avg_delta, 0.0)
                total += current
            return round(total, 2)

        horizons = {"7d": 7, "30d": 30, "90d": 90}
        forecasts = {}
        for label, days in horizons.items():
            revenue_projection = project_future(revenue_values[-1], revenue_change, days)
            cost_projection = project_future(cost_values[-1], cost_change, days)
            profit_projection = revenue_projection - cost_projection
            forecasts[label] = {
                "revenue": round(revenue_projection, 2),
                "costs": round(cost_projection, 2),
                "profit": round(profit_projection, 2),
                "trend": "up" if profit_projection >= 0 else "down",
            }

        revenue_volatility = pstdev(revenue_values) if len(revenue_values) > 1 else 0.0
        volatility_factor = self._safe_div(revenue_volatility, avg_revenue or 1.0)
        confidence = max(0.35, min(0.95, 1 / (1 + volatility_factor)))

        growth_rates = {
            "revenue": round(self._safe_div(revenue_change, avg_revenue or 1.0) * 100, 2),
            "costs": round(self._safe_div(cost_change, avg_cost or 1.0) * 100, 2),
            "profit": round(self._safe_div(profit_change, avg_profit or 1.0) * 100, 2),
        }

        return {
            "period": period if not date_from else "custom",
            "start_date": start[:10] if start else None,
            "end_date": end[:10] if end else None,
            "averages": {
                "revenue": round(avg_revenue, 2),
                "costs": round(avg_cost, 2),
                "profit": round(avg_profit, 2),
            },
            "growth_rates": growth_rates,
            "forecasts": forecasts,
            "confidence": round(confidence, 2),
            "series": series,
        }

    def profit_loss_report(
        self,
        period: str = "30d",
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        analysis = self.roi_analysis(period=period, date_from=date_from, date_to=date_to)
        timeline = analysis.get("timeline", []) or []

        profits = [row["profit"] for row in timeline]
        avg_profit = mean(profits) if profits else 0.0
        best_day = max(timeline, key=lambda row: row["profit"], default=None)
        worst_day = min(timeline, key=lambda row: row["profit"], default=None)
        volatility = pstdev(profits) if len(profits) > 1 else 0.0

        cumulative = []
        running_profit = 0.0
        for row in timeline:
            running_profit += row["profit"]
            enriched = dict(row)
            enriched["cumulative_profit"] = round(running_profit, 2)
            cumulative.append(enriched)

        analysis.update(
            {
                "daily_metrics": cumulative,
                "avg_daily_profit": round(avg_profit, 2),
                "best_day_profit": best_day["profit"] if best_day else 0.0,
                "worst_day_profit": worst_day["profit"] if worst_day else 0.0,
                "profit_volatility": round(volatility, 2),
                "cost_categories": analysis.get("cost_breakdown", {}).get("by_category", {}),
                "revenue_categories": analysis.get("revenue_breakdown", {}).get("by_category", {}),
            }
        )

        return analysis

    # ----------------- MANAGEMENT CATEGORII COST -----------------

    def list_cost_categories(self) -> List[Dict[str, Any]]:
        categories = self.db._table_select(COST_CATEGORY_TABLE, "*", order=("name", False)) or []
        if categories:
            return categories
        return [dict(cat, is_default=True) for cat in DEFAULT_COST_CATEGORIES]

    def create_cost_category(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        name = payload.get("name")
        if not name:
            raise ValueError("Category name is required")

        slug = payload.get("slug") or name.lower().strip().replace(" ", "_")
        category_data = {
            "slug": slug,
            "name": name,
            "description": payload.get("description"),
            "budget_cap": float(payload.get("budget_cap") or 0.0),
            "color": payload.get("color") or "#64748b",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return self.db._table_insert(COST_CATEGORY_TABLE, category_data)

    def update_cost_category(self, slug: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            key: value
            for key, value in {
                "name": payload.get("name"),
                "description": payload.get("description"),
                "budget_cap": float(payload.get("budget_cap")) if payload.get("budget_cap") is not None else None,
                "color": payload.get("color"),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }.items()
            if value is not None
        }
        if not payload:
            raise ValueError("No fields provided for update")
        return self.db._table_update_eq(COST_CATEGORY_TABLE, "slug", slug, payload)

    def delete_cost_category(self, slug: str) -> Dict[str, Any]:
        return self.db._table_delete_eq(COST_CATEGORY_TABLE, "slug", slug)

    def assign_cost_category(self, cost_id: Any, category_slug: str) -> Dict[str, Any]:
        cost_rows = self.db._table_select(COSTS_TABLE, "*", filters=[("eq", "id", cost_id)]) or []
        if not cost_rows:
            raise ValueError("Cost entry not found")

        metadata = self._parse_metadata(cost_rows[0].get("metadata"))
        metadata["category"] = category_slug

        payload = {
            "metadata": metadata,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return self.db._table_update_eq(COSTS_TABLE, "id", cost_id, payload)

    # ----------------- EXPORTURI -----------------

    def export_financial_data(
        self,
        period: str = "30d",
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        include_costs: bool = True,
        include_revenue: bool = True,
    ) -> Dict[str, Any]:
        start, end, filters = self._prepare_period_filters(period, date_from, date_to)
        costs = self.db._table_select(COSTS_TABLE, "*", filters=filters) if include_costs else []
        revenues = self.db._table_select(REVENUE_TABLE, "*", filters=filters) if include_revenue else []
        metrics = self.roi_analysis(period=period, date_from=date_from, date_to=date_to)

        return {
            "period": period if not date_from else "custom",
            "start_date": start[:10] if start else None,
            "end_date": end[:10] if end else None,
            "costs": costs or [],
            "revenues": revenues or [],
            "metrics": metrics,
        }

    def generate_invoice_pdf(self, invoice_id: str) -> Tuple[bytes, Dict[str, Any]]:
        invoice_rows = self.db._table_select(INVOICE_TABLE, "*", filters=[("eq", "id", invoice_id)]) or []
        if not invoice_rows:
            raise ValueError("Invoice not found")
        invoice = invoice_rows[0]
        pdf_bytes = self._render_invoice_pdf(invoice)
        return pdf_bytes, invoice

    def _render_invoice_pdf(self, invoice: Dict[str, Any]) -> bytes:
        """Generează un PDF simplificat pentru factură fără dependențe externe."""

        def sanitize(text: Any) -> str:
            value = str(text or "")
            return (
                value
                .replace("\\", "\\\\")
                .replace("(", "\\(")
                .replace(")", "\\)")
                .encode("latin-1", "ignore")
                .decode("latin-1")
            )

        lines = [
            f"Factura #{invoice.get('number') or invoice.get('id')}",
            f"Client: {invoice.get('client_name', 'N/A')}",
            f"Email: {invoice.get('client_email', 'N/A')}",
            f"Adresă: {invoice.get('client_address', 'N/A')}",
            "",
            f"Data emiterii: {invoice.get('created_at', '')}",
            f"Scadență: {invoice.get('due_date', '')}",
            "",
            "Detalii articole:",
        ]

        for item in invoice.get("items", []) or []:
            label = item.get("description") or item.get("name") or "Serviciu"
            qty = item.get("quantity", 1)
            total = float(item.get("total") or 0.0)
            lines.append(f" - {label} x{qty}: {total:.2f} EUR")

        lines.extend(
            [
                "",
                f"Subtotal: {float(invoice.get('subtotal') or 0.0):.2f} EUR",
                f"Taxe: {float(invoice.get('tax_amount') or 0.0):.2f} EUR",
                f"Total: {float(invoice.get('total') or 0.0):.2f} EUR",
            ]
        )

        content_lines = ["BT", "/F1 12 Tf", "72 800 Td"]
        for line in lines:
            content_lines.append(f"({sanitize(line)}) Tj")
            content_lines.append("0 -18 Td")
        content_lines.append("ET")
        content = "\n".join(content_lines)
        content_bytes = content.encode("latin-1")

        objects: List[str] = []

        def add_object(obj: str) -> None:
            objects.append(obj + "\n")

        add_object("1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj")
        add_object("2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj")
        add_object("3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj")
        add_object(f"4 0 obj << /Length {len(content_bytes)} >> stream\n{content}\nendstream endobj")
        add_object("5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj")

        pdf_body = "%PDF-1.4\n"
        offsets = [len(pdf_body.encode("latin-1"))]
        for obj in objects:
            pdf_body += obj
            offsets.append(len(pdf_body.encode("latin-1")))

        xref_start = len(pdf_body.encode("latin-1"))
        pdf_body += "xref\n0 6\n0000000000 65535 f \n"
        current_offset = 0
        for idx, obj in enumerate(objects, start=1):
            # compute offset for object idx
            if idx == 1:
                current_offset = offsets[0]
            else:
                current_offset = offsets[idx - 1]
            pdf_body += f"{current_offset:010} 00000 n \n"
        pdf_body += "trailer << /Size 6 /Root 1 0 R >>\n"
        pdf_body += f"startxref\n{xref_start}\n%%EOF"

        return pdf_body.encode("latin-1")

    def _recommendations(self, roi_pct: float, total_costs: float, total_revenue: float, net_profit: float) -> List[str]:
        rec = []
        if roi_pct < 0:
            rec.append("ROI negativ: revizuiți cheltuielile.")
        elif roi_pct < 10:
            rec.append("ROI scăzut: optimizați costurile / creșteți conversiile.")
        if total_costs > total_revenue:
            rec.append("Costurile depășesc veniturile: reduceți cheltuielile.")
        if net_profit < 0:
            rec.append("Profit negativ: analizați toate categoriile de cost.")
        if roi_pct > 50:
            rec.append("ROI excelent: scalați investițiile care performează.")
        if not rec:
            rec.append("Metricile sunt ok; continuați execuția curentă.")
        return rec

def get_financial_service() -> FinancialService:
    """Factory function pentru a obține o instanță FinancialService."""
    from ..supabase_client import get_supabase_service_instance
    return FinancialService(get_supabase_service_instance())
