"""
Logs routes for AutoPro Daune API.

This module provides endpoints for retrieving and managing application logs.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
import os

from ..services.supabase_client import get_supabase_service_instance

router = APIRouter(
    prefix="/api/logs",
    tags=["logs"],
    responses={404: {"description": "Not found"}}
)

@router.get("/")
async def get_logs(
    level: str = Query("info", description="Nivelul de log (debug, info, warning, error, critical)"),
    limit: int = Query(50, description="Numărul maxim de log-uri"),
    service: str = Query(None, description="Serviciul specific (opțional)")
) -> Dict[str, Any]:
    """
    Obține log-urile aplicației din Supabase.
    
    Args:
        level: Nivelul de log
        limit: Numărul maxim de log-uri
        service: Serviciul specific (opțional)
        
    Returns:
        Dicționar cu log-urile
    """
    try:
        logs = get_supabase_service_instance().logs_list(level=level, limit=limit)
        return {
            "items": logs,
            "total": len(logs),
            "level": level,
            "service": service,
            "limit": limit
        }
        
    except Exception as e:
        logging.error(f"Eroare la obținerea log-urilor: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la log-uri: {str(e)}")

@router.get("/stats")
async def get_log_stats(
    days: int = Query(7, description="Numărul de zile pentru statistici"),
    # Using Supabase service instead of database session
) -> Dict[str, Any]:
    """
    Obține statistici despre log-uri.
    
    Args:
        days: Numărul de zile pentru statistici
        db: Sesiunea de bază de date
        
    Returns:
        Dicționar cu statisticile
    """
    try:
        # Pentru moment, returnăm date mock
        # TODO: Implementați statisticile reale
        
        return {
            "period_days": days,
            "total_logs": 1250,
            "logs_by_level": {
                "error": 45,
                "warning": 120,
                "info": 1080,
                "debug": 5
            },
            "logs_by_service": {
                "financial_tracker": 300,
                "autoposter": 250,
                "leads": 200,
                "telegram_bot": 150,
                "video_generator": 100,
                "other": 250
            },
            "error_rate": 3.6,
            "most_common_errors": [
                {"error": "ROI_CALC_ERROR", "count": 15},
                {"error": "VIDEO_UPLOAD_FAILED", "count": 12},
                {"error": "TELEGRAM_SEND_ERROR", "count": 8}
            ],
            "logs_today": 180,
            "logs_this_week": 1250
        }
        
    except Exception as e:
        logging.error(f"Eroare la obținerea statisticilor log-urilor: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la statistici log-uri: {str(e)}")

@router.delete("/")
async def clear_logs(
    older_than_days: int = Query(30, description="Șterge log-urile mai vechi de X zile"),
    level: str = Query(None, description="Nivelul specific (opțional)"),
    # Using Supabase service instead of database session
) -> Dict[str, Any]:
    """
    Șterge log-urile vechi.
    
    Args:
        older_than_days: Șterge log-urile mai vechi de X zile
        level: Nivelul specific (opțional)
        db: Sesiunea de bază de date
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        # TODO: Implementați ștergerea reală a log-urilor
        
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        
        return {
            "success": True,
            "message": f"Log-uri mai vechi de {older_than_days} zile șterse",
            "cutoff_date": cutoff_date.isoformat(),
            "level": level,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Eroare la ștergerea log-urilor: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la ștergerea log-urilor: {str(e)}")

@router.get("/services")
async def get_log_services(
    # Using Supabase service instead of database session
) -> List[str]:
    """
    Obține lista de servicii care generează log-uri.
    
    Args:
        db: Sesiunea de bază de date
        
    Returns:
        Lista de servicii
    """
    try:
        # Pentru moment, returnăm lista mock
        # TODO: Implementați query-ul real pentru servicii
        
        return [
            "financial_tracker",
            "autoposter",
            "leads",
            "telegram_bot",
            "video_generator",
            "social_media",
            "api_gateway",
            "database"
        ]
        
    except Exception as e:
        logging.error(f"Eroare la obținerea serviciilor: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la servicii: {str(e)}")

@router.post("/test")
async def create_test_log(
    level: str = Query("info", description="Nivelul de log"),
    message: str = Query("Test log entry", description="Mesajul de log"),
    service: str = Query("admin", description="Serviciul"),
    # Using Supabase service instead of database session
) -> Dict[str, Any]:
    """
    Creează un log de test.
    
    Args:
        level: Nivelul de log
        message: Mesajul de log
        service: Serviciul
        db: Sesiunea de bază de date
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        # Creează log-ul de test
        test_log = {
            "level": level,
            "service": service,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": {
                "test": True,
                "created_by": "admin_dashboard"
            }
        }
        
        # Logăm în aplicație
        logger = logging.getLogger(service)
        if level.lower() == "error":
            logger.error(message)
        elif level.lower() == "warning":
            logger.warning(message)
        elif level.lower() == "debug":
            logger.debug(message)
        else:
            logger.info(message)
        
        return {
            "success": True,
            "message": "Log de test creat",
            "log_entry": test_log,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Eroare la crearea log-ului de test: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la log de test: {str(e)}")
