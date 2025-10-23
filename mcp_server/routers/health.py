"""Health and Status Routes"""

from typing import Any, Dict

from fastapi import APIRouter

from config import get_settings
from clients.orchestrator_client import get_orchestrator_client

router = APIRouter(tags=["Health"])


@router.get("/health")
def health() -> Dict[str, Any]:
    """Health check endpoint"""
    settings = get_settings()
    orchestrator = get_orchestrator_client()

    return {
        "status": "ok",
        "service": "mcp_server",
        "environment": settings.environment,
        "port": settings.server_port,
        "orchestrator_connected": orchestrator.ping(),
        "version": "0.2.0",
    }
