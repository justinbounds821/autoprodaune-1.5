"""
Whatsapp Service API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

import sys
sys.path.insert(0, "/workspace/microservices/autopro-common")
from autopro_common import get_db_session, get_logger, get_metrics

router = APIRouter(tags=["whatsapp-service"])
logger = get_logger(__name__)


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """Get service status"""
    return {
        "service": "whatsapp-service",
        "status": "operational",
        "features": ['webhook_handling', 'message_sending', 'group_management', 'bot_responses'],
    }


@router.get("/info")
async def get_info() -> Dict[str, Any]:
    """Get service information"""
    return {
        "service": "whatsapp-service",
        "description": "WhatsApp integration and bot",
        "version": "1.0.0",
        "features": ['webhook_handling', 'message_sending', 'group_management', 'bot_responses'],
    }
