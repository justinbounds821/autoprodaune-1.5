"""
Video AI Router - AI-powered video insights and search
Provides endpoints for semantic search, auto-tagging, captions, scene detection
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging

from ..services.vector_store import get_vector_store
from ..services.whisper_captions import get_whisper_service
from ..services.scene_detect import get_scene_detector
from ..services.tagging_service import get_tagging_service
from ..services.cost_tracker import get_cost_tracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/video/ai", tags=["Video AI"])


@router.get("/health")
async def ai_health_check():
    """Get health status of AI services"""
    vector_store = get_vector_store()
    whisper = get_whisper_service()
    scene_detector = get_scene_detector()
    tagging = get_tagging_service()
    
    return {
        "status": "healthy",
        "services": {
            "vector_search": vector_store.get_health(),
            "whisper_captions": whisper.get_health(),
            "scene_detection": scene_detector.get_health(),
            "tagging": tagging.get_health()
        }
    }


@router.get("/insights/{job_id}")
async def get_video_insights(job_id: str):
    """
    Get AI-generated insights for a specific video job.
    Includes tags, sentiment, scene cuts, captions, embeddings.
    """
    try:
        from ..services.supabase_client import get_supabase
        supabase = get_supabase()
        
        # Fetch insights from database
        response = supabase.table("video_insights").select("*").eq("job_id", job_id).execute()
        
        if not response.data:
            # If no insights yet, return empty structure
            return {
                "job_id": job_id,
                "tags": [],
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "entities": [],
                "scene_cuts": [],
                "captions": {
                    "available": False,
                    "formats": []
                },
                "vector_embedding": {
                    "available": False,
                    "dimension": 0
                },
                "message": "No insights processed yet. Run POST /api/video/ai/process/{job_id} to generate."
            }
        
        insight = response.data[0]
        whisper = get_whisper_service()
        vector_store = get_vector_store()
        
        return {
            "job_id": job_id,
            "tags": insight.get("tags", []),
            "sentiment": insight.get("sentiment", "neutral"),
            "sentiment_score": insight.get("sentiment_score", 0.0),
            "entities": insight.get("entities", []),
            "scene_cuts": insight.get("scene_cuts", []),
            "captions": {
                "available": bool(insight.get("captions_srt_path")),
                "formats": ["srt", "ass"] if insight.get("captions_srt_path") else [],
                "srt_path": insight.get("captions_srt_path"),
                "ass_path": insight.get("captions_ass_path")
            },
            "vector_embedding": {
                "available": bool(insight.get("vector_embedding")),
                "dimension": len(insight.get("vector_embedding", [])) if insight.get("vector_embedding") else 0
            },
            "audio_quality_score": insight.get("audio_quality_score"),
            "processed_at": insight.get("processed_at")
        }
    
    except Exception as e:
        logger.error(f"Error getting insights for {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")


@router.post("/search/similar")
async def search_similar_videos(
    query: str = Query(..., description="Search query text"),
    min_score: float = Query(0.7, description="Minimum similarity score"),
    limit: int = Query(10, description="Maximum results to return")
):
    """
    Search for videos similar to query using semantic vector search.
    Falls back to keyword search if vector search unavailable.
    """
    try:
        vector_store = get_vector_store()
        
        results = await vector_store.search_similar(
            query=query,
            min_score=min_score,
            limit=limit
        )
        
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "method": "vector" if vector_store.enabled else "keyword"
        }
    
    except Exception as e:
        logger.error(f"Search error for query '{query}': {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/process/{job_id}")
async def process_ai_features(job_id: str):
    """
    Process all AI features for a video job:
    - Generate embeddings
    - Extract tags and sentiment
    - Detect scenes
    - Generate captions
    - Calculate costs
    - Analyze audio quality
    """
    try:
        from ..services.video_ai_processor import get_video_ai_processor
        
        processor = get_video_ai_processor()
        
        if not processor.enabled:
            raise HTTPException(
                status_code=503, 
                detail="AI processing disabled. Enable with ENABLE_AI_INSIGHTS=true"
            )
        
        # Process all AI features using orchestrator
        results = await processor.process_job(job_id)
        
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI processing error for {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")


@router.get("/captions/{job_id}")
async def get_captions(job_id: str, format: str = Query("srt", regex="^(srt|ass)$")):
    """Download caption file for video"""
    try:
        from ..services.supabase_client import get_supabase
        from fastapi.responses import FileResponse
        import os
        
        whisper = get_whisper_service()
        
        if not whisper.enabled:
            raise HTTPException(status_code=503, detail="Caption service not available")
        
        supabase = get_supabase()
        
        # Get caption path from insights
        response = supabase.table("video_insights").select("*").eq("job_id", job_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="No insights found for this job")
        
        insight = response.data[0]
        caption_path = insight.get(f"captions_{format}_path")
        
        if not caption_path:
            raise HTTPException(status_code=404, detail=f"No {format.upper()} captions available for this job")
        
        if not os.path.exists(caption_path):
            raise HTTPException(status_code=404, detail="Caption file not found on disk")
        
        # Return file download
        return FileResponse(
            caption_path,
            media_type="text/plain",
            filename=f"{job_id}.{format}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting captions for {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get captions: {str(e)}")
