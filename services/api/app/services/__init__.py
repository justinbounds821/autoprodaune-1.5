"""
Servicii pentru AutoPro Daune API.

Acest pachet conține toate serviciile business logic pentru aplicație.
"""

# Importuri lazy pentru a evita importurile circulare
__all__ = [
    "FinancialTracker",
    "CostCalculator", 
    "ROICalculator",
    "get_financial_tracker",
    "get_cost_calculator",
    "get_roi_calculator"
]

# Factory functions disponibile direct
def get_financial_tracker():
    """Lazy import pentru FinancialService."""
    from .financial.service import get_financial_service
    return get_financial_service()

def get_cost_calculator():
    """Lazy import pentru CostCalculator."""
    from .cost_calculator import CostCalculator
    return CostCalculator()

def get_roi_calculator():
    """Lazy import pentru ROICalculator."""
    from .roi_calculator import ROICalculator
    from database import get_db
    db = next(get_db())
    return ROICalculator(db)
