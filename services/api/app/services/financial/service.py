from __future__ import annotations
from typing import Any, Dict, Optional, List, Tuple
from datetime import datetime, timezone
import logging

from .utils import period_bounds, normalize_provider

logger = logging.getLogger(__name__)

# === ADAPTEAZĂ DACĂ E CAZUL ===
COSTS_TABLE    = "api_costs"            # tabelul existent
REVENUE_TABLE  = "revenues"
CREDIT_TABLE   = "credit_balances"
ALERTS_TABLE   = "budget_alerts"

class FinancialService:
    """
    Fațadă pe Supabase pentru tracking costuri/revenue + analytics.
    Folosește supabase_service deja existent în proiect.
    """

    def __init__(self, supabase_service):
        self.db = supabase_service

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
        # Use custom dates if provided, otherwise use period
        if date_from and date_to:
            start = f"{date_from}T00:00:00Z"
            end = f"{date_to}T23:59:59Z"
        else:
            start, end = period_bounds(period)
        
        # Construiește filtrele doar dacă avem date valide
        filters = []
        if start:
            filters.append(("gte", "timestamp", start))
        if end:
            filters.append(("lte", "timestamp", end))
            
        costs = self.db._table_select(COSTS_TABLE, "*", filters=filters) or []
        revs = self.db._table_select(REVENUE_TABLE, "*", filters=filters) or []

        total_cost = sum(float(c.get("cost", 0)) for c in costs)
        total_rev  = sum(float(r.get("amount", 0)) for r in revs)
        net_profit = total_rev - total_cost
        roi = ((total_rev - total_cost) / total_cost * 100.0) if total_cost > 0 else 0.0

        return {
            "period": period if not date_from else "custom",
            "start_date": start[:10] if start else None,  # YYYY-MM-DD
            "end_date": end[:10] if end else None,        # YYYY-MM-DD
            "total_costs": round(total_cost, 2),
            "total_revenue": round(total_rev, 2),
            "net_profit": round(net_profit, 2),
            "roi_percentage": round(roi, 2),
            "cost_breakdown": {"api_costs": round(total_cost, 2)},
            "revenue_breakdown": {"all": round(total_rev, 2)},
            "cost_change_percentage": 0.0,
            "revenue_change_percentage": 0.0,
            "profit_change_percentage": 0.0,
            "roi_change_percentage": 0.0,
            "recommendations": self._recommendations(roi, total_cost, total_rev, net_profit)
        }

    def profit_loss_between(self, period: str = "30d") -> Dict[str, Any]:
        data = self.roi_analysis(period)
        pl = data["total_revenue"] - data["total_costs"]
        data["profit_loss"] = round(pl, 2)
        return data

    def dashboard(self, period: str = "7d", date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        # folosește roi_analysis cu date filtering
        return self.roi_analysis(period=period, date_from=date_from, date_to=date_to)

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
