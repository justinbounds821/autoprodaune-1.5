"""
Social media routes for AutoPro Daune API.

This module provides endpoints for social media management and posting.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import os
import asyncio
import uuid

from ..services.supabase_client import get_supabase_service_instance
from ..services.storage_s3 import upload_file

router = APIRouter(
    prefix="/api/social",
    tags=["social"],
    responses={404: {"description": "Not found"}}
)

@router.get("/summary")
async def get_social_summary() -> Dict[str, Any]:
    """
    Obține sumarul activității pe social media din Supabase.
    
    Returns:
        Dicționar cu sumarul social media
    """
    try:
        return get_supabase_service_instance().social_summary()
        
    except Exception as e:
        logging.error(f"Eroare la obținerea sumarului social: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la sumarul social: {str(e)}")

@router.post("/post-now")
async def post_now(
    platform: str = Query(..., description="Platforma pentru postare (tiktok, instagram, youtube)"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    # Using Supabase service instead of database session
) -> Dict[str, Any]:
    """
    Postează imediat pe o platformă social media.
    
    Args:
        platform: Platforma pentru postare
        background_tasks: Background tasks pentru procesare asincronă
        db: Sesiunea de bază de date
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        # Validăm platforma
        valid_platforms = ["tiktok", "instagram", "youtube"]
        if platform.lower() not in valid_platforms:
            raise HTTPException(status_code=400, detail=f"Platformă invalidă. Valide: {valid_platforms}")
        
        # Adăugăm task-ul în background
        background_tasks.add_task(_post_to_platform, platform.lower())
        
        return {
            "success": True,
            "message": f"Postare pe {platform} inițiată în background",
            "platform": platform,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Eroare la postarea pe {platform}: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la postare: {str(e)}")

@router.get("/posts")
async def get_recent_posts(
    platform: str = Query(None, description="Platforma specifică (opțional)"),
    limit: int = Query(20, description="Numărul maxim de postări"),
) -> Dict[str, Any]:
    """
    Obține postările recente de pe social media din Supabase.
    
    Args:
        platform: Platforma specifică (opțional)
        limit: Numărul maxim de postări
        
    Returns:
        Dicționar cu postările recente
    """
    try:
        # Obține postările din Supabase
        posts = get_supabase_service_instance()._table_select("social_posts", "*", order=("posted_at", True))
        
        # Filtrează după platformă dacă este specificată
        if platform:
            posts = [post for post in posts if post.get("platform") == platform.lower()]
        
        return {
            "posts": posts[:limit],
            "total": len(posts),
            "platform": platform,
            "limit": limit
        }
        
    except Exception as e:
        logging.error(f"Eroare la obținerea postărilor: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la postări: {str(e)}")


@router.post("/posts", response_model=Dict[str, Any])
async def create_social_post(
    post_data: Dict[str, Any]
):
    """
    Creează o postare social media nouă în Supabase.
    
    Args:
        post_data: Datele postării
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        # Creează postarea în Supabase
        payload = {
            "platform": post_data.get("platform"),
            "content": post_data.get("content"),
            "media_url": post_data.get("media_url"),  # NEW: Support for uploaded media
            "media_type": post_data.get("media_type"),  # NEW: image or video
            "engagement": post_data.get("engagement", 0),
            "views": post_data.get("views", 0),
            "likes": post_data.get("likes", 0),
            "comments": post_data.get("comments", 0),
            "shares": post_data.get("shares", 0),
            "revenue": post_data.get("revenue", 0.0),
            "status": post_data.get("status", "draft"),
            "posted_at": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        result = get_supabase_service_instance()._table_insert("social_posts", payload)
        
        return {
            "success": True,
            "message": "Postare social media creată cu succes",
            "data": result
        }
        
    except Exception as e:
        logging.error(f"Eroare la crearea postării: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la crearea postării: {str(e)}")


@router.put("/posts/{post_id}", response_model=Dict[str, Any])
async def update_social_post(
    post_id: int,
    post_data: Dict[str, Any]
):
    """
    Actualizează o postare social media existentă în Supabase.
    
    Args:
        post_id: ID-ul postării
        post_data: Datele noi pentru postare
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        # Actualizează postarea în Supabase
        update_data = {
            "platform": post_data.get("platform"),
            "content": post_data.get("content"),
            "engagement": post_data.get("engagement"),
            "views": post_data.get("views"),
            "likes": post_data.get("likes"),
            "comments": post_data.get("comments"),
            "shares": post_data.get("shares"),
            "revenue": post_data.get("revenue"),
            "status": post_data.get("status")
        }
        
        result = get_supabase_service_instance()._table_update_eq("social_posts", "id", post_id, update_data)
        
        if not result:
            raise HTTPException(status_code=404, detail="Postarea nu a fost găsită")
        
        return {
            "success": True,
            "message": "Postare social media actualizată cu succes",
            "data": result[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Eroare la actualizarea postării: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la actualizarea postării: {str(e)}")


@router.delete("/posts/{post_id}", response_model=Dict[str, Any])
async def delete_social_post(
    post_id: int
):
    """
    Șterge o postare social media din Supabase.
    
    Args:
        post_id: ID-ul postării
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        result = get_supabase_service_instance()._table_delete_eq("social_posts", "id", post_id)
        
        return {
            "success": True,
            "message": "Postare social media ștearsă cu succes",
            "data": result
        }
        
    except Exception as e:
        logging.error(f"Eroare la ștergerea postării: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la ștergerea postării: {str(e)}")

@router.get("/analytics")
async def get_social_analytics(
    platform: str = Query(None, description="Platforma specifică (opțional)"),
    days: int = Query(7, description="Numărul de zile pentru analiză"),
    # Using Supabase service instead of database session
) -> Dict[str, Any]:
    """
    Obține analitica pentru social media.
    
    Args:
        platform: Platforma specifică (opțional)
        days: Numărul de zile pentru analiză
        db: Sesiunea de bază de date
        
    Returns:
        Dicționar cu analitica
    """
    try:
        # Pentru moment, returnăm date mock
        # TODO: Implementați analitica reală
        
        return {
            "period_days": days,
            "platform": platform,
            "total_posts": 15,
            "total_engagement": 4250,
            "total_views": 48500,
            "average_engagement_rate": 4.1,
            "top_performing_post": {
                "id": 3,
                "platform": "youtube",
                "engagement": 2100,
                "content": "Tutorial complet despre procesul de daune"
            },
            "engagement_by_day": [
                {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), "engagement": 100 + i * 50}
                for i in range(days, 0, -1)
            ]
        }
        
    except Exception as e:
        logging.error(f"Eroare la obținerea analiticei: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la analitică: {str(e)}")

@router.post("/bots/start")
async def start_social_bots(
    platforms: List[str] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    # Using Supabase service instead of database session
) -> Dict[str, Any]:
    """
    Pornește bot-urile pentru social media.
    
    Args:
        platforms: Lista de platforme (opțional, toate dacă nu este specificat)
        background_tasks: Background tasks
        db: Sesiunea de bază de date
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        if platforms is None:
            platforms = ["tiktok", "instagram", "youtube"]
        
        # Adăugăm task-urile în background
        for platform in platforms:
            background_tasks.add_task(_start_bot_for_platform, platform)
        
        return {
            "success": True,
            "message": f"Bot-uri pornite pentru platformele: {', '.join(platforms)}",
            "platforms": platforms,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Eroare la pornirea bot-urilor: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la pornirea bot-urilor: {str(e)}")

@router.post("/bots/stop")
async def stop_social_bots(
    platforms: List[str] = None,
    # Using Supabase service instead of database session
) -> Dict[str, Any]:
    """
    Oprește bot-urile pentru social media.
    
    Args:
        platforms: Lista de platforme (opțional, toate dacă nu este specificat)
        db: Sesiunea de bază de date
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        if platforms is None:
            platforms = ["tiktok", "instagram", "youtube"]
        
        # TODO: Implementați oprirea reală a bot-urilor
        
        return {
            "success": True,
            "message": f"Bot-uri oprite pentru platformele: {', '.join(platforms)}",
            "platforms": platforms,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Eroare la oprirea bot-urilor: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la oprirea bot-urilor: {str(e)}")

# Funcții helper pentru background tasks
async def _post_to_platform(platform: str):
    """Funcție helper pentru postarea pe platformă în background."""
    try:
        logging.info(f"Postare pe {platform} în curs...")
        
        # TODO: Implementați logica reală de postare
        # Aici ar trebui să apelați serviciile de postare existente
        
        # Simulăm o postare
        await asyncio.sleep(2)  # Simulăm timpul de procesare
        
        logging.info(f"Postare pe {platform} completată")
        
    except Exception as e:
        logging.error(f"Eroare la postarea pe {platform}: {e}")

async def _start_bot_for_platform(platform: str):
    """Funcție helper pentru pornirea bot-ului pentru o platformă."""
    try:
        logging.info(f"Pornire bot pentru {platform}...")
        
        # TODO: Implementați pornirea reală a bot-ului
        
        logging.info(f"Bot pentru {platform} pornit")
        
    except Exception as e:
        logging.error(f"Eroare la pornirea bot-ului pentru {platform}: {e}")


@router.get("/followers")
async def get_all_followers() -> Dict[str, Any]:
    """
    Get follower/subscriber counts from all social media platforms.
    
    Returns:
        Dictionary with metrics from TikTok, Instagram, and YouTube
    """
    try:
        from ..services.autoposter.tiktok import get_follower_count as tiktok_followers
        from ..services.instagram.api_client import get_follower_count as instagram_followers
        from ..services.youtube.api_client import get_follower_count as youtube_followers
        
        # Get metrics from all platforms
        tiktok_data = tiktok_followers()
        instagram_data = instagram_followers()
        youtube_data = youtube_followers()
        
        # Calculate totals
        total_followers = (
            tiktok_data.get("follower_count", 0) +
            instagram_data.get("follower_count", 0) +
            youtube_data.get("subscriber_count", 0)
        )
        
        total_content = (
            tiktok_data.get("video_count", 0) +
            instagram_data.get("media_count", 0) +
            youtube_data.get("video_count", 0)
        )
        
        return {
            "success": True,
            "platforms": {
                "tiktok": tiktok_data,
                "instagram": instagram_data,
                "youtube": youtube_data
            },
            "totals": {
                "total_followers": total_followers,
                "total_content": total_content
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error getting follower counts: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get follower counts: {str(e)}"
        )


@router.get("/followers/{platform}")
async def get_platform_followers(platform: str) -> Dict[str, Any]:
    """
    Get follower count for a specific platform.
    
    Args:
        platform: Platform name (tiktok, instagram, youtube)
        
    Returns:
        Dictionary with platform-specific metrics
    """
    try:
        platform = platform.lower()
        
        if platform == "tiktok":
            from ..services.autoposter.tiktok import get_follower_count
            data = get_follower_count()
        elif platform == "instagram":
            from ..services.instagram.api_client import get_follower_count
            data = get_follower_count()
        elif platform == "youtube":
            from ..services.youtube.api_client import get_follower_count
            data = get_follower_count()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform: {platform}. Choose from: tiktok, instagram, youtube"
            )
        
        return {
            "success": True,
            "data": data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting {platform} followers: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get {platform} followers: {str(e)}"
        )


# ==================== MEDIA UPLOAD ENDPOINT ====================

@router.post("/upload-video")
async def upload_video_for_posting(
    video: UploadFile = File(...),
    caption: str = Form(...),
    platforms: str = Form(...),
    scheduled_for: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Upload video and create social media post.
    
    Steps:
    1. Validate video file
    2. Upload to Supabase Storage
    3. Create post record in database
    4. Return success with media URL
    """
    try:
        # Validate file type
        if not video.content_type or not video.content_type.startswith('video/'):
            raise HTTPException(
                status_code=400,
                detail="Only video files are allowed"
            )
        
        # Validate file size (50MB max)
        video_content = await video.read()
        file_size = len(video_content)
        max_size = 50 * 1024 * 1024  # 50MB
        
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"Video size ({file_size / 1024 / 1024:.1f}MB) exceeds maximum (50MB)"
            )
        
        # Generate unique filename
        file_ext = video.filename.split('.')[-1] if '.' in video.filename else 'mp4'
        unique_key = f"social_media/{uuid.uuid4().hex}.{file_ext}"
        
        # Upload to Supabase Storage
        from io import BytesIO
        video_file_obj = BytesIO(video_content)
        media_url = upload_file(video_file_obj, unique_key, video.content_type)
        
        # Parse platforms
        import json
        platform_list = json.loads(platforms) if isinstance(platforms, str) else platforms
        
        # Create post record for each platform
        created_posts = []
        for platform in platform_list:
            post_payload = {
                "platform": platform,
                "content": caption,
                "media_url": media_url,
                "media_type": "video",
                "status": "scheduled" if scheduled_for else "ready",
                "scheduled_for": scheduled_for,
                "posted_at": datetime.now().isoformat() if not scheduled_for else None,
                "created_at": datetime.now().isoformat()
            }
            
            result = get_supabase_service_instance()._table_insert("social_posts", post_payload)
            created_posts.append(result)
        
        logging.info(f"Video uploaded: {unique_key}, platforms: {platform_list}")
        
        return {
            "success": True,
            "message": f"Video uploaded successfully for {len(platform_list)} platform(s)",
            "media_url": media_url,
            "posts": created_posts
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error uploading video: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload video: {str(e)}"
        )
