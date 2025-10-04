from decimal import Decimal as D
from typing import Dict, Any
from .estimators import estimate_monthly_costs

def optimize_costs(current_usage: Dict[str, Any], budget_limit: D) -> Dict[str, Any]:
    est = estimate_monthly_costs(current_usage)
    total = est["total_monthly_cost"]

    if total <= budget_limit:
        return {
            "status": "within_budget",
            "current_cost": total,
            "budget_limit": budget_limit,
            "remaining_budget": budget_limit - total,
            "suggestions": ["Costurile curente sunt în limitele bugetului."],
        }

    sug = []
    if "Pika" in current_usage:
        if current_usage["Pika"].get("quality") == "high":
            sug.append({"provider": "Pika", "suggestion": "Reduce quality high→medium (~30%)", "potential_savings": total * D("0.15")})
        if current_usage["Pika"].get("resolution") == "4K":
            sug.append({"provider": "Pika", "suggestion": "4K→1080p (~50%)", "potential_savings": total * D("0.25")})
    if "HeyGen" in current_usage and current_usage["HeyGen"].get("avatar_type") == "premium":
        sug.append({"provider": "HeyGen", "suggestion": "Avatar premium→default (~40%)", "potential_savings": total * D("0.20")})

    sug += [
        {"provider": "General", "suggestion": "Caching pentru a reduce apelurile duplicate", "potential_savings": total * D("0.10")},
        {"provider": "General", "suggestion": "Scurtează durata video-urilor", "potential_savings": total * D("0.15")},
    ]

    savings = sum(s["potential_savings"] for s in sug)
    return {
        "status": "over_budget",
        "current_cost": total,
        "budget_limit": budget_limit,
        "excess_cost": total - budget_limit,
        "optimization_suggestions": sug,
        "total_potential_savings": savings,
        "new_estimated_cost": total - savings,
        "currency": "USD",
    }
