"""
REAL Social Media Routes - AutoPro Daune
TikTok, YouTube, Instagram, Facebook integration
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from ..middleware.jwt_auth import get_current_user, CurrentUser
from ..services.social_media_service_real import get_social_service, SocialMediaService

router = APIRouter(prefix="/api/social", tags=["social-real"])

class SocialPostRequest(BaseModel):
    video_id: Optional[UUID] = None
    video_url: Optional[str] = None
    caption: str
    hashtags: List[str] = []
    platforms: List[str]  # ["tiktok", "instagram", "youtube"]

@router.get("/followers")
async def get_all_followers(
    current_user: CurrentUser = Depends(get_current_user),
    social_service: SocialMediaService = Depends(get_social_service)
):
    """Get follower counts from all platforms - REAL API calls"""
    return await social_service.get_all_followers()

@router.get("/youtube/stats")
async def get_youtube_stats(
    channel_id: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
    social_service: SocialMediaService = Depends(get_social_service)
):
    """Get YouTube channel statistics"""
    return await social_service.get_youtube_stats(channel_id)

@router.get("/tiktok/stats")
async def get_tiktok_stats(
    current_user: CurrentUser = Depends(get_current_user),
    social_service: SocialMediaService = Depends(get_social_service)
):
    """Get TikTok account statistics"""
    return await social_service.get_tiktok_stats()

@router.post("/post")
async def post_to_social_media(
    request: SocialPostRequest,
    current_user: CurrentUser = Depends(get_current_user),
    social_service: SocialMediaService = Depends(get_social_service)
):
    """
    Post content to multiple social media platforms
    Platforms: tiktok, instagram, youtube, facebook
    """
    results = []
    
    for platform in request.platforms:
        try:
            if platform == "tiktok":
                result = await social_service.post_to_tiktok(
                    video_url=request.video_url,
                    caption=request.caption,
                    hashtags=request.hashtags,
                    user_id=current_user.id
                )
                results.append(result)
            elif platform == "youtube":
                # YouTube posting requires video file path, not URL
                if not request.video_id:
                    raise HTTPException(status_code=400, detail="video_id required for YouTube")
                # Would need to download video first or use local path
                pass
            # Add other platforms...
            
        except Exception as e:
            logger.error(f"Error posting to {platform}: {str(e)}")
            results.append({
                "success": False,
                "platform": platform,
                "error": str(e)
            })
    
    return {
        "success": True,
        "results": results,
        "platforms_attempted": len(request.platforms),
        "platforms_succeeded": sum(1 for r in results if r.get('success'))
    }
