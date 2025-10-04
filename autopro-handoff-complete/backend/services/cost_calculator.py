"""
Wrapper compat pentru vechiul `cost_calculator.py`.
Expune aceeași clasă/nume folosite în codul existent.
"""
from .financial.costs import CostCalculator, estimate_monthly_costs, estimate_budget_requirements, optimize_costs
from .financial.costs import CostCategory  # dacă ai importuri vechi

__all__ = [
    "CostCalculator",
    "estimate_monthly_costs",
    "estimate_budget_requirements",
    "optimize_costs",
    "CostCategory",
]

# opțional: factory compat
def get_cost_calculator() -> "CostCalculator":
    return CostCalculator()
