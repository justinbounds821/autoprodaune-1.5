from decimal import Decimal as D
from typing import Dict, Any
from datetime import datetime
from .calculator import CostCalculator
from .rates import CONFIG

def estimate_monthly_costs(usage_plan: Dict[str, Any], calc: CostCalculator | None = None) -> Dict[str, Any]:
    cc = calc or CostCalculator()
    total = D("0")
    breakdown: Dict[str, Any] = {}

    for provider, usage in usage_plan.items():
        if provider == "Pika":
            d = D(usage.get("avg_duration_seconds", 10))
            res = usage.get("resolution", "720p")
            q = usage.get("quality", "high")
            per = cc.calculate_pika_cost(int(d), res, q)["cost"]
            provider_cost = per * D(usage.get("videos_per_day", 0) * 30)
        elif provider == "HeyGen":
            d = D(usage.get("avg_duration_seconds", 30))
            per = cc.calculate_heygen_cost(int(d), usage.get("avatar_type", "default"), usage.get("voice_type", "standard"))["cost"]
            provider_cost = per * D(usage.get("videos_per_day", 0) * 30)
        elif provider in ("TikTok", "Instagram", "YouTube"):
            per = cc.calculate_social_media_posting_cost(provider, usage.get("content_type", "video"))["cost"]
            provider_cost = per * D(usage.get("posts_per_day", 0) * 30)
        else:
            provider_cost = D("0")
        breakdown[provider] = {"monthly_cost": provider_cost, "usage_details": usage}
        total += provider_cost

    taxes = total * CONFIG["tax_rate"]
    overhead = total * CONFIG["overhead_rate"]
    return {
        "total_monthly_cost": total,
        "taxes": taxes,
        "overhead": overhead,
        "grand_total": total + taxes + overhead,
        "cost_breakdown": breakdown,
        "currency": CONFIG["currency"],
        "estimation_period": "monthly",
        "calculation_timestamp": datetime.now().isoformat(),
    }

def estimate_budget_requirements(target_roi: D, expected_revenue: D, time_period_days: int = 30) -> Dict[str, Any]:
    if target_roi <= D("-100"):
        raise ValueError("ROI țintă nu poate fi ≤ -100%")
    if expected_revenue < 0 or time_period_days <= 0:
        raise ValueError("Parametri invalidi")

    roi_dec = target_roi / D("100")
    max_budget = expected_revenue / (D("1") + roi_dec)
    daily_budget = max_budget / D(time_period_days)
    dist = {
        "Pika": max_budget * D("0.40"),
        "HeyGen": max_budget * D("0.20"),
        "TikTok": max_budget * D("0.15"),
        "Instagram": max_budget * D("0.15"),
        "YouTube": max_budget * D("0.05"),
        "Other": max_budget * D("0.05"),
    }
    return {
        "target_roi_percentage": target_roi,
        "expected_revenue": expected_revenue,
        "max_budget": max_budget,
        "daily_budget": daily_budget,
        "time_period_days": time_period_days,
        "budget_distribution": dist,
        "currency": CONFIG["currency"],
        "calculation_timestamp": datetime.now().isoformat(),
    }
