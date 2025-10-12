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

@router.get("/ping")
async def ping() -> Dict[str, Any]:
    """Endpoint de test rapid pentru API."""
    return {"status": "alive", "timestamp": datetime.now().isoformat()}

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
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        health_status["dependencies"]["database"] = "skipped (not configured)"
    else:
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
    r2_endpoint = os.getenv("R2_ENDPOINT_URL")
    r2_access_key = os.getenv("R2_ACCESS_KEY_ID")
    r2_secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
    
    if not r2_endpoint or not r2_access_key or not r2_secret_key:
        health_status["dependencies"]["r2_storage"] = "skipped (not configured)"
    else:
        try:
            from ..services.storage_s3 import _get_client
            client = _get_client()
            # Try to list buckets (this will fail if credentials are wrong)
            client.list_buckets()
            health_status["dependencies"]["r2_storage"] = "healthy"
        except Exception as e:
            health_status["dependencies"]["r2_storage"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
    
    # Check n8n connection
    n8n_url = os.getenv("N8N_BASE_URL")
    
    if not n8n_url:
        health_status["dependencies"]["n8n"] = "skipped (not configured)"
    else:
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
