# services/api/app/routes/video_internal_alias.py
"""
Internal video engine router with lip-sync capabilities.
Compatible with existing HeyGen API routes.
SRP: API routing only, delegates to services.
"""
import os
import logging
from fastapi import APIRouter, HTTPException, Response, Form
from typing import Optional

logger = logging.getLogger(__name__)

from ..models.video_models import (
    GenerateVideoRequest, GenerateVideoResponse, JobStatusResponse,
    AvatarsResponse, AvatarInfo
)
from ..services.job_store import get_job
from ..services.video_engine_lipsync import enqueue_lipsync

router = APIRouter(prefix="/api/video/video/heygen", tags=["video-internal"])

@router.get("/avatars", response_model=AvatarsResponse)
async def list_avatars():
    """
    List available avatars for internal video engine.
    Compatible with HeyGen API structure.
    """
    return AvatarsResponse(
        items=[
            AvatarInfo(
                id="internal_default",
                label="Internal High-Realism",
                description="High-quality avatar with realistic lip-sync using SadTalker/Wav2Lip",
                thumbnail_url="/api/assets/avatar_thumb.png"
            )
        ]
    )

@router.post("/generate", response_model=GenerateVideoResponse)
async def generate_video_form(
    script: str = Form(..., description="Textul pentru video (max 1000 caractere)"),
    avatar_id: Optional[str] = Form(None, description="ID-ul avatarului (ignored for internal engine)"),
    voice_id: Optional[str] = Form(None, description="ID-ul vocii"),
    style: str = Form("realistic", description="Stilul video"),
    quality: str = Form("high", description="Calitatea video"),
    language: str = Form("ro", description="Limba pentru voice-over"),
    avatar_image_url: Optional[str] = Form(None, description="URL către imaginea avatarului"),
    avatar_video_url: Optional[str] = Form(None, description="URL către video-ul avatarului")
):
    """
    Generate video using internal lip-sync engine.
    Compatible with HeyGen API structure and form data.
    """
    # Check if internal engine is enabled
    if not os.getenv("USE_INTERNAL_VIDEO_ENGINE", "false").lower() in ("1", "true", "yes"):
        raise HTTPException(
            status_code=412, 
            detail="Internal video engine disabled (set USE_INTERNAL_VIDEO_ENGINE=true)"
        )
    
    # Validate input
    if len(script) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Script-ul nu poate depăși 1000 caractere"
        )
    
    if len(script) < 10:
        raise HTTPException(
            status_code=400,
            detail="Script-ul trebuie să aibă cel puțin 10 caractere"
        )
    
    # Require at least one avatar input for lip-sync
    if not avatar_image_url and not avatar_video_url:
        raise HTTPException(
            status_code=400,
            detail="Provide avatar_image_url OR avatar_video_url for lip-sync realism"
        )
    
    try:
        # Enqueue the job
        job_id = await enqueue_lipsync(
            script=script,
            voice_id=voice_id,
            avatar_image_url=avatar_image_url,
            avatar_video_url=avatar_video_url
        )
        
        return GenerateVideoResponse(
            job_id=job_id,
            provider="internal",
            status="queued",
            message="Video generation queued successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to enqueue video generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start video generation: {str(e)}"
        )

@router.post("/generate-json", response_model=GenerateVideoResponse)
async def generate_video_json(request: GenerateVideoRequest):
    """
    Generate video using internal lip-sync engine (JSON input).
    Alternative endpoint for JSON requests.
    """
    # Check if internal engine is enabled
    if not os.getenv("USE_INTERNAL_VIDEO_ENGINE", "false").lower() in ("1", "true", "yes"):
        raise HTTPException(
            status_code=412, 
            detail="Internal video engine disabled (set USE_INTERNAL_VIDEO_ENGINE=true)"
        )
    
    # Require at least one avatar input for lip-sync
    if not request.avatar_image_url and not request.avatar_video_url:
        raise HTTPException(
            status_code=400,
            detail="Provide avatar_image_url OR avatar_video_url for lip-sync realism"
        )
    
    try:
        # Enqueue the job
        job_id = await enqueue_lipsync(
            script=request.script,
            voice_id=request.voice_id,
            avatar_image_url=str(request.avatar_image_url) if request.avatar_image_url else None,
            avatar_video_url=str(request.avatar_video_url) if request.avatar_video_url else None
        )
        
        return GenerateVideoResponse(
            job_id=job_id,
            provider="internal",
            status="queued",
            message="Video generation queued successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to enqueue video generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start video generation: {str(e)}"
        )

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get job status and video URL.
    Compatible with HeyGen API structure.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        video_url=job.get("video_url"),
        error=job.get("error"),
        meta=job.get("meta", {}),
        created_at=job.get("created_at"),
        completed_at=job.get("completed_at")
    )

@router.get("/download/{job_id}")
async def download_video(job_id: str):
    """
    Download generated video file.
    Compatible with HeyGen API structure.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Job not completed (status: {job['status']})"
        )
    
    video_path = job.get("meta", {}).get("output_path")
    if not video_path or not os.path.isfile(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    try:
        with open(video_path, "rb") as f:
            video_data = f.read()
        
        return Response(
            content=video_data,
            media_type="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename=video_{job_id}.mp4"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to read video file {video_path}: {e}")
        raise HTTPException(status_code=500, detail="Failed to read video file")

@router.get("/health")
async def health_check():
    """
    Health check for internal video engine.
    """
    backend = os.getenv("LIPSYNC_BACKEND", "sadtalker")
    engine_enabled = os.getenv("USE_INTERNAL_VIDEO_ENGINE", "false").lower() in ("1", "true", "yes")
    
    # Check if required directories exist
    sadtalker_exists = os.path.exists("third_party/SadTalker")
    wav2lip_exists = os.path.exists("third_party/Wav2Lip")
    
    return {
        "status": "healthy" if engine_enabled else "disabled",
        "engine_enabled": engine_enabled,
        "backend": backend,
        "sadtalker_available": sadtalker_exists,
        "wav2lip_available": wav2lip_exists,
        "ffmpeg_available": _check_ffmpeg(),
        "elevenlabs_configured": bool(os.getenv("ELEVENLABS_API_KEY"))
    }

def _check_ffmpeg() -> bool:
    """Check if FFmpeg is available."""
    try:
        import subprocess
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False
