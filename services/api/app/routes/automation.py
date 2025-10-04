"""
Automation routes for AutoPro Daune API.

This module provides endpoints for automation management including:
- 3x daily video posting automation
- WhatsApp bot automation
- Referral system automation
- Performance tracking automation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import asyncio

from ..services.supabase_client import get_supabase_service_instance
from ..services.social_poster import SocialPoster
from ..services.whatsapp_bot import WhatsAppBot

router = APIRouter(
    prefix="/api/automation",
    tags=["automation"],
    responses={404: {"description": "Not found"}}
)

class AutomationSchedule(BaseModel):
    enabled: bool = True
    posting_times: List[str] = Field(default=["09:00", "15:00", "21:00"])
    platforms: List[str] = Field(default=["tiktok", "facebook", "instagram"])
    content_types: List[str] = Field(default=["educational", "testimonial", "promotional"])

class VideoGenerationRequest(BaseModel):
    template_type: str = Field(..., description="Type: educational, testimonial, promotional")
    target_platforms: List[str] = Field(default=["tiktok", "facebook", "instagram"])
    scheduled_for: Optional[str] = None

@router.get("/status")
async def get_automation_status() -> Dict[str, Any]:
    """
    Obține statusul sistemului de automatizare.

    Returns:
        Dicționar cu statusul automatizării
    """
    try:
        supabase_service = get_supabase_service_instance()

        # Get recent automation activities
        recent_posts = supabase_service.client.table("social_posts").select("*").order("created_at", desc=True).limit(10).execute()
        recent_videos = supabase_service.client.table("video_jobs").select("*").order("created_at", desc=True).limit(5).execute()

        # Calculate stats
        today = datetime.now().date()
        today_posts = [p for p in recent_posts.data if datetime.fromisoformat(p["created_at"]).date() == today]

        return {
            "automation_active": True,
            "daily_target": 3,
            "posts_today": len(today_posts),
            "next_scheduled_post": "15:00",  # This would be dynamic
            "recent_posts": recent_posts.data,
            "recent_videos": recent_videos.data,
            "performance": {
                "total_views_today": sum(p.get("views", 0) for p in today_posts),
                "total_engagement_today": sum(p.get("engagement", 0) for p in today_posts),
                "leads_generated_today": sum(p.get("leads_generated", 0) for p in today_posts)
            }
        }

    except Exception as e:
        logging.error(f"Error getting automation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedule/configure")
async def configure_schedule(schedule_data: AutomationSchedule) -> Dict[str, Any]:
    """
    Configurează programul de automatizare.
    """
    try:
        # Store schedule in database
        supabase_service = get_supabase_service_instance()

        schedule_config = {
            "enabled": schedule_data.enabled,
            "posting_times": schedule_data.posting_times,
            "platforms": schedule_data.platforms,
            "content_types": schedule_data.content_types,
            "updated_at": datetime.now().isoformat()
        }

        # Store or update automation config
        result = supabase_service.client.table("automation_config").upsert(schedule_config).execute()

        return {
            "success": True,
            "message": "Automation schedule configured successfully",
            "config": schedule_config
        }

    except Exception as e:
        logging.error(f"Error configuring schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video/generate-and-post")
async def generate_and_post_video(
    video_request: VideoGenerationRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Generează și postează un video automat.
    """
    try:
        # Generate unique job ID
        job_id = f"auto_{video_request.template_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create video generation job
        supabase_service = get_supabase_service_instance()

        video_job = {
            "client_job_id": job_id,
            "template_type": video_request.template_type,
            "target_platforms": video_request.target_platforms,
            "status": "queued",
            "progress": 0,
            "scheduled_for": video_request.scheduled_for or datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        result = supabase_service.client.table("video_jobs").insert(video_job).execute()

        # Schedule background processing
        background_tasks.add_task(
            _process_video_generation_and_posting,
            job_id,
            video_request.template_type,
            video_request.target_platforms
        )

        return {
            "success": True,
            "message": "Video generation and posting scheduled",
            "job_id": job_id,
            "template_type": video_request.template_type,
            "platforms": video_request.target_platforms
        }

    except Exception as e:
        logging.error(f"Error scheduling video generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/daily-cycle/trigger")
async def trigger_daily_cycle(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Declanșează ciclul zilnic de automatizare (3 videouri).
    """
    try:
        # Check if already run today
        today = datetime.now().date()
        supabase_service = get_supabase_service_instance()

        today_start = datetime.combine(today, datetime.min.time()).isoformat()
        today_posts = supabase_service.client.table("social_posts").select("*").gte("created_at", today_start).execute()

        if len(today_posts.data) >= 3:
            return {
                "success": False,
                "message": "Daily cycle already completed",
                "posts_today": len(today_posts.data)
            }

        # Schedule the remaining posts
        content_types = ["educational", "testimonial", "promotional"]
        remaining_posts = 3 - len(today_posts.data)

        scheduled_jobs = []

        for i in range(remaining_posts):
            content_type = content_types[i % len(content_types)]
            job_id = f"daily_{content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"

            background_tasks.add_task(
                _process_video_generation_and_posting,
                job_id,
                content_type,
                ["tiktok", "facebook", "instagram"]
            )

            scheduled_jobs.append({
                "job_id": job_id,
                "content_type": content_type,
                "platforms": ["tiktok", "facebook", "instagram"]
            })

        return {
            "success": True,
            "message": f"Daily cycle triggered - {remaining_posts} videos scheduled",
            "scheduled_jobs": scheduled_jobs,
            "posts_today": len(today_posts.data)
        }

    except Exception as e:
        logging.error(f"Error triggering daily cycle: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_automation_performance(
    days: int = Query(7, description="Number of days to analyze")
) -> Dict[str, Any]:
    """
    Obține performanța sistemului de automatizare.
    """
    try:
        supabase_service = get_supabase_service_instance()

        # Get posts from specified period
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        posts = supabase_service.client.table("social_posts").select("*").gte("created_at", start_date).execute()

        # Get leads from same period
        leads = supabase_service.client.table("leads").select("*").gte("created_at", start_date).execute()

        # Get referrals
        referrals = supabase_service.client.table("referrals").select("*").gte("created_at", start_date).execute()

        # Calculate metrics
        total_posts = len(posts.data)
        total_views = sum(p.get("views", 0) for p in posts.data)
        total_engagement = sum(p.get("engagement", 0) for p in posts.data)
        total_clicks = sum(p.get("clicks", 0) for p in posts.data)
        total_leads = len(leads.data)
        total_referrals = len(referrals.data)

        # Calculate ROI metrics
        referral_earnings = len([r for r in referrals.data if r.get("status") == "completed"]) * 200  # 200 LEI per referral

        # Daily breakdown
        daily_stats = {}
        for post in posts.data:
            post_date = datetime.fromisoformat(post["created_at"]).date().isoformat()
            if post_date not in daily_stats:
                daily_stats[post_date] = {"posts": 0, "views": 0, "engagement": 0, "leads": 0}

            daily_stats[post_date]["posts"] += 1
            daily_stats[post_date]["views"] += post.get("views", 0)
            daily_stats[post_date]["engagement"] += post.get("engagement", 0)

        for lead in leads.data:
            lead_date = datetime.fromisoformat(lead["created_at"]).date().isoformat()
            if lead_date in daily_stats:
                daily_stats[lead_date]["leads"] += 1

        return {
            "period_days": days,
            "summary": {
                "total_posts": total_posts,
                "total_views": total_views,
                "total_engagement": total_engagement,
                "total_clicks": total_clicks,
                "total_leads_generated": total_leads,
                "total_referrals": total_referrals,
                "referral_earnings_lei": referral_earnings,
                "avg_posts_per_day": round(total_posts / days, 1),
                "engagement_rate": round((total_engagement / total_views * 100), 2) if total_views > 0 else 0,
                "lead_conversion_rate": round((total_leads / total_clicks * 100), 2) if total_clicks > 0 else 0
            },
            "daily_breakdown": daily_stats,
            "top_performing_posts": sorted(posts.data, key=lambda x: x.get("engagement", 0), reverse=True)[:5]
        }

    except Exception as e:
        logging.error(f"Error getting automation performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/whatsapp/optimize")
async def optimize_whatsapp_responses(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Optimizează răspunsurile WhatsApp Bot.
    """
    try:
        background_tasks.add_task(_optimize_whatsapp_automation)

        return {
            "success": True,
            "message": "WhatsApp optimization started",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logging.error(f"Error optimizing WhatsApp: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task functions
async def _process_video_generation_and_posting(job_id: str, template_type: str, platforms: List[str]):
    """
    Procesează generarea și postarea unui video în background.
    """
    try:
        logging.info(f"Starting video generation for job {job_id}, template: {template_type}")

        supabase_service = get_supabase_service_instance()

        # Update job status to processing
        supabase_service.client.table("video_jobs").update({
            "status": "processing",
            "progress": 10,
            "updated_at": datetime.now().isoformat()
        }).eq("client_job_id", job_id).execute()

        # Simulate video generation (in real implementation, this would call actual video services)
        await asyncio.sleep(30)  # Simulate processing time

        # Update progress
        supabase_service.client.table("video_jobs").update({
            "progress": 60,
            "updated_at": datetime.now().isoformat()
        }).eq("client_job_id", job_id).execute()

        # Create mock video URL (in real implementation, this would be the actual generated video)
        video_url = f"https://storage.autoprodaune.com/videos/{job_id}.mp4"

        # Post to social media platforms
        social_poster = SocialPoster()

        content_templates = {
            "educational": "🚗 Știai că poți obține despăgubiri pentru daunele auto în doar 24h? #AutoProDaune #Daune #Asigurari",
            "testimonial": "✨ Client mulțumit: 'Am primit despăgubirile în 2 zile cu AutoPro Daune!' #Testimonial #ClientMultumit",
            "promotional": "💰 Câștigă 200 LEI pentru fiecare prieten recomandat! Înregistrează-te acum! #Referral #200Lei"
        }

        content = content_templates.get(template_type, "🚗 AutoPro Daune - Expertul tău în despăgubiri auto!")

        # Create social media post
        post_data = {
            "title": f"AutoPro Daune - {template_type.title()}",
            "content": content,
            "platforms": platforms,
            "video_url": video_url,
            "status": "published",
            "views": 0,
            "engagement": 0,
            "clicks": 0,
            "leads_generated": 0,
            "created_at": datetime.now().isoformat()
        }

        result = supabase_service.client.table("social_posts").insert(post_data).execute()

        # Complete video job
        supabase_service.client.table("video_jobs").update({
            "status": "completed",
            "progress": 100,
            "output_url": video_url,
            "updated_at": datetime.now().isoformat()
        }).eq("client_job_id", job_id).execute()

        logging.info(f"Video generation and posting completed for job {job_id}")

    except Exception as e:
        logging.error(f"Error in video generation task for job {job_id}: {e}")

        # Update job status to failed
        supabase_service = get_supabase_service_instance()
        supabase_service.client.table("video_jobs").update({
            "status": "failed",
            "error_message": str(e),
            "updated_at": datetime.now().isoformat()
        }).eq("client_job_id", job_id).execute()

async def _optimize_whatsapp_automation():
    """
    Optimizează automatizarea WhatsApp.
    """
    try:
        logging.info("Starting WhatsApp automation optimization")

        # Analyze recent WhatsApp conversations
        supabase_service = get_supabase_service_instance()

        # Get recent leads from WhatsApp
        recent_leads = supabase_service.client.table("leads").select("*").eq("source", "whatsapp").order("created_at", desc=True).limit(50).execute()

        # Analyze response patterns and optimize bot responses
        # This is where AI/ML optimization would happen

        logging.info("WhatsApp automation optimization completed")

    except Exception as e:
        logging.error(f"Error in WhatsApp optimization: {e}")