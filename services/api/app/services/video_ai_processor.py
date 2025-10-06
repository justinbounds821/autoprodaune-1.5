"""
Video AI Processor - Orchestrate all AI processing for videos
Single Responsibility: Coordinate AI features for video jobs
Integrates: tagging, scene detection, captions, embeddings, cost tracking
"""
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class VideoAIProcessor:
    """
    Orchestrate all AI processing for video jobs.
    Coordinates multiple AI services and stores results.
    """
    
    def __init__(self):
        self.enabled = os.getenv("ENABLE_AI_INSIGHTS", "false").lower() == "true"
        
        if not self.enabled:
            logger.info("⚠️ Video AI processor disabled (ENABLE_AI_INSIGHTS=false)")
    
    async def process_job(self, job_id: str) -> Dict[str, Any]:
        """
        Process all AI features for a video job.
        Returns comprehensive results with all AI insights.
        """
        if not self.enabled:
            return {
                "job_id": job_id,
                "processed": False,
                "reason": "AI processing disabled",
                "enable_with": "ENABLE_AI_INSIGHTS=true"
            }
        
        try:
            from .supabase_client import get_supabase
            from .vector_store import get_vector_store
            from .whisper_captions import get_whisper_service
            from .scene_detect import get_scene_detector
            from .tagging_service import get_tagging_service
            from .audio_enhance import get_audio_enhancer
            from .cost_tracker import get_cost_tracker
            
            supabase = get_supabase()
            
            # Get job details
            job_response = supabase.table("video_jobs").select("*").eq("id", job_id).execute()
            
            if not job_response.data:
                raise ValueError(f"Job {job_id} not found")
            
            job = job_response.data[0]
            video_path = job.get("output_url") or job.get("video_url")
            
            results = {
                "job_id": job_id,
                "started_at": datetime.utcnow().isoformat(),
                "processed_features": [],
                "errors": [],
                "insights": {}
            }
            
            # 1. Tagging & Sentiment Analysis
            tagging_service = get_tagging_service()
            if tagging_service.enabled:
                try:
                    content = job.get("input_text", "") or job.get("script", "")
                    tags_result = await tagging_service.analyze_content(
                        content, 
                        title=job.get("title")
                    )
                    results["processed_features"].append("tagging")
                    results["insights"]["tags"] = tags_result.get("tags", [])
                    results["insights"]["sentiment"] = tags_result.get("sentiment")
                    results["insights"]["sentiment_score"] = tags_result.get("sentiment_score", 0.0)
                    results["insights"]["entities"] = tags_result.get("entities", [])
                except Exception as e:
                    logger.error(f"Tagging failed for {job_id}: {e}")
                    results["errors"].append(f"Tagging: {str(e)}")
            
            # 2. Scene Detection (only for local files)
            scene_detector = get_scene_detector()
            if scene_detector.enabled and video_path and (video_path.startswith("/") or video_path.startswith("./")):
                try:
                    scenes = await scene_detector.detect_scenes(video_path)
                    results["processed_features"].append("scene_detection")
                    results["insights"]["scene_cuts"] = scenes
                    results["insights"]["scene_summary"] = scene_detector.get_scene_summary(scenes)
                except Exception as e:
                    logger.error(f"Scene detection failed for {job_id}: {e}")
                    results["errors"].append(f"Scene Detection: {str(e)}")
            
            # 3. Caption Generation (only for local files)
            whisper_service = get_whisper_service()
            if whisper_service.enabled and video_path and (video_path.startswith("/") or video_path.startswith("./")):
                try:
                    captions = await whisper_service.generate_captions(video_path)
                    if captions:
                        results["processed_features"].append("captions")
                        results["insights"]["captions_srt_path"] = captions.get("srt_path")
                        results["insights"]["captions_ass_path"] = captions.get("ass_path")
                        results["insights"]["caption_language"] = captions.get("language")
                        results["insights"]["caption_segments"] = captions.get("segments")
                except Exception as e:
                    logger.error(f"Caption generation failed for {job_id}: {e}")
                    results["errors"].append(f"Captions: {str(e)}")
            
            # 4. Vector Embedding
            vector_store = get_vector_store()
            if vector_store.enabled:
                try:
                    content = job.get("input_text", "") or job.get("script", "")
                    embedding = vector_store.generate_embedding(content)
                    results["processed_features"].append("vector_embedding")
                    results["insights"]["vector_embedding"] = embedding
                except Exception as e:
                    logger.error(f"Embedding generation failed for {job_id}: {e}")
                    results["errors"].append(f"Embedding: {str(e)}")
            
            # 5. Audio Quality Analysis (if audio enhancement enabled)
            audio_enhancer = get_audio_enhancer()
            if audio_enhancer.enabled and video_path and (video_path.startswith("/") or video_path.startswith("./")):
                try:
                    quality = await audio_enhancer._analyze_audio_quality(video_path)
                    results["processed_features"].append("audio_quality")
                    results["insights"]["audio_quality"] = quality
                except Exception as e:
                    logger.error(f"Audio quality analysis failed for {job_id}: {e}")
                    results["errors"].append(f"Audio Quality: {str(e)}")
            
            # 6. Cost Calculation
            cost_tracker = get_cost_tracker()
            if cost_tracker.enabled:
                try:
                    # Calculate costs based on job metadata
                    tts_seconds = job.get("tts_duration", 0)
                    processing_seconds = job.get("processing_time", 0)
                    storage_mb = job.get("output_size_mb", 0)
                    
                    ai_features_used = {
                        "embeddings": "vector_embedding" in results["processed_features"],
                        "captions_minutes": results["insights"].get("caption_segments", 0) / 60 if "captions" in results["processed_features"] else 0
                    }
                    
                    costs = await cost_tracker.calculate_job_cost(
                        job_id=job_id,
                        tts_seconds=tts_seconds,
                        processing_seconds=processing_seconds,
                        storage_mb=storage_mb,
                        ai_features_used=ai_features_used
                    )
                    results["processed_features"].append("cost_tracking")
                    results["costs"] = costs
                except Exception as e:
                    logger.error(f"Cost calculation failed for {job_id}: {e}")
                    results["errors"].append(f"Cost Tracking: {str(e)}")
            
            # Store insights in database
            if results["insights"]:
                try:
                    insight_data = results["insights"].copy()
                    insight_data["job_id"] = job_id
                    insight_data["processed_at"] = datetime.utcnow().isoformat()
                    
                    supabase.table("video_insights").upsert(insight_data).execute()
                    results["insights_saved"] = True
                except Exception as e:
                    logger.error(f"Failed to save insights for {job_id}: {e}")
                    results["errors"].append(f"Database Save: {str(e)}")
            
            results["completed_at"] = datetime.utcnow().isoformat()
            results["success"] = len(results["errors"]) == 0
            
            return results
        
        except Exception as e:
            logger.error(f"AI processing failed for {job_id}: {e}")
            return {
                "job_id": job_id,
                "processed": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_health(self) -> Dict[str, Any]:
        """Health check for AI processor"""
        from .vector_store import get_vector_store
        from .whisper_captions import get_whisper_service
        from .scene_detect import get_scene_detector
        from .tagging_service import get_tagging_service
        
        return {
            "enabled": self.enabled,
            "services": {
                "vector_store": get_vector_store().get_health(),
                "whisper_captions": get_whisper_service().get_health(),
                "scene_detection": get_scene_detector().get_health(),
                "tagging": get_tagging_service().get_health()
            }
        }


# Singleton instance
_instance = None

def get_video_ai_processor() -> VideoAIProcessor:
    """Get or create VideoAIProcessor singleton"""
    global _instance
    if _instance is None:
        _instance = VideoAIProcessor()
    return _instance
