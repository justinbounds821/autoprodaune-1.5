"""
Automation Service API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

import sys
sys.path.insert(0, "/workspace/microservices/autopro-common")
from autopro_common import get_db_session, get_logger, get_metrics

router = APIRouter(tags=["automation-service"])
logger = get_logger(__name__)


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """Get service status"""
    return {
        "service": "automation-service",
        "status": "operational",
        "features": ['workflow_execution', 'scheduling', 'trigger_management', 'action_execution'],
    }


@router.get("/info")
async def get_info() -> Dict[str, Any]:
    """Get service information"""
    return {
        "service": "automation-service",
        "description": "Workflow automation and scheduling",
        "version": "1.0.0",
        "features": ['workflow_execution', 'scheduling', 'trigger_management', 'action_execution'],
    }
