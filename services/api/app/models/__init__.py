"""
Modele de bază de date pentru AutoPro Daune API.

Acest pachet conține toate modelele SQLAlchemy pentru aplicație.
"""

from .financial import (
    Base,
    APICost,
    Revenue,
    FinancialMetrics,
    CampaignMetrics,
    CreditBalance,
    BudgetAlert,
    ProviderType,
    OperationType,
    RevenueSource,
    AlertType,
)
from .automation import (
    AutomationRule,
    AutomationCondition,
    AutomationAction,
    AutomationRunHistory,
    NotificationPreference,
)

__all__ = [
    "Base",
    "APICost",
    "Revenue", 
    "FinancialMetrics",
    "CampaignMetrics",
    "CreditBalance",
    "BudgetAlert",
    "ProviderType",
    "OperationType",
    "RevenueSource",
    "AlertType",
    "AutomationRule",
    "AutomationCondition",
    "AutomationAction",
    "AutomationRunHistory",
    "NotificationPreference",
]
