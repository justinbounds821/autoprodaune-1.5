"""
Lead scoring API endpoints
"""
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/workspace/microservices/autopro-common")
from autopro_common import get_db_session, get_logger, get_metrics

from app.services.scoring_service import LeadScoringService

router = APIRouter(prefix="/leads/scoring", tags=["scoring"])
logger = get_logger(__name__)


@router.post("/{lead_id}/score")
async def score_lead(
    lead_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Calculate and update lead score
    
    Args:
        lead_id: Lead ID
        session: Database session
        
    Returns:
        Scoring results with priority and recommendation
    """
    try:
        scoring_service = LeadScoringService(session)
        result = await scoring_service.score_lead(lead_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        logger.info(f"Lead {lead_id} scored: {result['score']}/100 ({result['priority']})")
        
        return {
            "success": True,
            "lead_id": lead_id,
            "scoring": result,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to score lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to score lead: {str(e)}")


@router.post("/batch-score")
async def batch_score_leads(
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Batch score multiple leads
    
    Args:
        status: Optional filter by status
        limit: Max leads to score
        session: Database session
        
    Returns:
        Batch scoring results
    """
    try:
        scoring_service = LeadScoringService(session)
        results = await scoring_service.batch_score_leads(status=status, limit=limit)
        
        # Calculate distribution
        priority_distribution = {
            "urgent": len([r for r in results if r["priority"] == "urgent"]),
            "high": len([r for r in results if r["priority"] == "high"]),
            "medium": len([r for r in results if r["priority"] == "medium"]),
            "low": len([r for r in results if r["priority"] == "low"]),
        }
        
        logger.info(f"Batch scored {len(results)} leads")
        
        return {
            "success": True,
            "scored_count": len(results),
            "priority_distribution": priority_distribution,
            "leads": results[:10],  # First 10 for preview
        }
        
    except Exception as e:
        logger.error(f"Batch scoring failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch scoring failed: {str(e)}")
