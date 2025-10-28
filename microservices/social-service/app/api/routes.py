"""
Social Service API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

import sys
sys.path.insert(0, "/workspace/microservices/autopro-common")
from autopro_common import get_db_session, get_logger, get_metrics

router = APIRouter(tags=["social-service"])
logger = get_logger(__name__)


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """Get service status"""
    return {
        "service": "social-service",
        "status": "operational",
        "features": ['tiktok_posting', 'instagram_posting', 'facebook_posting', 'youtube_posting', 'scheduler'],
    }


@router.get("/info")
async def get_info() -> Dict[str, Any]:
    """Get service information"""
    return {
        "service": "social-service",
        "description": "Social media integrations and posting",
        "version": "1.0.0",
        "features": ['tiktok_posting', 'instagram_posting', 'facebook_posting', 'youtube_posting', 'scheduler'],
    }
