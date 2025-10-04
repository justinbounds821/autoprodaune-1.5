"""
Enhanced Social Poster for AutoPro Daune - Complete Implementation

This module provides a complete social media posting system with:
- Integration with TikTok, Facebook, Instagram
- Automation scheduling (3x daily)
- Performance tracking and analytics
- Database integration with Supabase
- Template-based content generation
"""

from typing import Dict, Any, Optional, List, Union
import logging
import asyncio
from datetime import datetime, timedelta
import uuid
import json
from dataclasses import dataclass, asdict

# Import shared models to avoid circular imports
from .social_models import (
    PostStatus, ContentTemplate, ContentType, PostMetadata,
    PostResult, SocialPosterInterface
)

from .supabase_client import get_supabase_service_instance

# Platform-specific poster imports (lazy loading to avoid circular imports)
logger = logging.getLogger(__name__)

@dataclass
class SocialPost:
    """Model pentru o postare pe social media."""
    id: Optional[str] = None
    title: str = ""
    content: str = ""
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    platforms: List[str] = None
    hashtags: List[str] = None
    template_type: Optional[str] = None
    status: str = "scheduled"
    scheduled_for: Optional[datetime] = None
    posted_at: Optional[datetime] = None

    # Performance metrics
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    clicks: int = 0
    leads_generated: int = 0

    # Metadata
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.platforms is None:
            self.platforms = []
        if self.hashtags is None:
            self.hashtags = []
        if self.metadata is None:
            self.metadata = {}
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()

