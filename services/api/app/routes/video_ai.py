# services/api/app/routes/video_ai.py
"""
Video AI routes for Phase 8/9 features.
Provides endpoints for:
- AI health checks
- Video insights (tags, scene cuts, embeddings)
- Similar video search
"""
from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/video/ai", tags=["video-ai"])


class InsightsResponse(BaseModel):
    """Video insights response model."""
    job_id: str
    tags: List[str]
    scene_cuts: List[float]
    vector_embedding: Optional[List[float]] = None
    captions: Optional[Dict[str, Any]] = None


class SimilarVideo(BaseModel):
    """Similar video result model."""
    job_id: str
    score: float
    tags: List[str]
    thumb_url: Optional[str] = None


@router.get("/health")
def ai_health() -> Dict[str, Any]:
    """
    Health check for AI services.
    
    Returns:
        Service status and configuration
    """
    try:
        from app.services.vector_store import VectorStore
        from app.services.scene_detect import SceneDetectService
        from app.services.tagging_service import TaggingService
        
        vs = VectorStore()
        
        return {
            "status": "healthy",
            "services": {
                "vector_search": {
                    "enabled": bool(vs.enabled),
                    "dimension": vs.dim
                },
                "scene_detection": {
                    "enabled": True
                },
                "tagging": {
                    "enabled": True
                }
            }
        }
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e)
        }


@router.get("/insights/{job_id}", response_model=InsightsResponse)
def get_insights(job_id: str) -> InsightsResponse:
    """
    Get AI insights for a video job.
    
    Args:
        job_id: Video job identifier
        
    Returns:
        Video insights including tags, scene cuts, embeddings
        
    Raises:
        HTTPException: If job not found or insights not available
    """
    try:
        from app.services.job_repo_supabase import get_supabase_service_instance
        from app.services.job_store import get_job
        
        # Try to get insights from database
        try:
            svc = get_supabase_service_instance()
            result = svc.sb.table("video_insights").select("*").eq("job_id", job_id).execute()
            
            if result.data and len(result.data) > 0:
                row = result.data[0]
                return InsightsResponse(
                    job_id=job_id,
                    tags=row.get("tags", []),
                    scene_cuts=row.get("scene_cuts", []),
                    vector_embedding=row.get("vector_embedding"),
                    captions=row.get("captions")
                )
        except Exception as e:
            logger.warning(f"Failed to fetch from database: {e}")
        
        # Fallback to in-memory job store
        job = get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Return minimal insights
        return InsightsResponse(
            job_id=job_id,
            tags=[],
            scene_cuts=[0.0],
            vector_embedding=None,
            captions=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get insights for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/similar")
def search_similar(
    query: str,
    min_score: float = 0.7,
    limit: int = 10
) -> List[SimilarVideo]:
    """
    Search for similar videos using semantic search.
    
    Args:
        query: Search query text
        min_score: Minimum similarity score (0.0-1.0)
        limit: Maximum number of results
        
    Returns:
        List of similar videos sorted by relevance
    """
    try:
        from app.services.vector_store import VectorStore
        from app.services.job_repo_supabase import get_supabase_service_instance
        
        vs = VectorStore()
        
        if not vs.enabled:
            return []
        
        # Generate query embedding
        query_emb = vs._embed(query)
        
        # Search in database
        svc = get_supabase_service_instance()
        
        # Use PostgreSQL pgvector similarity search
        # Note: This requires pgvector extension and proper indexing
        query_vector = "[" + ",".join(str(x) for x in query_emb) + "]"
        
        result = svc.sb.rpc(
            "search_similar_videos",
            {
                "q": query_vector,
                "min_score": min_score,
                "k": limit
            }
        ).execute()
        
        if not result.data:
            return []
        
        return [
            SimilarVideo(
                job_id=row["job_id"],
                score=row["score"],
                tags=row.get("tags", []),
                thumb_url=row.get("thumb_url")
            )
            for row in result.data
        ]
        
    except Exception as e:
        logger.error(f"Similar video search failed: {e}")
        return []
