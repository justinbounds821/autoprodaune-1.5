"""
Financial Service API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

import sys
sys.path.insert(0, "/workspace/microservices/autopro-common")
from autopro_common import get_db_session, get_logger, get_metrics

router = APIRouter(tags=["financial-service"])
logger = get_logger(__name__)


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """Get service status"""
    return {
        "service": "financial-service",
        "status": "operational",
        "features": ['cost_calculation', 'roi_tracking', 'invoicing', 'expense_management'],
    }


@router.get("/info")
async def get_info() -> Dict[str, Any]:
    """Get service information"""
    return {
        "service": "financial-service",
        "description": "Financial tracking and invoicing",
        "version": "1.0.0",
        "features": ['cost_calculation', 'roi_tracking', 'invoicing', 'expense_management'],
    }
