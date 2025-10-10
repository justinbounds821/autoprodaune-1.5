"""
REAL Financial Routes - AutoPro Daune
All calculations from database
NO MOCKS
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from datetime import datetime
from ..middleware.jwt_auth import get_current_user, get_current_admin, CurrentUser
from ..services.financial_service_real import get_financial_service, FinancialService
from fastapi.responses import StreamingResponse
import io

router = APIRouter(prefix="/api/financial", tags=["financial-real"])

@router.get("/revenue")
async def get_revenue(
    period: str = Query("30d", pattern="^(7d|30d|90d)$"),
    current_user: CurrentUser = Depends(get_current_user),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Get revenue summary - REAL calculation from database
    Period: 7d, 30d, or 90d
    """
    return await financial_service.get_revenue_summary(
        user_id=current_user.id,
        period=period
    )

@router.get("/costs")
async def get_costs(
    period: str = Query("30d", pattern="^(7d|30d|90d)$"),
    current_user: CurrentUser = Depends(get_current_user),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Get cost breakdown - REAL calculation from database
    Includes API costs, infrastructure, marketing
    """
    return await financial_service.get_cost_breakdown(
        period=period
    )

@router.get("/profit")
async def get_profit(
    period: str = Query("30d", pattern="^(7d|30d|90d)$"),
    current_user: CurrentUser = Depends(get_current_user),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Get profit calculation - REAL (revenue - costs)
    Includes profit margin and ROI
    """
    return await financial_service.get_profit(period=period)

@router.get("/dashboard")
async def get_financial_dashboard(
    current_user: CurrentUser = Depends(get_current_user),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Get complete financial dashboard metrics
    REAL-TIME data from database
    """
    return await financial_service.get_dashboard_metrics(
        user_id=current_user.id
    )

@router.post("/transaction")
async def create_transaction(
    type: str,
    category: str,
    amount: float,
    description: Optional[str] = None,
    source: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Create financial transaction
    Type: revenue, cost, refund
    """
    return await financial_service.create_transaction(
        user_id=current_user.id,
        type=type,
        category=category,
        amount=amount,
        description=description,
        source=source
    )

@router.post("/api-cost")
async def track_api_cost(
    provider: str,
    operation_type: str,
    units_consumed: float,
    cost_per_unit: float,
    total_cost: float,
    current_user: CurrentUser = Depends(get_current_admin),  # Admin only
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Track API usage cost
    Admin only
    """
    return await financial_service.track_api_cost(
        provider=provider,
        operation_type=operation_type,
        units_consumed=units_consumed,
        cost_per_unit=cost_per_unit,
        total_cost=total_cost
    )

@router.get("/export/csv")
async def export_financial_csv(
    type: Optional[str] = Query(None, pattern="^(revenue|cost|refund)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: CurrentUser = Depends(get_current_user),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Export financial data to CSV
    Returns downloadable CSV file
    """
    csv_content = await financial_service.export_financial_csv(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        type=type
    )
    
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=financial_export.csv"
        }
    )
