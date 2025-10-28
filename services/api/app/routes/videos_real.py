"""
REAL Video Routes - AutoPro Daune
MoviePy + HeyGen generation with authentication
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from uuid import UUID
from ..middleware.jwt_auth import get_current_user, CurrentUser
from ..services.video_service_real import get_video_service, VideoServiceReal
from pydantic import BaseModel

router = APIRouter(prefix="/api/videos", tags=["videos-real"])

class VideoGenerateRequest(BaseModel):
    title: str
    script: str
    provider: str = "moviepy"  # moviepy, heygen, pika
    avatar_id: Optional[str] = "professional"
    background_image: Optional[str] = None

@router.post("/generate")
async def generate_video(
    request: VideoGenerateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    video_service: VideoServiceReal = Depends(get_video_service)
):
    """
    Generate video using specified provider
    Providers: moviepy (internal), heygen, pika
    """
    if request.provider == "moviepy":
        return await video_service.generate_moviepy_video(
            user_id=current_user.id,
            title=request.title,
            script=request.script,
            background_image=request.background_image
        )
    elif request.provider == "heygen":
        return await video_service.generate_heygen_video(
            user_id=current_user.id,
            title=request.title,
            script=request.script,
            avatar_id=request.avatar_id
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Provider '{request.provider}' not yet implemented"
        )

@router.get("")
async def list_videos(
    status: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
    video_service: VideoServiceReal = Depends(get_video_service)
):
    """List videos with filters"""
    return await video_service.list_videos(
        user_id=current_user.id,
        status=status,
        provider=provider,
        limit=limit,
        offset=offset
    )

@router.get("/{video_id}")
async def get_video(
    video_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    video_service: VideoServiceReal = Depends(get_video_service)
):
    """Get video by ID"""
    return await video_service.get_video(
        video_id=video_id,
        user_id=current_user.id
    )

@router.delete("/{video_id}")
async def delete_video(
    video_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    video_service: VideoServiceReal = Depends(get_video_service)
):
    """Delete video"""
    success = await video_service.delete_video(
        video_id=video_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {"success": True, "message": "Video deleted"}
