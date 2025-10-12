"""
Router pentru endpoint-urile financiare - AutoPro Daune.

Acest modul implementează endpoint-urile REST pentru:
- Tracking costuri și venituri
- Calcularea ROI-ului
- Analiza profitabilității
- Dashboard financiar
"""

import os
import logging
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query, Path, Body, Form

logger = logging.getLogger(__name__)

# Avoid importing SQLAlchemy-based models at import time to keep router lightweight

from ..services.financial.costs.calculator import CostCalculator
# from ..services.roi_calculator import ROICalculator  # Temporarily disabled due to SQLAlchemy/Python 3.13 compatibility

from ..services.supabase_client import get_supabase_service_instance
from ..services.financial.service import FinancialService
from ..services.financial.manager import get_financial_manager

# Inițializează serviciul financiar și calculatorii
ft = FinancialService(get_supabase_service_instance())
fm = get_financial_manager()
cost_calculator = CostCalculator()
# roi_calculator = ROICalculator()  # Temporarily disabled due to SQLAlchemy/Python 3.13 compatibility
from ..schemas.financial import (
    APICostCreate, RevenueCreate, FinancialMetricsCreate,
    ROIAnalysisResponse, ProfitLossResponse, FinancialDashboardResponse,
    CampaignMetricsCreate, CampaignMetricsResponse,
    CreditBalanceUpdate, CreditBalanceResponse,
    BudgetAlertCreate, BudgetAlertResponse
)


# Inițializează router-ul
router = APIRouter(
    prefix="/api/financial",
    tags=["financial"],
    responses={404: {"description": "Not found"}}
)

# Serviciile financiare sunt acum în Supabase


# ==================== ENDPOINT-URI PENTRU TRACKING ====================

@router.get("/revenue")
async def get_revenue_data(
    period: str = Query("7d", description="Time period (1d, 7d, 30d, 90d)")
) -> List[Dict[str, Any]]:
    """Return daily revenue series for the selected period as an array of {date, amount}."""
    try:
        supabase = get_supabase_service_instance()
        end_date = datetime.now()
        period_key = (period or "7d").lower()
        if period_key == "1d":
            start_date = end_date - timedelta(days=1)
        elif period_key == "7d":
            start_date = end_date - timedelta(days=7)
        elif period_key == "30d":
            start_date = end_date - timedelta(days=30)
        elif period_key == "90d":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=7)

        # Pull recent revenues by timestamp
        start_iso = start_date.isoformat()
        revs = supabase._table_select("revenues", "amount,timestamp", filters=[("gte", "timestamp", start_iso)]) or []

        # Group by day
        by_day: Dict[str, float] = {}
        for r in revs:
            ts = (r.get("timestamp") or "")[:10]
            by_day[ts] = by_day.get(ts, 0.0) + float(r.get("amount") or 0)

        # Build continuous daily series
        out: List[Dict[str, Any]] = []
        cur = datetime(start_date.year, start_date.month, start_date.day)
        end = datetime(end_date.year, end_date.month, end_date.day)
        while cur <= end:
            d = cur.strftime("%Y-%m-%d")
            out.append({"date": d, "amount": round(by_day.get(d, 0.0), 2)})
            cur += timedelta(days=1)
        return out
    except Exception as e:
        logging.error(f"Error getting revenue data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get revenue data: {str(e)}")


@router.get("/costs")
async def get_costs_data(
    period: str = Query("7d", description="Time period (1d, 7d, 30d, 90d)")
) -> List[Dict[str, Any]]:
    """Return daily costs series for the selected period as an array of {date, amount}."""
    try:
        supabase = get_supabase_service_instance()
        end_date = datetime.now()
        period_key = (period or "7d").lower()
        if period_key == "1d":
            start_date = end_date - timedelta(days=1)
        elif period_key == "7d":
            start_date = end_date - timedelta(days=7)
        elif period_key == "30d":
            start_date = end_date - timedelta(days=30)
        elif period_key == "90d":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=7)

        start_iso = start_date.isoformat()
        costs = supabase._table_select("api_costs", "cost,timestamp", filters=[("gte", "timestamp", start_iso)]) or []

        by_day: Dict[str, float] = {}
        for c in costs:
            ts = (c.get("timestamp") or "")[:10]
            by_day[ts] = by_day.get(ts, 0.0) + float(c.get("cost") or 0)

        out: List[Dict[str, Any]] = []
        cur = datetime(start_date.year, start_date.month, start_date.day)
        end = datetime(end_date.year, end_date.month, end_date.day)
        while cur <= end:
            d = cur.strftime("%Y-%m-%d")
            out.append({"date": d, "amount": round(by_day.get(d, 0.0), 2)})
            cur += timedelta(days=1)
        return out
    except Exception as e:
        logging.error(f"Error getting costs data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get costs data: {str(e)}")


