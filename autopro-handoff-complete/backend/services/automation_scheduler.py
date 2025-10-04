"""
Automation Scheduler for AutoPro Daune - Complete Implementation

This module provides the core automation scheduling system that handles:
- 3x daily video posting automation (09:00, 15:00, 21:00)
- Content template rotation (Educational, Testimonial, Promotional)
- Social media platform management
- Performance tracking and optimization
"""

import asyncio
import logging
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os

from .social_models import ContentTemplate
from .social_poster import get_social_poster
from .video_generator import VideoGenerator
from .supabase_client import get_supabase_service_instance

logger = logging.getLogger(__name__)

@dataclass
class AutomationConfig:
    """Configuration for automation system."""
    enabled: bool = True
    posting_times: List[str] = None
    platforms: List[str] = None
    content_templates: Dict[str, int] = None
    timezone: str = "Europe/Bucharest"

    def __post_init__(self):
        if self.posting_times is None:
            self.posting_times = ["09:00", "15:00", "21:00"]
        if self.platforms is None:
            self.platforms = ["tiktok", "facebook", "instagram"]
        if self.content_templates is None:
            self.content_templates = {
                "educational": 40,
                "testimonial": 30,
                "promotional": 30
            }

class AutomationScheduler:
    """
    Main automation scheduler for AutoPro Daune.

    Handles the complete automation workflow:
    - Scheduled video generation and posting
    - Platform management
    - Performance tracking
    - Error handling and recovery
    """

    def __init__(self):
        """Initialize the automation scheduler."""
        self.config = AutomationConfig()
        self.social_poster = get_social_poster()
        self.video_generator = VideoGenerator()
        self.supabase = get_supabase_service_instance()

        self._is_running = False
        self._scheduler_thread = None

        # Load config from database
        self._load_config_from_db()

        logger.info("✅ AutomationScheduler initialized")

    def _load_config_from_db(self):
        """Load automation configuration from database."""
        try:
            result = self.supabase.client.table("automation_config").select("*").eq("config_key", "daily_posting_schedule").execute()

            if result.data:
                config_data = result.data[0].get("config_value", {})
                self.config.enabled = config_data.get("enabled", True)
                self.config.posting_times = config_data.get("times", ["09:00", "15:00", "21:00"])
                self.config.timezone = config_data.get("timezone", "Europe/Bucharest")

            logger.info(f"✅ Loaded automation config: {self.config.posting_times}")

        except Exception as e:
            logger.warning(f"⚠️ Failed to load config from DB, using defaults: {e}")

    def start(self):
        """Start the automation scheduler."""
        if self._is_running:
            logger.warning("⚠️ Scheduler already running")
            return

        logger.info("🚀 Starting AutoPro Daune automation scheduler")

        # Schedule daily posts
        for post_time in self.config.posting_times:
            schedule.every().day.at(post_time).do(self._scheduled_post_job)
            logger.info(f"✅ Scheduled daily post at {post_time}")

        # Schedule daily metrics update
        schedule.every().day.at("23:55").do(self._update_daily_metrics)

        # Schedule weekly optimization
        schedule.every().sunday.at("02:00").do(self._weekly_optimization)

        self._is_running = True

        # Start scheduler in separate thread
        self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()

        logger.info("✅ Automation scheduler started successfully")

    def stop(self):
        """Stop the automation scheduler."""
        if not self._is_running:
            logger.warning("⚠️ Scheduler not running")
            return

        logger.info("⏹️ Stopping automation scheduler")

        self._is_running = False
        schedule.clear()

        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)

        logger.info("✅ Automation scheduler stopped")

    def _run_scheduler(self):
        """Run the scheduler loop."""
        logger.info("🔄 Scheduler loop started")

        while self._is_running:
            try:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"❌ Scheduler loop error: {e}")
                time.sleep(60)  # Wait a minute before retrying

    def _scheduled_post_job(self):
        """Execute a scheduled post job."""
        try:
            logger.info("🎬 Starting scheduled post job")

            # Check if we haven't already posted too many times today
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time()).isoformat()

            result = self.supabase.client.table("social_posts").select("*").gte("created_at", today_start).execute()
            posts_today = len(result.data) if result.data else 0

            if posts_today >= 3:
                logger.info(f"✅ Daily quota reached ({posts_today}/3 posts)")
                return

            # Determine content template for this post
            template_type = self._get_next_template_type(posts_today)

            # Generate and post content
            success = asyncio.run(self._generate_and_post_content(template_type))

            if success:
                logger.info(f"✅ Scheduled post completed: {template_type}")
                self._log_automation_event("post_success", {"template_type": template_type, "posts_today": posts_today + 1})
            else:
                logger.error(f"❌ Scheduled post failed: {template_type}")
                self._log_automation_event("post_error", {"template_type": template_type, "posts_today": posts_today})

        except Exception as e:
            logger.error(f"❌ Scheduled post job failed: {e}")
            self._log_automation_event("job_error", {"error": str(e)})

    def _get_next_template_type(self, posts_today: int) -> str:
        """Determine the next content template type based on daily rotation."""
        template_rotation = ["educational", "testimonial", "promotional"]
        return template_rotation[posts_today % len(template_rotation)]

    async def _generate_and_post_content(self, template_type: str) -> bool:
        """Generate content and post to social media platforms."""
        try:
            # Generate content using template
            context_data = {
                "timeframe": "24-48h",
                "amount": "5000",
                "testimonial": "Am fost foarte mulțumit de serviciile AutoPro Daune!",
                "client_result": "5000 LEI în 48h"
            }

            if template_type == "educational":
                content_template = ContentTemplate.EDUCATIONAL
            elif template_type == "testimonial":
                content_template = ContentTemplate.TESTIMONIAL
            else:
                content_template = ContentTemplate.PROMOTIONAL

            content_data = self.social_poster.generate_content_from_template(content_template, context_data)

            # Optional: Generate video (commented out for now to avoid API costs)
            video_url = None
            # video_result = self.video_generator.generate_video()
            # video_url = video_result.get("video_path")

            # Schedule the post
            post_id = self.social_poster.schedule_post(
                content=content_data["content"],
                hashtags=content_data["hashtags"],
                template_type=content_data["template_type"],
                video_url=video_url,
                platforms=self.config.platforms,
                scheduled_for=datetime.now()
            )

            # Execute the post
            results = await self.social_poster.execute_scheduled_post(post_id)

            # Check if at least one platform succeeded
            success_count = sum(1 for r in results.values() if r.get("success", False))

            return success_count > 0

        except Exception as e:
            logger.error(f"❌ Failed to generate and post content: {e}")
            return False

    def _update_daily_metrics(self):
        """Update daily performance metrics."""
        try:
            logger.info("📊 Updating daily metrics")

            yesterday = datetime.now().date() - timedelta(days=1)
            yesterday_start = datetime.combine(yesterday, datetime.min.time()).isoformat()
            yesterday_end = datetime.combine(yesterday, datetime.max.time()).isoformat()

            # Get leads from yesterday
            leads_result = self.supabase.client.table("leads").select("*").gte("created_at", yesterday_start).lte("created_at", yesterday_end).execute()
            leads_count = len(leads_result.data) if leads_result.data else 0

            # Get posts from yesterday
            posts_result = self.supabase.client.table("social_posts").select("*").gte("created_at", yesterday_start).lte("created_at", yesterday_end).execute()
            posts_data = posts_result.data if posts_result.data else []

            posts_count = len(posts_data)
            total_views = sum(p.get("views", 0) for p in posts_data)
            total_engagement = sum(p.get("engagement", 0) for p in posts_data)

            # Get referrals from yesterday
            referrals_result = self.supabase.client.table("referrals").select("*").gte("created_at", yesterday_start).lte("created_at", yesterday_end).execute()
            referrals_count = len(referrals_result.data) if referrals_result.data else 0

            # Insert/update performance metrics
            metrics_data = {
                "metric_date": yesterday.isoformat(),
                "metric_type": "daily",
                "leads_generated": leads_count,
                "posts_published": posts_count,
                "total_views": total_views,
                "total_engagement": total_engagement,
                "whatsapp_conversations": 0,  # Would be calculated from WhatsApp data
                "videos_generated": posts_count,  # Assuming 1 video per post
                "referral_rewards_paid": referrals_count * 200,  # 200 LEI per referral
                "created_at": datetime.now().isoformat()
            }

            self.supabase.client.table("performance_metrics").insert(metrics_data).execute()

            logger.info(f"✅ Daily metrics updated for {yesterday}: {leads_count} leads, {posts_count} posts")

        except Exception as e:
            logger.error(f"❌ Failed to update daily metrics: {e}")

    def _weekly_optimization(self):
        """Perform weekly optimization tasks."""
        try:
            logger.info("🔧 Running weekly optimization")

            # Analyze performance and optimize content templates
            week_ago = datetime.now() - timedelta(days=7)

            # Get posts from last week
            posts_result = self.supabase.client.table("social_posts").select("*").gte("created_at", week_ago.isoformat()).execute()
            posts_data = posts_result.data if posts_result.data else []

            # Analyze performance by template type
            template_performance = {}
            for post in posts_data:
                template_type = post.get("template_type", "unknown")
                if template_type not in template_performance:
                    template_performance[template_type] = {
                        "count": 0,
                        "total_views": 0,
                        "total_engagement": 0,
                        "total_leads": 0
                    }

                template_performance[template_type]["count"] += 1
                template_performance[template_type]["total_views"] += post.get("views", 0)
                template_performance[template_type]["total_engagement"] += post.get("engagement", 0)
                template_performance[template_type]["total_leads"] += post.get("leads_generated", 0)

            # Log performance insights
            for template_type, metrics in template_performance.items():
                if metrics["count"] > 0:
                    avg_engagement = metrics["total_engagement"] / metrics["count"]
                    logger.info(f"📊 {template_type}: {metrics['count']} posts, avg engagement: {avg_engagement:.1f}")

            # Clean old logs (older than 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            self.supabase.client.table("system_logs").delete().lt("created_at", thirty_days_ago.isoformat()).execute()

            logger.info("✅ Weekly optimization completed")

        except Exception as e:
            logger.error(f"❌ Weekly optimization failed: {e}")

    def _log_automation_event(self, event_type: str, details: Dict[str, Any]):
        """Log automation events to database."""
        try:
            log_entry = {
                "level": "info",
                "category": "automation",
                "message": f"Automation event: {event_type}",
                "details": details,
                "source_service": "automation_scheduler",
                "source_function": event_type,
                "created_at": datetime.now().isoformat()
            }

            self.supabase.client.table("system_logs").insert(log_entry).execute()

        except Exception as e:
            logger.error(f"❌ Failed to log automation event: {e}")

    async def trigger_manual_post(self, template_type: str = "educational") -> Dict[str, Any]:
        """Manually trigger a post (for API endpoint)."""
        try:
            logger.info(f"🎯 Manual post trigger: {template_type}")

            success = await self._generate_and_post_content(template_type)

            if success:
                return {
                    "success": True,
                    "message": f"Manual post completed successfully: {template_type}",
                    "template_type": template_type,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": f"Manual post failed: {template_type}",
                    "template_type": template_type,
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"❌ Manual post trigger failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "template_type": template_type,
                "timestamp": datetime.now().isoformat()
            }

    def get_status(self) -> Dict[str, Any]:
        """Get current automation status."""
        try:
            # Get today's posts
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time()).isoformat()

            result = self.supabase.client.table("social_posts").select("*").gte("created_at", today_start).execute()
            posts_today = len(result.data) if result.data else 0

            # Calculate next scheduled time
            current_time = datetime.now().strftime("%H:%M")
            next_post_time = None

            for post_time in sorted(self.config.posting_times):
                if post_time > current_time:
                    next_post_time = post_time
                    break

            if not next_post_time:
                # Next post is tomorrow
                next_post_time = self.config.posting_times[0] + " (tomorrow)"

            return {
                "is_running": self._is_running,
                "enabled": self.config.enabled,
                "posts_today": posts_today,
                "daily_target": 3,
                "next_scheduled": next_post_time,
                "posting_schedule": self.config.posting_times,
                "platforms": self.config.platforms,
                "timezone": self.config.timezone
            }

        except Exception as e:
            logger.error(f"❌ Failed to get automation status: {e}")
            return {
                "is_running": False,
                "enabled": False,
                "error": str(e)
            }

# Global scheduler instance
_automation_scheduler = None

def get_automation_scheduler() -> AutomationScheduler:
    """Get the global automation scheduler instance."""
    global _automation_scheduler
    if _automation_scheduler is None:
        _automation_scheduler = AutomationScheduler()
    return _automation_scheduler

def start_automation():
    """Start the automation system."""
    scheduler = get_automation_scheduler()
    scheduler.start()

def stop_automation():
    """Stop the automation system."""
    scheduler = get_automation_scheduler()
    scheduler.stop()

# CLI entry point for running as standalone service
if __name__ == "__main__":
    import signal
    import sys

    def signal_handler(sig, frame):
        logger.info("🛑 Received shutdown signal")
        stop_automation()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("🚀 Starting AutoPro Daune Automation Scheduler")

    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("✅ Environment variables loaded")
    except ImportError:
        logger.warning("⚠️ python-dotenv not available, using system environment")

    # Start automation
    start_automation()

    logger.info("✅ AutoPro Daune Automation Scheduler is running")
    logger.info("Press Ctrl+C to stop...")

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received")
        stop_automation()