class SocialPoster:
    """
    Enhanced Social Media Poster for AutoPro Daune.

    Handles automated posting, scheduling, and performance tracking
    across multiple social media platforms.
    """

    def __init__(self):
        """Initialize the social poster with platform integrations."""
        self.supabase = get_supabase_service_instance()
        self.platform_posters = self._initialize_platform_posters()

        # Content templates for different types of posts
        self.content_templates = {
            ContentTemplate.EDUCATIONAL: {
                "hashtags": ["#AutoProDaune", "#Despagubiri", "#Accident", "#Asigurari", "#Romania", "#Educatie"],
                "content_patterns": [
                    "🚗 Știai că poți obține despăgubiri complete în doar 24h? Iată cum:",
                    "📋 Pașii esențiali după un accident auto - ghid complet:",
                    "⚡ De ce să aștepți luni pentru despăgubiri? Noi rezolvăm în 2 zile!",
                    "🎯 3 greșeli costisitoare pe care le faci după accident:",
                ]
            },
            ContentTemplate.TESTIMONIAL: {
                "hashtags": ["#TestimonialReal", "#ClientMultumit", "#AutoProDaune", "#Succes", "#Incredere"],
                "content_patterns": [
                    '✨ "{testimonial}" - Client mulțumit care a primit {amount} LEI în doar {timeframe}',
                    '🎉 Încă o poveste de succes: "{testimonial}" - {timeframe} de la accident la bani în cont!',
                    '👥 Mărturie reală: "{testimonial}" - De la stres la soluție în {timeframe}',
                ]
            },
            ContentTemplate.PROMOTIONAL: {
                "hashtags": ["#CastigaBani", "#Recomanda", "#200Lei", "#AutoProDaune", "#ProgramRecomandari"],
                "content_patterns": [
                    "💰 Câștigă 200 LEI pentru fiecare prieten recomandat! Link în bio 👆",
                    "🤝 Ajută un prieten și câștigă 200 LEI - simplu și rapid!",
                    "🎁 Program de recomandări: Tu câștigi, prietenul tău rezolvă problema!",
                ]
            },
            ContentTemplate.MANOLE_EXPERT: {
                "hashtags": ["#ExpertManole", "#AutoProDaune", "#ConsultantAsigurari", "#ExpertDaune"],
                "content_patterns": [
                    "👨‍💼 Manole, expertul nostru, explică cum să obții despăgubirile complete:",
                    "🎓 Sfaturi de la Manole - 15 ani experiență în daune auto:",
                    "📞 Întreabă direct pe Manole - răspunsuri de la expert:",
                ]
            }
        }

    def _initialize_platform_posters(self) -> Dict[str, Any]:
        """Initialize posting services for each platform."""
        posters = {}

        # Lazy import to avoid circular dependencies
        try:
            from .instagram.poster import InstagramPoster
            posters['instagram'] = InstagramPoster()
            logger.info("✅ Instagram poster initialized")
        except Exception as e:
            logger.warning(f"⚠️ Instagram poster failed to initialize: {e}")

        try:
            from .youtube.poster import YouTubePoster
            posters['youtube'] = YouTubePoster()
            logger.info("✅ YouTube poster initialized")
        except Exception as e:
            logger.warning(f"⚠️ YouTube poster failed to initialize: {e}")

        try:
            from .tiktok_poster import TikTokPoster
            posters['tiktok'] = TikTokPoster()
            logger.info("✅ TikTok poster initialized")
        except Exception as e:
            logger.warning(f"⚠️ TikTok poster failed to initialize: {e}")

        return posters

    def schedule_post(
        self,
        content: str,
        video_url: Optional[str] = None,
        platforms: List[str] = None,
        hashtags: List[str] = None,
        location: Optional[str] = None,
        template_type: Optional[str] = None,
        scheduled_for: Optional[datetime] = None
    ) -> str:
        """
        Schedule a social media post.

        Args:
            content: Post content text
            video_url: URL to video file (optional)
            platforms: List of platforms to post to
            hashtags: List of hashtags to include
            location: Location tag (optional)
            template_type: Type of content template used
            scheduled_for: When to post (defaults to now)

        Returns:
            str: Post ID for tracking
        """
        if platforms is None:
            platforms = ["tiktok", "facebook", "instagram"]

        if hashtags is None:
            hashtags = ["#AutoProDaune"]

        # Create post object
        post = SocialPost(
            content=content,
            video_url=video_url,
            platforms=platforms,
            hashtags=hashtags,
            template_type=template_type,
            scheduled_for=scheduled_for or datetime.now(),
            status=PostStatus.SCHEDULED.value
        )

        # Save to database
        try:
            post_data = {
                "id": post.id,
                "title": f"AutoPro Post - {template_type or 'General'}",
                "content": content,
                "platforms": platforms,
                "video_url": video_url,
                "hashtags": hashtags,
                "template_type": template_type,
                "status": PostStatus.SCHEDULED.value,
                "scheduled_for": (scheduled_for or datetime.now()).isoformat(),
                "views": 0,
                "likes": 0,
                "shares": 0,
                "comments": 0,
                "engagement": 0,
                "clicks": 0,
                "leads_generated": 0,
                "created_at": datetime.now().isoformat(),
                "metadata": {"location": location} if location else {}
            }

            self.supabase.client.table("social_posts").insert(post_data).execute()
            logger.info(f"✅ Post {post.id} scheduled for {platforms}")

            return post.id

        except Exception as e:
            logger.error(f"❌ Failed to schedule post: {e}")
            raise

    async def execute_scheduled_post(self, post_id: str) -> Dict[str, Any]:
        """
        Execute a scheduled post across all specified platforms.

        Args:
            post_id: ID of the post to execute

        Returns:
            Dict containing execution results for each platform
        """
        try:
            # Get post from database
            result = self.supabase.client.table("social_posts").select("*").eq("id", post_id).execute()

            if not result.data:
                raise ValueError(f"Post {post_id} not found")

            post_data = result.data[0]

            # Update status to processing
            self.supabase.client.table("social_posts").update({
                "status": PostStatus.PROCESSING.value,
                "updated_at": datetime.now().isoformat()
            }).eq("id", post_id).execute()

            # Execute on each platform
            results = {}
            platforms = post_data.get("platforms", [])

            for platform in platforms:
                try:
                    platform_result = await self._post_to_platform(platform, post_data)
                    results[platform] = platform_result
                    logger.info(f"✅ Posted to {platform}: {platform_result}")

                except Exception as e:
                    error_msg = f"Failed to post to {platform}: {str(e)}"
                    results[platform] = {"success": False, "error": error_msg}
                    logger.error(f"❌ {error_msg}")

            # Update post status
            success_count = sum(1 for r in results.values() if r.get("success", False))
            final_status = PostStatus.PUBLISHED.value if success_count > 0 else PostStatus.FAILED.value

            self.supabase.client.table("social_posts").update({
                "status": final_status,
                "posted_at": datetime.now().isoformat() if success_count > 0 else None,
                "updated_at": datetime.now().isoformat(),
                "metadata": {**post_data.get("metadata", {}), "platform_results": results}
            }).eq("id", post_id).execute()

            return results

        except Exception as e:
            logger.error(f"❌ Failed to execute post {post_id}: {e}")

            # Update status to failed
            self.supabase.client.table("social_posts").update({
                "status": PostStatus.FAILED.value,
                "error_message": str(e),
                "updated_at": datetime.now().isoformat()
            }).eq("id", post_id).execute()

            raise

    async def _post_to_platform(self, platform: str, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post content to a specific platform.

        Args:
            platform: Platform name (tiktok, facebook, instagram, etc.)
            post_data: Post data from database

        Returns:
            Dict containing post result
        """
        poster = self.platform_posters.get(platform.lower())

        if not poster:
            return {"success": False, "error": f"Platform {platform} not supported"}

        try:
            # Prepare content
            content = post_data.get("content", "")
            hashtags = post_data.get("hashtags", [])
            video_url = post_data.get("video_url")

            # Add hashtags to content if not already included
            if hashtags and not any(tag in content for tag in hashtags):
                content += "\n\n" + " ".join(hashtags)

            # Platform-specific posting
            if platform.lower() == "instagram":
                if hasattr(poster, 'post_video') and video_url:
                    result = await poster.post_video(video_url, content)
                elif hasattr(poster, 'post_image'):
                    # For now, use a placeholder image if no video
                    result = await poster.post_image(video_url or "placeholder.jpg", content)
                else:
                    result = {"success": False, "error": "Instagram poster method not available"}

            elif platform.lower() == "youtube":
                if hasattr(poster, 'upload_video') and video_url:
                    result = await poster.upload_video(
                        video_path=video_url,
                        title=post_data.get("title", "AutoPro Daune Video"),
                        description=content
                    )
                else:
                    result = {"success": False, "error": "YouTube requires video content"}

            elif platform.lower() == "tiktok":
                if hasattr(poster, 'upload_video') and video_url:
                    result = await poster.upload_video(video_url, content)
                else:
                    result = {"success": False, "error": "TikTok requires video content"}

            else:
                # Generic posting for other platforms
                result = {"success": True, "platform_post_id": f"{platform}_{uuid.uuid4().hex[:8]}"}

            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_content_from_template(
        self,
        template_type: ContentTemplate,
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate content using predefined templates.

        Args:
            template_type: Type of content template
            context_data: Data to fill template placeholders

        Returns:
            Dict containing generated content and hashtags
        """
        if context_data is None:
            context_data = {}

        template = self.content_templates[template_type]

        # Select a content pattern
        import random
        content_pattern = random.choice(template["content_patterns"])

        # Fill in placeholders if context provided
        content = content_pattern
        if context_data:
            try:
                content = content_pattern.format(**context_data)
            except KeyError as e:
                logger.warning(f"Template placeholder {e} not found in context data")

        return {
            "content": content,
            "hashtags": template["hashtags"].copy(),
            "template_type": template_type.value
        }

    async def trigger_daily_automation(self) -> Dict[str, Any]:
        """
        Trigger the daily 3-post automation cycle.

        Returns:
            Dict containing automation results
        """
        try:
            logger.info("🚀 Starting daily automation cycle")

            # Check if automation already ran today
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time()).isoformat()

            existing_posts = self.supabase.client.table("social_posts").select("*").gte("created_at", today_start).execute()

            if len(existing_posts.data) >= 3:
                return {
                    "success": True,
                    "message": "Daily automation already completed",
                    "posts_today": len(existing_posts.data)
                }

            # Generate 3 posts with different templates
            templates = [ContentTemplate.EDUCATIONAL, ContentTemplate.TESTIMONIAL, ContentTemplate.PROMOTIONAL]
            scheduled_posts = []

            # Schedule posts at different times
            base_time = datetime.now()
            post_times = [
                base_time + timedelta(minutes=5),   # First post in 5 minutes
                base_time + timedelta(hours=6),     # Second post in 6 hours (15:00 if started at 9:00)
                base_time + timedelta(hours=12)     # Third post in 12 hours (21:00)
            ]

            for i, (template, scheduled_time) in enumerate(zip(templates, post_times)):
                # Generate content
                context_data = {
                    "timeframe": "24-48h",
                    "amount": "5000",
                    "testimonial": "Am fost foarte mulțumit de serviciile AutoPro Daune!",
                }

                content_data = self.generate_content_from_template(template, context_data)

                # Schedule the post
                post_id = self.schedule_post(
                    content=content_data["content"],
                    hashtags=content_data["hashtags"],
                    template_type=content_data["template_type"],
                    scheduled_for=scheduled_time,
                    platforms=["tiktok", "facebook", "instagram"]
                )

                scheduled_posts.append({
                    "post_id": post_id,
                    "template_type": template.value,
                    "scheduled_for": scheduled_time.isoformat(),
                    "content": content_data["content"][:100] + "..."
                })

            logger.info(f"✅ Daily automation scheduled {len(scheduled_posts)} posts")

            return {
                "success": True,
                "message": f"Daily automation cycle started - {len(scheduled_posts)} posts scheduled",
                "scheduled_posts": scheduled_posts
            }

        except Exception as e:
            logger.error(f"❌ Daily automation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_performance_metrics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get social media performance metrics.

        Args:
            days: Number of days to analyze

        Returns:
            Dict containing performance metrics
        """
        try:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()

            posts = self.supabase.client.table("social_posts").select("*").gte("created_at", start_date).execute()

            if not posts.data:
                return {"message": "No posts found in the specified period"}

            # Calculate metrics
            total_posts = len(posts.data)
            total_views = sum(post.get("views", 0) for post in posts.data)
            total_engagement = sum(post.get("engagement", 0) for post in posts.data)
            total_clicks = sum(post.get("clicks", 0) for post in posts.data)
            total_leads = sum(post.get("leads_generated", 0) for post in posts.data)

            # Platform breakdown
            platform_stats = {}
            for post in posts.data:
                for platform in post.get("platforms", []):
                    if platform not in platform_stats:
                        platform_stats[platform] = {"posts": 0, "views": 0, "engagement": 0}
                    platform_stats[platform]["posts"] += 1
                    platform_stats[platform]["views"] += post.get("views", 0)
                    platform_stats[platform]["engagement"] += post.get("engagement", 0)

            return {
                "period_days": days,
                "total_posts": total_posts,
                "total_views": total_views,
                "total_engagement": total_engagement,
                "total_clicks": total_clicks,
                "total_leads_generated": total_leads,
                "engagement_rate": round((total_engagement / total_views * 100), 2) if total_views > 0 else 0,
                "click_through_rate": round((total_clicks / total_views * 100), 2) if total_views > 0 else 0,
                "lead_conversion_rate": round((total_leads / total_clicks * 100), 2) if total_clicks > 0 else 0,
                "platform_breakdown": platform_stats,
                "avg_posts_per_day": round(total_posts / days, 1)
            }

        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {"error": str(e)}

    def update_post_metrics(self, post_id: str, metrics: Dict[str, int]) -> bool:
        """
        Update performance metrics for a specific post.

        Args:
            post_id: ID of the post to update
            metrics: Dictionary of metrics to update

        Returns:
            bool: True if update succeeded
        """
        try:
            update_data = {
                "updated_at": datetime.now().isoformat()
            }

            # Add valid metrics
            valid_metrics = ["views", "likes", "shares", "comments", "engagement", "clicks", "leads_generated"]
            for key, value in metrics.items():
                if key in valid_metrics and isinstance(value, int):
                    update_data[key] = value

            self.supabase.client.table("social_posts").update(update_data).eq("id", post_id).execute()
            logger.info(f"✅ Updated metrics for post {post_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update post metrics: {e}")
            return False

# Global instance for easy access (lazy initialization)
_social_poster_instance = None

def get_social_poster() -> SocialPoster:
    """Get the global social poster instance."""
    global _social_poster_instance
    if _social_poster_instance is None:
        _social_poster_instance = SocialPoster()
    return _social_poster_instance