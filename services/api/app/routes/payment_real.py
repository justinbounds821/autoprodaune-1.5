"""
REAL Payment Routes - AutoPro Daune
Stripe integration for payments, invoices, subscriptions
"""

from fastapi import APIRouter, Depends
from typing import List, Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel
from ..middleware.jwt_auth import get_current_user, CurrentUser
from ..services.payment_service_real import get_payment_service, PaymentService

router = APIRouter(prefix="/api/payments", tags=["payments-real"])

class PaymentIntentRequest(BaseModel):
    amount: float
    currency: str = "RON"
    description: Optional[str] = None

class SubscriptionRequest(BaseModel):
    plan_id: str
    payment_method_id: str

class InvoiceItem(BaseModel):
    description: str
    amount: float

class InvoiceRequest(BaseModel):
    items: List[InvoiceItem]
    customer_info: Dict[str, str]

@router.post("/create-intent")
async def create_payment_intent(
    request: PaymentIntentRequest,
    current_user: CurrentUser = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Create Stripe payment intent - REAL"""
    return await payment_service.create_payment_intent(
        amount=request.amount,
        currency=request.currency,
        description=request.description,
        user_id=current_user.id
    )

@router.post("/subscribe")
async def create_subscription(
    request: SubscriptionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Create subscription - REAL Stripe"""
    return await payment_service.create_subscription(
        user_id=current_user.id,
        plan_id=request.plan_id,
        payment_method_id=request.payment_method_id
    )

@router.post("/generate-invoice")
async def generate_invoice(
    request: InvoiceRequest,
    current_user: CurrentUser = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Generate invoice PDF - REAL"""
    return await payment_service.generate_invoice(
        user_id=current_user.id,
        items=[item.dict() for item in request.items],
        customer_info=request.customer_info
    )
