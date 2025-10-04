# services/api/app/services/webhook_notifier.py
"""
Webhook notification service for job completion.
SRP: Webhook sending only, no business logic.
"""
import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

class WebhookNotifier:
    """Service for sending webhook notifications."""

    def __init__(self):
        """Initialize webhook notifier."""
        self.webhook_url = os.getenv("WEBHOOK_COMPLETED_URL")
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self.timeout = 10  # seconds

        if self.webhook_url:
            logger.info(f"✅ Webhook notifier initialized: {self.webhook_url}")
        else:
            logger.info("Webhook notifier disabled (no WEBHOOK_COMPLETED_URL)")

    async def send_webhook(self, job_id: str, status: str, video_url: str = None,
                          error: str = None, metadata: Dict[str, Any] = None) -> bool:
        """
        Send webhook notification for job completion.

        Args:
            job_id: Job identifier
            status: Job status
            video_url: URL to generated video
            error: Error message if job failed
            metadata: Additional metadata

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.webhook_url:
            logger.debug(f"Webhook disabled, would notify job {job_id} status: {status}")
            return False

        payload = {
            "job_id": job_id,
            "status": status,
            "timestamp": asyncio.get_event_loop().time(),
            "provider": "internal"
        }

        if video_url:
            payload["video_url"] = video_url
        if error:
            payload["error"] = error
        if metadata:
            payload["metadata"] = metadata

        # Retry logic
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Sending webhook for job {job_id} (attempt {attempt + 1})")

                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        self.webhook_url,
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    )

                    if response.status_code < 400:
                        logger.info(f"✅ Webhook sent successfully for job {job_id}")
                        await self._mark_webhook_delivered(job_id, True)
                        return True
                    else:
                        logger.warning(f"Webhook failed with status {response.status_code}: {response.text}")

                # Wait before retry (exponential backoff)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))

            except httpx.TimeoutException:
                logger.warning(f"Webhook timeout for job {job_id} (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Webhook error for job {job_id}: {e}")

        # All retries failed
        logger.error(f"Failed to send webhook for job {job_id} after {self.max_retries} attempts")
        await self._mark_webhook_delivered(job_id, False, str(e))
        return False

    async def _mark_webhook_delivered(self, job_id: str, success: bool, error: str = None) -> None:
        """Mark webhook as delivered in Supabase."""
        try:
            from .job_repo_supabase import get_job_repo

            repo = get_job_repo()
            repo.mark_webhook_delivered(job_id, success, error)

        except Exception as e:
            logger.error(f"Failed to mark webhook delivery for job {job_id}: {e}")

    def is_enabled(self) -> bool:
        """Check if webhook notifications are enabled."""
        return bool(self.webhook_url)

    def get_config(self) -> Dict[str, Any]:
        """Get webhook configuration."""
        return {
            "enabled": self.is_enabled(),
            "url": self.webhook_url,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "timeout": self.timeout
        }

# Global instance
_webhook_notifier = None

def get_webhook_notifier() -> WebhookNotifier:
    """Get or create global webhook notifier instance."""
    global _webhook_notifier
    if _webhook_notifier is None:
        _webhook_notifier = WebhookNotifier()
    return _webhook_notifier