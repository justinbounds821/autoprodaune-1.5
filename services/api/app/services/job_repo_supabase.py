# services/api/app/services/job_repo_supabase.py
"""
Supabase repository for video job persistence.
SRP: Database operations only, no business logic.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SupabaseJobRepo:
    """Repository for video job persistence in Supabase."""

    def __init__(self):
        """Initialize Supabase connection."""
        try:
            from supabase import create_client, Client
            url = os.getenv("SUPABASE_URL", "")
            key = os.getenv("SUPABASE_SERVICE_KEY", "")

            if not url or not key:
                logger.warning("Supabase credentials not configured, using in-memory fallback")
                self.client = None
                self.enabled = False
                return

            self.client: Client = create_client(url, key)
            self.enabled = True
            logger.info("✅ Supabase job repository initialized")

        except ImportError:
            logger.warning("Supabase client not available, using in-memory fallback")
            self.client = None
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.client = None
            self.enabled = False

    def save_job(self, job_id: str, job_data: Dict[str, Any]) -> bool:
        """
        Save or update job in Supabase.

        Args:
            job_id: Job identifier
            job_data: Job data dictionary

        Returns:
            True if saved successfully, False otherwise
        """
        if not self.enabled or not self.client:
            logger.debug(f"Supabase disabled, would save job {job_id}")
            return False

        try:
            # Prepare data for Supabase
            data = {
                "job_id": job_id,
                "status": job_data.get("status", "queued"),
                "script": job_data.get("script", ""),
                "voice_id": job_data.get("voice_id"),
                "avatar_image_url": job_data.get("avatar_image_url"),
                "avatar_video_url": job_data.get("avatar_video_url"),
                "timeline": json.dumps(job_data.get("timeline", {})),
                "result_url": job_data.get("result_url"),
                "provider": job_data.get("provider", "internal"),
                "error": job_data.get("error"),
                "updated_at": datetime.utcnow().isoformat()
            }

            # Upsert job
            result = self.client.table("video_jobs").upsert(data).execute()

            if result.data:
                logger.info(f"✅ Saved job {job_id} to Supabase")
                return True
            else:
                logger.error(f"Failed to save job {job_id} to Supabase")
                return False

        except Exception as e:
            logger.error(f"Error saving job {job_id} to Supabase: {e}")
            return False

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job from Supabase.

        Args:
            job_id: Job identifier

        Returns:
            Job data dictionary or None if not found
        """
        if not self.enabled or not self.client:
            logger.debug(f"Supabase disabled, would get job {job_id}")
            return None

        try:
            result = self.client.table("video_jobs").select("*").eq("job_id", job_id).execute()

            if result.data and len(result.data) > 0:
                job = result.data[0]
                # Parse JSON fields
                if job.get("timeline"):
                    try:
                        job["timeline"] = json.loads(job["timeline"])
                    except:
                        job["timeline"] = {}

                logger.debug(f"Retrieved job {job_id} from Supabase")
                return job
            else:
                logger.debug(f"Job {job_id} not found in Supabase")
                return None

        except Exception as e:
            logger.error(f"Error getting job {job_id} from Supabase: {e}")
            return None

    def update_job_status(self, job_id: str, status: str, **kwargs) -> bool:
        """
        Update job status in Supabase.

        Args:
            job_id: Job identifier
            status: New status
            **kwargs: Additional fields to update

        Returns:
            True if updated successfully, False otherwise
        """
        if not self.enabled or not self.client:
            logger.debug(f"Supabase disabled, would update job {job_id} status to {status}")
            return False

        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat(),
                **kwargs
            }

            result = self.client.table("video_jobs").update(update_data).eq("job_id", job_id).execute()

            if result.data:
                logger.info(f"✅ Updated job {job_id} status to {status} in Supabase")
                return True
            else:
                logger.error(f"Failed to update job {job_id} status in Supabase")
                return False

        except Exception as e:
            logger.error(f"Error updating job {job_id} status in Supabase: {e}")
            return False

    def save_cost(self, job_id: str, cost_data: Dict[str, Any]) -> bool:
        """
        Save cost data for a job.

        Args:
            job_id: Job identifier
            cost_data: Cost data dictionary

        Returns:
            True if saved successfully, False otherwise
        """
        if not self.enabled or not self.client:
            logger.debug(f"Supabase disabled, would save cost for job {job_id}")
            return False

        try:
            data = {
                "job_id": job_id,
                "tts_seconds": cost_data.get("tts_seconds", 0),
                "processing_seconds": cost_data.get("processing_seconds", 0),
                "storage_mb": cost_data.get("storage_mb", 0),
                "amount_cents": cost_data.get("amount_cents", 0)
            }

            result = self.client.table("video_costs").insert(data).execute()

            if result.data:
                logger.info(f"✅ Saved cost data for job {job_id} to Supabase")
                return True
            else:
                logger.error(f"Failed to save cost data for job {job_id} to Supabase")
                return False

        except Exception as e:
            logger.error(f"Error saving cost data for job {job_id} to Supabase: {e}")
            return False

    def save_assets(self, job_id: str, assets: list) -> bool:
        """
        Save video assets for a job.

        Args:
            job_id: Job identifier
            assets: List of asset dictionaries

        Returns:
            True if saved successfully, False otherwise
        """
        if not self.enabled or not self.client:
            logger.debug(f"Supabase disabled, would save assets for job {job_id}")
            return False

        try:
            assets_data = []
            for asset in assets:
                assets_data.append({
                    "job_id": job_id,
                    "kind": asset.get("kind", "unknown"),
                    "url": asset.get("url", ""),
                    "meta": json.dumps(asset.get("meta", {}))
                })

            if assets_data:
                result = self.client.table("video_assets").insert(assets_data).execute()

                if result.data:
                    logger.info(f"✅ Saved {len(assets_data)} assets for job {job_id} to Supabase")
                    return True
                else:
                    logger.error(f"Failed to save assets for job {job_id} to Supabase")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error saving assets for job {job_id} to Supabase: {e}")
            return False

    def save_webhook(self, job_id: str, webhook_url: str) -> bool:
        """
        Save webhook configuration for a job.

        Args:
            job_id: Job identifier
            webhook_url: Webhook URL

        Returns:
            True if saved successfully, False otherwise
        """
        if not self.enabled or not self.client:
            logger.debug(f"Supabase disabled, would save webhook for job {job_id}")
            return False

        try:
            data = {
                "job_id": job_id,
                "url": webhook_url,
                "delivered": False,
                "last_error": None
            }

            result = self.client.table("video_webhooks").insert(data).execute()

            if result.data:
                logger.info(f"✅ Saved webhook for job {job_id} to Supabase")
                return True
            else:
                logger.error(f"Failed to save webhook for job {job_id} to Supabase")
                return False

        except Exception as e:
            logger.error(f"Error saving webhook for job {job_id} to Supabase: {e}")
            return False

    def mark_webhook_delivered(self, job_id: str, success: bool, error: str = None) -> bool:
        """
        Mark webhook as delivered.

        Args:
            job_id: Job identifier
            success: Whether delivery was successful
            error: Error message if delivery failed

        Returns:
            True if updated successfully, False otherwise
        """
        if not self.enabled or not self.client:
            logger.debug(f"Supabase disabled, would mark webhook delivered for job {job_id}")
            return False

        try:
            update_data = {
                "delivered": success,
                "updated_at": datetime.utcnow().isoformat()
            }

            if not success and error:
                update_data["last_error"] = error

            result = self.client.table("video_webhooks").update(update_data).eq("job_id", job_id).execute()

            if result.data:
                logger.info(f"✅ Marked webhook as {'delivered' if success else 'failed'} for job {job_id}")
                return True
            else:
                logger.error(f"Failed to mark webhook for job {job_id}")
                return False

        except Exception as e:
            logger.error(f"Error marking webhook for job {job_id} in Supabase: {e}")
            return False

# Global instance
_job_repo = None

def get_job_repo() -> SupabaseJobRepo:
    """Get or create global job repository instance."""
    global _job_repo
    if _job_repo is None:
        _job_repo = SupabaseJobRepo()
    return _job_repo