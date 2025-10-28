"""
Referrals routes for AutoPro Daune API.

This module provides endpoints for managing referrals.
Uses Supabase as the single source of truth.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

from ..services.supabase_client import get_supabase_service_instance

router = APIRouter(
    prefix="/api/referrals",
    tags=["referrals"],
    responses={404: {"description": "Not found"}}
)

@router.get("/")
async def get_referrals(
    limit: int = Query(50, description="Numărul maxim de referrals de returnat"),
    offset: int = Query(0, description="Offset pentru paginare"),
    status: str = Query(None, description="Status-ul referrals (pending, completed, cancelled)")
) -> Dict[str, Any]:
    """
    Obține lista de referrals din Supabase.
    
    Args:
        limit: Numărul maxim de referrals
        offset: Offset pentru paginare
        status: Status-ul referrals (opțional)
        
    Returns:
        Dicționar cu lista de referrals
    """
    try:
        referrals = get_supabase_service_instance().referrals_list(limit=limit)
        return {
            "items": referrals,
            "total": len(referrals),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logging.error(f"Eroare la obținerea referrals: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la obținerea referrals: {str(e)}")

@router.post("/")
async def create_referral(
    referral_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Creează un referral nou în Supabase.
    
    Args:
        referral_data: Datele referral-ului
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        result = get_supabase_service_instance().referral_create(referral_data)
        return {
            "success": True,
            "message": "Referral creat cu succes",
            "data": result
        }
        
    except Exception as e:
        logging.error(f"Eroare la crearea referral-ului: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la crearea referral-ului: {str(e)}")

@router.get("/stats")
async def get_referral_stats() -> Dict[str, Any]:
    """
    Obține statistici despre referrals din Supabase.
    
    Returns:
        Dicționar cu statisticile
    """
    try:
        return get_supabase_service_instance().referral_stats()
        
    except Exception as e:
        logging.error(f"Eroare la obținerea statisticilor referrals: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la statistici: {str(e)}")

@router.put("/{referral_id}/complete")
async def complete_referral(
    referral_id: int
) -> Dict[str, Any]:
    """
    Marchează un referral ca fiind completat în Supabase.
    
    Args:
        referral_id: ID-ul referral-ului
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        return get_supabase_service_instance().referral_complete(referral_id)
        
    except Exception as e:
        logging.error(f"Eroare la completarea referral-ului {referral_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la completarea referral-ului: {str(e)}")