@router.post("/track-cost", response_model=Dict[str, Any])
async def track_api_cost(
    cost_data: Dict[str, Any]
):
    """
    Înregistrează un cost API nou în Supabase.
    
    Args:
        cost_data: Datele costului de înregistrat
        
    Returns:
        Dicționar cu rezultatul operației
    """
    # Not implemented without ROI calculator (SQLAlchemy dependency removed)
    raise HTTPException(status_code=501, detail="Budget allocation optimization not implemented")
    try:
        result = fm.add_cost(
            provider=cost_data.get("provider"),
            amount=cost_data.get("cost", 0),
            currency=cost_data.get("currency", "EUR"),
            operation=cost_data.get("operation", "unknown"),
            meta=cost_data.get("metadata", {})
        )
        return {
            "success": True,
            "message": "Cost API înregistrat cu succes",
            "data": result
        }
        
    except Exception as e:
        logging.error(f"Eroare la înregistrarea costului API: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la înregistrarea costului: {str(e)}")


@router.put("/track-cost/{cost_id}", response_model=Dict[str, Any])
async def update_api_cost(
    cost_id: int = Path(..., description="ID-ul costului"),
    cost_data: Dict[str, Any] = Body(...)
):
    """
    Actualizează un cost API existent în Supabase.
    
    Args:
        cost_id: ID-ul costului de actualizat
        cost_data: Datele noi pentru cost
        
    Returns:
        Dicționar cu rezultatul operației
    """
    # Moved to Supabase service; disable SQLAlchemy implementation
    raise HTTPException(status_code=501, detail="Campaigns moved to Supabase service")
    try:
        result = ft.update_api_cost(cost_id, **cost_data)
        
        if not result:
            raise HTTPException(status_code=404, detail="Costul nu a fost găsit")
        
        return {
            "success": True,
            "message": "Cost API actualizat cu succes",
            "data": result[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Eroare la actualizarea costului API: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la actualizarea costului: {str(e)}")


@router.delete("/track-cost/{cost_id}", response_model=Dict[str, Any])
async def delete_api_cost(
    cost_id: int = Path(..., description="ID-ul costului")
):
    """
    Șterge un cost API din Supabase.
    
    Args:
        cost_id: ID-ul costului de șters
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        result = ft.delete_api_cost(cost_id)
        
        return {
            "success": True,
            "message": "Cost API șters cu succes",
            "data": result
        }
        
    except Exception as e:
        logging.error(f"Eroare la ștergerea costului API: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la ștergerea costului: {str(e)}")


@router.post("/track-revenue", response_model=Dict[str, Any])
async def track_revenue(
    revenue_data: Dict[str, Any]
):
    """
    Înregistrează un venit nou în Supabase.
    
    Args:
        revenue_data: Datele venitului de înregistrat
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        result = fm.add_revenue(
            source=revenue_data.get("source"),
            amount=revenue_data.get("amount", 0),
            currency=revenue_data.get("currency", "EUR"),
            provider=revenue_data.get("provider"),
            meta=revenue_data.get("metadata", {})
        )
        return {
            "success": True,
            "message": "Venit înregistrat cu succes",
            "data": result
        }
        
    except Exception as e:
        logging.error(f"Eroare la înregistrarea venitului: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la înregistrarea venitului: {str(e)}")


@router.put("/track-revenue/{revenue_id}", response_model=Dict[str, Any])
async def update_revenue(
    revenue_id: int = Path(..., description="ID-ul venitului"),
    revenue_data: Dict[str, Any] = Body(...)
):
    """
    Actualizează un venit existent în Supabase.
    
    Args:
        revenue_id: ID-ul venitului de actualizat
        revenue_data: Datele noi pentru venit
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        result = ft.update_revenue(revenue_id, **revenue_data)
        
        if not result:
            raise HTTPException(status_code=404, detail="Venitul nu a fost găsit")
        
        return {
            "success": True,
            "message": "Venit actualizat cu succes",
            "data": result[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Eroare la actualizarea venitului: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la actualizarea venitului: {str(e)}")


@router.delete("/track-revenue/{revenue_id}", response_model=Dict[str, Any])
async def delete_revenue(
    revenue_id: int = Path(..., description="ID-ul venitului")
):
    """
    Șterge un venit din Supabase.
    
    Args:
        revenue_id: ID-ul venitului de șters
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        result = ft.delete_revenue(revenue_id)
        
        return {
            "success": True,
            "message": "Venit șters cu succes",
            "data": result
        }
        
    except Exception as e:
        logging.error(f"Eroare la ștergerea venitului: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la ștergerea venitului: {str(e)}")


@router.post("/calculate-daily-metrics/{target_date}")
async def calculate_daily_metrics(
    target_date: date = Path(..., description="Data pentru care se calculează metricile"),
    # Using Supabase service instead of database session
):
    """
    Calculează metricile financiare pentru o dată specificată.
    
    Args:
        target_date: Data pentru care se calculează metricile
        db: Sesiunea de bază de date
        
    Returns:
        Dicționar cu metricile calculate
    """
    try:
        # Daily metrics moved to Supabase aggregations
        raise HTTPException(status_code=501, detail="Daily metrics moved to Supabase aggregations")
        
        return {
            "success": True,
            "message": f"Metrici calculate pentru {target_date}",
            "data": {
                "date": result.date.isoformat(),
                "total_costs": float(result.total_costs),
                "total_revenue": float(result.total_revenue),
                "net_profit": float(result.net_profit),
                "roi_percentage": float(result.roi_percentage),
                "created_at": result.created_at.isoformat(),
                "updated_at": result.updated_at.isoformat()
            }
        }
        
    except Exception as e:
        logging.error(f"Eroare la calcularea metricilor zilnice: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la calcularea metricilor: {str(e)}")


# ==================== ENDPOINT-URI PENTRU ROI ====================

@router.get("/roi/{period}", response_model=ROIAnalysisResponse)
async def get_roi_analysis(
    period: str = Path(description="Perioada pentru analiza ROI (today, 7d, 30d, mtd, ytd)"),
    date_from: Optional[str] = Query(None, description="Data start custom (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Data end custom (YYYY-MM-DD)")
):
    """
    Obține analiza ROI pentru o perioadă specificată sau interval custom.
    
    Args:
        period: Perioada preset pentru analiză
        date_from: Data start custom (opțional, override period)
        date_to: Data end custom (opțional, override period)
        
    Returns:
        Obiect ROIData cu rezultatul
    """
    try:
        result = fm.roi(period=period, date_from=date_from, date_to=date_to)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Eroare la obținerea analizei ROI: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la analiza ROI: {str(e)}")


# ==================== PAYMENT TRACKING ENDPOINTS ====================

@router.get("/payments")
async def get_payments(
    status: Optional[str] = Query(None, description="Payment status filter"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    client_id: Optional[str] = Query(None, description="Client ID filter"),
    limit: int = Query(50, description="Number of payments to return")
) -> Dict[str, Any]:
    """Get payment tracking data."""
    try:
        supabase = get_supabase_service_instance()
        
        # Build filters
        filters = []
        if status:
            filters.append(("eq", "status", status))
        if date_from:
            filters.append(("gte", "payment_date", date_from))
        if date_to:
            filters.append(("lte", "payment_date", date_to))
        if client_id:
            filters.append(("eq", "client_id", client_id))
        
        # Get payments from database
        payments = supabase._table_select(
            "payments",
            "*",
            filters,
            limit=limit,
            order_by=[("payment_date", "desc")]
        )
        
        return {
            "success": True,
            "data": {"payments": payments},
            "total": len(payments)
        }
        
    except Exception as e:
        logger.error(f"[PaymentTracking] Get payments error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get payments: {str(e)}")


@router.post("/payments")
async def create_payment(
    invoice_id: str = Form(...),
    amount: float = Form(...),
    payment_method: str = Form(...),
    payment_date: Optional[str] = Form(None),
    reference: Optional[str] = Form(None),
    notes: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """Create a new payment record."""
    try:
        supabase = get_supabase_service_instance()
        
        # Validate invoice exists
        invoice = supabase._table_select("invoices", "*", [("eq", "id", invoice_id)])
        if not invoice or len(invoice) == 0:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice_data = invoice[0]
        
        # Calculate payment date
        if not payment_date:
            payment_date = datetime.now().isoformat().split('T')[0]
        
        # Create payment record
        payment_data = {
            "id": str(uuid.uuid4()),
            "invoice_id": invoice_id,
            "client_id": invoice_data.get("client_id"),
            "amount": amount,
            "payment_method": payment_method,
            "payment_date": payment_date,
            "reference": reference,
            "notes": notes,
            "status": "completed",
            "created_at": datetime.now().isoformat()
        }
        
        result = supabase._table_insert("payments", payment_data)
        
        return {
            "success": True,
            "message": "Payment created successfully",
            "data": payment_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[PaymentTracking] Create payment error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create payment: {str(e)}")


@router.get("/payments/overview")
async def get_payment_overview(
    period: str = Query("30d", description="Time period (7d, 30d, 90d, 1y)")
) -> Dict[str, Any]:
    """Get payment overview statistics."""
    try:
        supabase = get_supabase_service_instance()
        
        # Calculate date range
        end_date = datetime.now()
        if period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
        elif period == "1y":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        start_date_str = start_date.isoformat().split('T')[0]
        end_date_str = end_date.isoformat().split('T')[0]
        
        # Get payments in period
        payments = supabase._table_select(
            "payments",
            "*",
            [
                ("gte", "payment_date", start_date_str),
                ("lte", "payment_date", end_date_str)
            ]
        )
        
        # Calculate statistics
        total_payments = len(payments)
        total_amount = sum(p.get("amount", 0) for p in payments)
        completed_payments = [p for p in payments if p.get("status") == "completed"]
        pending_payments = [p for p in payments if p.get("status") == "pending"]
        failed_payments = [p for p in payments if p.get("status") == "failed"]
        
        # Payment methods breakdown
        payment_methods = {}
        for payment in payments:
            method = payment.get("payment_method", "unknown")
            payment_methods[method] = payment_methods.get(method, 0) + 1
        
        return {
            "success": True,
            "data": {
                "overview": {
                    "period": period,
                    "total_payments": total_payments,
                    "total_amount": total_amount,
                    "completed_count": len(completed_payments),
                    "completed_amount": sum(p.get("amount", 0) for p in completed_payments),
                    "pending_count": len(pending_payments),
                    "pending_amount": sum(p.get("amount", 0) for p in pending_payments),
                    "failed_count": len(failed_payments),
                    "failed_amount": sum(p.get("amount", 0) for p in failed_payments),
                    "payment_methods": payment_methods
                }
            }
        }
        
    except Exception as e:
        logger.error(f"[PaymentTracking] Get overview error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get payment overview: {str(e)}")


# ==================== INVOICE GENERATION ENDPOINTS ====================

@router.get("/invoices")
async def get_invoices(
    status: Optional[str] = Query(None, description="Invoice status filter"),
    client_id: Optional[str] = Query(None, description="Client ID filter"),
    limit: int = Query(50, description="Number of invoices to return")
) -> Dict[str, Any]:
    """Get invoice data."""
    try:
        supabase = get_supabase_service_instance()
        
        # Build filters
        filters = []
        if status:
            filters.append(("eq", "status", status))
        if client_id:
            filters.append(("eq", "client_id", client_id))
        
        # Get invoices from database
        invoices = supabase._table_select(
            "invoices",
            "*",
            filters,
            limit=limit,
            order_by=[("created_at", "desc")]
        )
        
        return {
            "success": True,
            "data": {"invoices": invoices},
            "total": len(invoices)
        }
        
    except Exception as e:
        logger.error(f"[InvoiceGeneration] Get invoices error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get invoices: {str(e)}")


@router.post("/invoices")
async def create_invoice(
    client_name: str = Form(...),
    client_email: str = Form(...),
    client_address: str = Form(...),
    due_date: str = Form(...),
    tax_rate: float = Form(0.19),
    items: str = Form(...),  # JSON string
    notes: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """Create a new invoice."""
    try:
        import json
        
        # Parse items
        try:
            invoice_items = json.loads(items)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid items JSON")
        
        # Calculate totals
        subtotal = sum(item.get("total", 0) for item in invoice_items)
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        
        # Generate invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y-%m')}-{len(invoice_items)}"
        
        # Create invoice
        invoice_data = {
            "id": str(uuid.uuid4()),
            "number": invoice_number,
            "client_name": client_name,
            "client_email": client_email,
            "client_address": client_address,
            "due_date": due_date,
            "tax_rate": tax_rate,
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "total": total,
            "items": invoice_items,
            "notes": notes,
            "status": "draft",
            "created_at": datetime.now().isoformat()
        }
        
        supabase = get_supabase_service_instance()
        result = supabase._table_insert("invoices", invoice_data)
        
        return {
            "success": True,
            "message": "Invoice created successfully",
            "data": invoice_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[InvoiceGeneration] Create invoice error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create invoice: {str(e)}")


# ==================== BUDGET PLANNING ENDPOINTS ====================

@router.get("/budget-plans")
async def get_budget_plans() -> Dict[str, Any]:
    """Get budget plans."""
    try:
        supabase = get_supabase_service_instance()
        
        budget_plans = supabase._table_select(
            "budget_plans",
            "*",
            [],
            order_by=[("created_at", "desc")]
        )
        
        return {
            "success": True,
            "data": {"budget_plans": budget_plans},
            "total": len(budget_plans)
        }
        
    except Exception as e:
        logger.error(f"[BudgetPlanning] Get budget plans error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get budget plans: {str(e)}")


@router.post("/budget-plans")
async def create_budget_plan(
    name: str = Form(...),
    description: str = Form(...),
    period: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    categories: str = Form(...)  # JSON string
) -> Dict[str, Any]:
    """Create a new budget plan."""
    try:
        import json
        
        # Parse categories
        try:
            budget_categories = json.loads(categories)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid categories JSON")
        
        # Calculate total budget
        total_budget = sum(cat.get("budget_amount", 0) for cat in budget_categories)
        
        # Create budget plan
        budget_plan_data = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "total_budget": total_budget,
            "categories": budget_categories,
            "status": "draft",
            "created_at": datetime.now().isoformat()
        }
        
        supabase = get_supabase_service_instance()
        result = supabase._table_insert("budget_plans", budget_plan_data)
        
        return {
            "success": True,
            "message": "Budget plan created successfully",
            "data": budget_plan_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[BudgetPlanning] Create budget plan error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create budget plan: {str(e)}")


@router.get("/profit-loss")
async def get_profit_loss(
    start_date: date = Query(..., description="Data de început"),
    end_date: date = Query(..., description="Data de sfârșit")
):
    """
    Obține analiza profit/pierdere pentru o perioadă specificată din Supabase.
    
    Args:
        start_date: Data de început
        end_date: Data de sfârșit
        
    Returns:
        Dicționar cu datele profit/pierdere
    """
    try:
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Data de început nu poate fi mai mare decât data de sfârșit")
        
        days = (end_date - start_date).days
        period = f"{days}d"
        return ft.profit_loss_between(period)
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Eroare la obținerea analizei profit/pierdere: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la analiza profit/pierdere: {str(e)}")


# ==================== ENDPOINT-URI PENTRU DASHBOARD ====================

@router.get("/dashboard")
async def get_financial_dashboard(
    date_from: Optional[str] = Query(None, description="Data start (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Data end (YYYY-MM-DD)"),
    period: str = Query("7d", description="Perioada (today, 7d, 30d, mtd, ytd)")
):
    """
    Obține datele pentru dashboard-ul financiar din Supabase.

    Args:
        date_from: Data start pentru filtrare (opțional)
        date_to: Data end pentru filtrare (opțional)
        period: Perioada preset (default: 7d)

    Returns:
        Dicționar cu datele dashboard-ului
    """
    # FAKE_MODE support for testing without Supabase
    if os.getenv("FAKE_MODE") == "true":
        return {
            "success": True,
            "data": {
                "total_costs": 1250.50,
                "total_revenue": 8500.00,
                "roi_percentage": 580.0,
                "videos_generated": 142,
                "period": period,
                "date_from": date_from or "2025-10-02",
                "date_to": date_to or "2025-10-09"
            }
        }

    try:
        return fm.dashboard(date_from=date_from, date_to=date_to, period=period)

    except Exception as e:
        logging.error(f"Eroare la obținerea datelor dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la dashboard: {str(e)}")


# ==================== ENDPOINT-URI PENTRU CAMPANII ====================

@router.post("/campaigns", response_model=Dict[str, Any])
async def create_campaign(
    campaign_data: CampaignMetricsCreate,
):
    """
    Creează o campanie nouă.
    
    Args:
        campaign_data: Datele campaniei
        db: Sesiunea de bază de date
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        # Moved to FinancialService
        
        # Creează campania în baza de date
        db_campaign = CampaignMetrics(**campaign_data.dict())
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)
        
        return {
            "success": True,
            "message": "Campanie creată cu succes",
            "data": {
                "id": db_campaign.id,
                "campaign_name": db_campaign.campaign_name,
                "campaign_type": db_campaign.campaign_type.value,
                "start_date": db_campaign.start_date.isoformat(),
                "created_at": db_campaign.created_at.isoformat()
            }
        }
        
    except Exception as e:
        logging.error(f"Eroare la crearea campaniei: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la crearea campaniei: {str(e)}")


@router.get("/campaigns", response_model=List[CampaignMetricsResponse])
async def get_campaigns(
    limit: int = Query(10, description="Numărul maxim de campanii de returnat"),
    # Using Supabase service instead of database session
):
    """
    Obține lista de campanii.
    
    Args:
        limit: Numărul maxim de campanii
        db: Sesiunea de bază de date
        
    Returns:
        Lista de campanii
    """
    try:
        # Moved to FinancialService
        campaigns = []  # Campaign metrics moved to Supabase
        
        return campaigns
        
    except Exception as e:
        logging.error(f"Eroare la obținerea campaniilor: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la obținerea campaniilor: {str(e)}")


@router.put("/campaigns/{campaign_id}", response_model=Dict[str, Any])
async def update_campaign(
    campaign_id: int = Path(..., description="ID-ul campaniei"),
    update_data: Dict[str, Any] = None,
    # Using Supabase service instead of database session
):
    """
    Actualizează o campanie existentă.
    
    Args:
        campaign_id: ID-ul campaniei
        update_data: Datele de actualizat
        db: Sesiunea de bază de date
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        # Moved to FinancialService
        result = {}  # Campaign metrics moved to Supabase
        
        if not result:
            raise HTTPException(status_code=404, detail="Campania nu a fost găsită")
        
        return {
            "success": True,
            "message": "Campanie actualizată cu succes",
            "data": {
                "id": result.id,
                "campaign_name": result.campaign_name,
                "updated_at": result.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Eroare la actualizarea campaniei: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la actualizarea campaniei: {str(e)}")


# ==================== ENDPOINT-URI PENTRU CREDIT BALANCE ====================

@router.get("/credit-balance/{provider}", response_model=CreditBalanceResponse)
async def get_credit_balance(
    provider: str = Path(..., description="Providerul pentru care se obține balanța"),
    # Using Supabase service instead of database session
):
    """
    Obține balanța de credite pentru un provider.
    
    Args:
        provider: Numele providerului
        db: Sesiunea de bază de date
        
    Returns:
        Obiect CreditBalance cu balanța
    """
    try:
        result = fm.get_credit_balance(provider)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Nu există balanță pentru providerul {provider}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Eroare la obținerea balanței de credite: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la balanța de credite: {str(e)}")


@router.put("/credit-balance/{provider}", response_model=Dict[str, Any])
async def update_credit_balance(
    provider: str = Path(..., description="Providerul pentru care se actualizează balanța"),
    amount: Decimal = Query(..., description="Suma de actualizat"),
    # Using Supabase service instead of database session
):
    """
    Actualizează balanța de credite pentru un provider.
    
    Args:
        provider: Numele providerului
        amount: Suma de actualizat
        db: Sesiunea de bază de date
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        result = fm.update_credit_balance(provider, float(amount))
        
        return {
            "success": True,
            "message": f"Balanța de credite actualizată pentru {provider}",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Eroare la actualizarea balanței de credite: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la actualizarea balanței: {str(e)}")


# ==================== ENDPOINT-URI PENTRU BUDGET ALERTS ====================

@router.post("/budget-alerts", response_model=Dict[str, Any])
async def create_budget_alert(
    alert_data: BudgetAlertCreate,
    # Using Supabase service instead of database session
):
    """
    Creează o alertă de buget nouă.
    
    Args:
        alert_data: Datele alertei
        db: Sesiunea de bază de date
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        result = fm.create_budget_alert(
            alert_name=alert_data.alert_name,
            threshold=alert_data.threshold_value,
            alert_type=alert_data.alert_type,
            message=alert_data.message,
            meta={}
        )
        
        return {
            "success": True,
            "message": "Alertă de buget creată cu succes",
            "data": result
        }
        
    except Exception as e:
        logging.error(f"Eroare la crearea alertei de buget: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la crearea alertei: {str(e)}")


@router.get("/budget-alerts", response_model=List[BudgetAlertResponse])
async def get_budget_alerts(
    limit: int = Query(10, description="Numărul maxim de alerte de returnat"),
    # Using Supabase service instead of database session
):
    """
    Obține lista de alerte de buget.
    
    Args:
        limit: Numărul maxim de alerte
        db: Sesiunea de bază de date
        
    Returns:
        Lista de alerte de buget
    """
    try:
        alerts = fm.get_budget_alerts()
        
        return alerts[:limit]
        
    except Exception as e:
        logging.error(f"Eroare la obținerea alertelor de buget: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la obținerea alertelor: {str(e)}")


# ==================== ENDPOINT-URI PENTRU CALCULARE COSTURI ====================

@router.post("/calculate-cost/pika", response_model=Dict[str, Any])
async def calculate_pika_cost(
    duration_seconds: int = Query(..., description="Durata video-ului în secunde"),
    resolution: str = Query("720p", description="Rezoluția video-ului"),
    quality: str = Query("high", description="Calitatea video-ului")
):
    """
    Calculează costul pentru generarea video cu Pika.
    
    Args:
        duration_seconds: Durata în secunde
        resolution: Rezoluția (720p, 1080p, 4K)
        quality: Calitatea (low, medium, high)
        
    Returns:
        Dicționar cu costul calculat
    """
    try:
        result = cost_calculator.calculate_pika_cost(duration_seconds, resolution, quality)
        
        return {
            "success": True,
            "message": "Cost calculat cu succes",
            "data": result
        }
        
    except Exception as e:
        logging.error(f"Eroare la calcularea costului Pika: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la calcularea costului: {str(e)}")


@router.post("/calculate-cost/heygen", response_model=Dict[str, Any])
async def calculate_heygen_cost(
    duration_seconds: int = Query(..., description="Durata video-ului în secunde"),
    avatar_type: str = Query("default", description="Tipul avatarului"),
    voice_type: str = Query("standard", description="Tipul vocii")
):
    """
    Calculează costul pentru generarea video cu HeyGen.
    
    Args:
        duration_seconds: Durata în secunde
        avatar_type: Tipul avatarului
        voice_type: Tipul vocii
        
    Returns:
        Dicționar cu costul calculat
    """
    try:
        result = cost_calculator.calculate_heygen_cost(duration_seconds, avatar_type, voice_type)
        
        return {
            "success": True,
            "message": "Cost calculat cu succes",
            "data": result
        }
        
    except Exception as e:
        logging.error(f"Eroare la calcularea costului HeyGen: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la calcularea costului: {str(e)}")


@router.post("/calculate-cost/social-media", response_model=Dict[str, Any])
async def calculate_social_media_cost(
    platform: str = Query(..., description="Platforma (TikTok, Instagram, YouTube)"),
    content_type: str = Query("video", description="Tipul conținutului"),
    file_size_mb: Optional[float] = Query(None, description="Mărimea fișierului în MB")
):
    """
    Calculează costul pentru postarea pe social media.
    
    Args:
        platform: Platforma de postare
        content_type: Tipul conținutului
        file_size_mb: Mărimea fișierului
        
    Returns:
        Dicționar cu costul calculat
    """
    try:
        result = cost_calculator.calculate_social_media_posting_cost(platform, content_type, file_size_mb)
        
        return {
            "success": True,
            "message": "Cost calculat cu succes",
            "data": result
        }
        
    except Exception as e:
        logging.error(f"Eroare la calcularea costului social media: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la calcularea costului: {str(e)}")


# ==================== ENDPOINT-URI PENTRU ESTIMARE COSTURI ====================

@router.post("/estimate-monthly-costs", response_model=Dict[str, Any])
async def estimate_monthly_costs(
    usage_plan: Dict[str, Any]
):
    """
    Estimează costurile lunare bazate pe un plan de utilizare.
    
    Args:
        usage_plan: Planul de utilizare
        
    Returns:
        Dicționar cu estimarea costurilor
    """
    try:
        result = cost_calculator.estimate_monthly_costs(usage_plan)
        
        return {
            "success": True,
            "message": "Costuri estimate cu succes",
            "data": result
        }
        
    except Exception as e:
        logging.error(f"Eroare la estimarea costurilor lunare: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la estimarea costurilor: {str(e)}")


@router.post("/estimate-budget-requirements", response_model=Dict[str, Any])
async def estimate_budget_requirements(
    target_roi: Decimal = Query(..., description="ROI-ul țintă în procente"),
    expected_revenue: Decimal = Query(..., description="Veniturile așteptate"),
    time_period_days: int = Query(30, description="Perioada în zile")
):
    """
    Estimează cerințele de buget bazate pe ROI țintă.
    
    Args:
        target_roi: ROI-ul țintă
        expected_revenue: Veniturile așteptate
        time_period_days: Perioada în zile
        
    Returns:
        Dicționar cu estimarea cerințelor
    """
    try:
        result = cost_calculator.estimate_budget_requirements(target_roi, expected_revenue, time_period_days)
        
        return {
            "success": True,
            "message": "Cerințe de buget estimate cu succes",
            "data": result
        }
        
    except Exception as e:
        logging.error(f"Eroare la estimarea cerințelor de buget: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la estimarea cerințelor: {str(e)}")


# ==================== ENDPOINT-URI PENTRU OPTIMIZARE ====================

@router.post("/optimize-costs", response_model=Dict[str, Any])
async def optimize_costs(
    current_usage: Dict[str, Any],
    budget_limit: Decimal = Query(..., description="Limita de buget")
):
    """
    Sugerează optimizări pentru reducerea costurilor.
    
    Args:
        current_usage: Utilizarea curentă
        budget_limit: Limita de buget
        
    Returns:
        Dicționar cu sugestiile de optimizare
    """
    try:
        result = cost_calculator.optimize_costs(current_usage, budget_limit)
        
        return {
            "success": True,
            "message": "Optimizări calculate cu succes",
            "data": result
        }
        
    except Exception as e:
        logging.error(f"Eroare la optimizarea costurilor: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la optimizare: {str(e)}")


@router.post("/optimize-budget-allocation", response_model=Dict[str, Any])
async def optimize_budget_allocation(
    total_budget: Decimal = Query(..., description="Bugetul total"),
    campaign_performance: List[Dict[str, Any]] = Body(default=[], description="Performanța campaniilor")
):
    """
    Optimizează alocarea bugetului bazată pe performanța campaniilor.
    
    Args:
        total_budget: Bugetul total
        campaign_performance: Performanța campaniilor
        
    Returns:
        Dicționar cu alocarea optimizată
    """
    try:
        result = roi_calculator.optimize_budget_allocation(total_budget, campaign_performance)
        
        return {
            "success": True,
            "message": "Alocarea bugetului optimizată cu succes",
            "data": result
        }
        
    except Exception as e:
        logging.error(f"Eroare la optimizarea alocării bugetului: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la optimizarea alocării: {str(e)}")
