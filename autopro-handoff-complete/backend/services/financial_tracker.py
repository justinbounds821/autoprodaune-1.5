"""Thin-compat wrapper peste FinancialService (modular)."""
from .financial.service import get_financial_service

_ft = None
def _get():
    global _ft
    if _ft is None:
        _ft = get_financial_service()
    return _ft

# păstrează "numele vechi" dacă existau
def track_api_cost(*, provider: str, amount: float, currency: str = "EUR", operation: str = "unknown", meta=None):
    return _get().track_api_cost(provider=provider, amount=amount, currency=currency, operation=operation, meta=meta)

def update_api_cost(cost_id, **fields):
    return _get().update_api_cost(cost_id, **fields)

def delete_api_cost(cost_id):
    return _get().delete_api_cost(cost_id)

def track_revenue(*, source: str, amount: float, currency: str = "EUR", provider=None, meta=None):
    return _get().track_revenue(source=source, amount=amount, currency=currency, provider=provider, meta=meta)

def update_revenue(revenue_id, **fields):
    return _get().update_revenue(revenue_id, **fields)

def delete_revenue(revenue_id):
    return _get().delete_revenue(revenue_id)

def roi_analysis(period: str = "7d"):
    return _get().roi_analysis(period)

def profit_loss_between(period: str = "30d"):
    return _get().profit_loss_between(period)

def dashboard(period: str = "7d"):
    return _get().dashboard(period)

def get_credit_balance(provider: str = None):
    return _get().get_credit_balance(provider)

def update_credit_balance(provider: str, new_balance: float):
    return _get().update_credit_balance(provider, new_balance)

def create_budget_alert(*, alert_name: str, threshold: float, alert_type: str = "budget", message: str = None, meta=None):
    return _get().create_budget_alert(alert_name=alert_name, threshold=threshold, alert_type=alert_type, message=message, meta=meta)

def get_budget_alerts(*, provider: str | None = None):
    return _get().get_budget_alerts(provider=provider)
