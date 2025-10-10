"""
Scheme Pydantic pentru AutoPro Daune API.

Acest pachet conține toate schemele pentru validarea și serializarea datelor.
"""

from .financial import (
    # API Cost schemas
    APICostCreate,
    APICostResponse,
    
    # Revenue schemas
    RevenueCreate,
    RevenueResponse,
    
    # Financial Metrics schemas
    FinancialMetricsCreate,
    FinancialMetricsResponse,
    
    # Campaign Metrics schemas
    CampaignMetricsCreate,
    CampaignMetricsResponse,
    
    # Credit Balance schemas
    CreditBalanceResponse,
    CreditBalanceUpdate,
    
    # Budget Alert schemas
    BudgetAlertCreate,
    BudgetAlertResponse,
    
    # Dashboard schemas
    FinancialDashboardResponse,
    
    # Analysis schemas
    ROIAnalysisRequest,
    ROIAnalysisResponse,
    ProfitLossRequest,
    ProfitLossResponse,
    
    # Bulk operation schemas
    BulkAPICostCreate,
    BulkRevenueCreate,
    
    # Statistics schemas
    FinancialStatsResponse,
    
    # Export schemas
    ExportRequest,
    ExportResponse
)

from .ai_insights import (
    AIInsightData,
    AIInsightMetrics,
    AIInsightsContext,
    AIInsightsFilters,
    AIInsightsReportRequest,
    AIInsightsResponse,
)

__all__ = [
    # API Cost schemas
    "APICostCreate",
    "APICostResponse",
    
    # Revenue schemas
    "RevenueCreate", 
    "RevenueResponse",
    
    # Financial Metrics schemas
    "FinancialMetricsCreate",
    "FinancialMetricsResponse",
    
    # Campaign Metrics schemas
    "CampaignMetricsCreate",
    "CampaignMetricsResponse",

    # AI Insights
    "AIInsightData",
    "AIInsightMetrics",
    "AIInsightsContext",
    "AIInsightsFilters",
    "AIInsightsReportRequest",
    "AIInsightsResponse",

    # Credit Balance schemas
    "CreditBalanceResponse",
    "CreditBalanceUpdate",
    
    # Budget Alert schemas
    "BudgetAlertCreate",
    "BudgetAlertResponse",
    
    # Dashboard schemas
    "FinancialDashboardResponse",
    
    # Analysis schemas
    "ROIAnalysisRequest",
    "ROIAnalysisResponse",
    "ProfitLossRequest",
    "ProfitLossResponse",
    
    # Bulk operation schemas
    "BulkAPICostCreate",
    "BulkRevenueCreate",
    
    # Statistics schemas
    "FinancialStatsResponse",
    
    # Export schemas
    "ExportRequest",
    "ExportResponse"
]
