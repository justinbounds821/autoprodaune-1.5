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
        # Get services
        tagging = get_tagging_service()
        scene_detector = get_scene_detector()
        vector_store = get_vector_store()
        whisper = get_whisper_service()
        
        # TODO: Fetch job from database
        # For now, return mock structure showing what would be returned
        
        # Generate mock insights
        content_text = f"Sample video content for job {job_id}"
        tags_data = await tagging.analyze_content(content_text, title=f"Video {job_id}")
        
        return {
            "job_id": job_id,
            "tags": tags_data.get("tags", []),
            "sentiment": tags_data.get("sentiment", "neutral"),
            "sentiment_score": tags_data.get("sentiment_score", 0.0),
            "entities": tags_data.get("entities", []),
            "scene_cuts": [],  # Would be populated after processing
            "captions": {
                "available": whisper.enabled,
                "formats": ["srt", "ass"] if whisper.enabled else []
            },
            "vector_embedding": {
                "available": vector_store.enabled,
                "dimension": vector_store.dimension if vector_store.enabled else 0
            }
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
    """
    try:
        # Get services
        vector_store = get_vector_store()
        tagging = get_tagging_service()
        scene_detector = get_scene_detector()
        whisper = get_whisper_service()
        cost_tracker = get_cost_tracker()
        
        # TODO: Get video path from database
        video_path = f"/path/to/video/{job_id}.mp4"
        
        results = {
            "job_id": job_id,
            "processed_features": [],
            "errors": []
        }
        
        # 1. Generate tags and sentiment
        if tagging.enabled:
            try:
                tags_result = await tagging.analyze_content("Sample content", title=f"Job {job_id}")
                results["processed_features"].append("tagging")
                results["tags"] = tags_result
            except Exception as e:
                results["errors"].append(f"Tagging failed: {str(e)}")
        
        # 2. Detect scenes
        if scene_detector.enabled:
            try:
                scenes = await scene_detector.detect_scenes(video_path)
                results["processed_features"].append("scene_detection")
                results["scenes"] = len(scenes)
            except Exception as e:
                results["errors"].append(f"Scene detection failed: {str(e)}")
        
        # 3. Generate captions
        if whisper.enabled:
            try:
                captions = await whisper.generate_captions(video_path)
                if captions:
                    results["processed_features"].append("captions")
                    results["captions"] = captions
            except Exception as e:
                results["errors"].append(f"Caption generation failed: {str(e)}")
        
        # 4. Generate vector embedding
        if vector_store.enabled:
            try:
                embedding = vector_store.generate_embedding(f"Content for {job_id}")
                results["processed_features"].append("vector_embedding")
                results["embedding_dim"] = len(embedding) if embedding else 0
            except Exception as e:
                results["errors"].append(f"Embedding generation failed: {str(e)}")
        
        return results
    
    except Exception as e:
        logger.error(f"AI processing error for {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")


@router.get("/captions/{job_id}")
async def get_captions(job_id: str, format: str = Query("srt", regex="^(srt|ass)$")):
    """Download caption file for video"""
    try:
        whisper = get_whisper_service()
        
        if not whisper.enabled:
            raise HTTPException(status_code=503, detail="Caption service not available")
        
        # TODO: Retrieve caption file path from storage
        caption_path = f"/path/to/captions/{job_id}.{format}"
        
        return {
            "job_id": job_id,
            "format": format,
            "download_url": caption_path,
            "message": "Caption file ready"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting captions for {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get captions: {str(e)}")
