"""
Health check routes for AutoPro Daune API.

This module provides health check endpoints to monitor the status
of the API service and its dependencies.
"""

from fastapi import APIRouter
from typing import Dict, Any
import os
import requests
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns:
        Dictionary with health status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "AutoPro Daune API",
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with dependency status.
    
    Returns:
        Dictionary with detailed health information
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "AutoPro Daune API",
        "version": "1.0.0",
        "dependencies": {}
    }
    
    # Check database connection
    try:
        # Using Supabase service instead of database session
        from ..services.supabase_client import get_supabase_service_instance
        # Test Supabase connection
        get_supabase_service_instance().leads_list(limit=1)
        health_status["dependencies"]["database"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check R2 storage
    try:
        from services.storage_s3 import _get_client
        client = _get_client()
        # Try to list buckets (this will fail if credentials are wrong)
        client.list_buckets()
        health_status["dependencies"]["r2_storage"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["r2_storage"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check n8n connection
    n8n_url = os.getenv("N8N_BASE_URL", "http://localhost:5678")
    try:
        response = requests.get(f"{n8n_url}/healthz", timeout=5)
        if response.status_code == 200:
            health_status["dependencies"]["n8n"] = "healthy"
        else:
            health_status["dependencies"]["n8n"] = f"unhealthy: status {response.status_code}"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["dependencies"]["n8n"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status
