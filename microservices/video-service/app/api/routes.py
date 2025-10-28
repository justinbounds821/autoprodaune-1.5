"""
Video Service API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

import sys
sys.path.insert(0, "/workspace/microservices/autopro-common")
from autopro_common import get_db_session, get_logger, get_metrics

router = APIRouter(tags=["video-service"])
logger = get_logger(__name__)


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """Get service status"""
    return {
        "service": "video-service",
        "status": "operational",
        "features": ['video_generation', 'template_management', 'heygen_integration', 'video_queue'],
    }


@router.get("/info")
async def get_info() -> Dict[str, Any]:
    """Get service information"""
    return {
        "service": "video-service",
        "description": "Video generation and processing engine",
        "version": "1.0.0",
        "features": ['video_generation', 'template_management', 'heygen_integration', 'video_queue'],
    }
