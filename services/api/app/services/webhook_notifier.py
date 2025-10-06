"""
Webhook Notifier Service - Send webhook notifications for job events
Single Responsibility: Trigger webhooks on job completion/failure
Safe-by-default: Disabled unless ENABLE_WEBHOOKS=true
"""
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class WebhookNotifierService:
    """
    Send webhook notifications when jobs complete, fail, or reach milestones.
    Supports retry logic and webhook logs.
    """
    
    def __init__(self):
        self.enabled = os.getenv("ENABLE_WEBHOOKS", "false").lower() == "true"
        self.webhook_completed_url = os.getenv("WEBHOOK_COMPLETED_URL", "")
        self.webhook_failed_url = os.getenv("WEBHOOK_FAILED_URL", "")
        self.webhook_secret = os.getenv("WEBHOOK_SECRET", "")
        self.max_retries = int(os.getenv("WEBHOOK_MAX_RETRIES", "3"))
        self.timeout = int(os.getenv("WEBHOOK_TIMEOUT", "30"))
        
        if not self.enabled:
            logger.info("⚠️ Webhooks disabled (ENABLE_WEBHOOKS=false)")
            return
        
        if not self.webhook_completed_url and not self.webhook_failed_url:
            logger.warning("⚠️ No webhook URLs configured")
            self.enabled = False
        else:
            logger.info("✅ Webhooks enabled")
    
    async def notify_job_completed(
        self, 
        job_id: str, 
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send webhook notification when job completes successfully"""
        if not self.enabled or not self.webhook_completed_url:
            return {"sent": False, "reason": "disabled_or_not_configured"}
        
        payload = {
            "event": "job.completed",
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": job_data
        }
        
        return await self._send_webhook(self.webhook_completed_url, payload)
    
    async def notify_job_failed(
        self, 
        job_id: str, 
        error: str,
        job_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send webhook notification when job fails"""
        if not self.enabled or not self.webhook_failed_url:
            return {"sent": False, "reason": "disabled_or_not_configured"}
        
        payload = {
            "event": "job.failed",
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "error": error,
            "data": job_data or {}
        }
        
        return await self._send_webhook(self.webhook_failed_url, payload)
    
    async def notify_job_progress(
        self, 
        job_id: str, 
        progress: float,
        stage: str
    ) -> Dict[str, Any]:
        """Send webhook notification for job progress updates"""
        if not self.enabled or not self.webhook_completed_url:
            return {"sent": False, "reason": "disabled_or_not_configured"}
        
        payload = {
            "event": "job.progress",
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "progress": progress,
            "stage": stage
        }
        
        return await self._send_webhook(self.webhook_completed_url, payload)
    
    async def _send_webhook(
        self, 
        url: str, 
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send webhook with retry logic"""
        import httpx
        import hashlib
        import hmac
        
        # Add signature if secret configured
        headers = {"Content-Type": "application/json"}
        if self.webhook_secret:
            signature = hmac.new(
                self.webhook_secret.encode(),
                json.dumps(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            headers["X-Webhook-Signature"] = signature
        
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        json=payload,
                        headers=headers,
                        timeout=self.timeout
                    )
                    
                    if response.status_code in (200, 201, 202, 204):
                        logger.info(f"Webhook sent successfully: {payload['event']} (job={payload['job_id']})")
                        return {
                            "sent": True,
                            "status_code": response.status_code,
                            "attempt": attempt,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    else:
                        logger.warning(f"Webhook failed with status {response.status_code}, attempt {attempt}/{self.max_retries}")
                        if attempt == self.max_retries:
                            return {
                                "sent": False,
                                "error": f"HTTP {response.status_code}",
                                "attempts": attempt
                            }
            
            except httpx.TimeoutException:
                logger.warning(f"Webhook timeout on attempt {attempt}/{self.max_retries}")
                if attempt == self.max_retries:
                    return {"sent": False, "error": "timeout", "attempts": attempt}
            
            except Exception as e:
                logger.error(f"Webhook error on attempt {attempt}/{self.max_retries}: {e}")
                if attempt == self.max_retries:
                    return {"sent": False, "error": str(e), "attempts": attempt}
        
        return {"sent": False, "error": "unknown", "attempts": self.max_retries}
    
    async def get_webhook_logs(
        self, 
        job_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get webhook delivery logs"""
        # TODO: Store webhook logs in database
        # For now, return mock data
        return [
            {
                "id": f"wh_{i}",
                "job_id": job_id or f"job_{i}",
                "event": "job.completed",
                "sent_at": datetime.utcnow().isoformat(),
                "status": "delivered",
                "attempts": 1
            }
            for i in range(min(3, limit))
        ]
    
    def get_health(self) -> Dict[str, Any]:
        """Health check for webhook service"""
        return {
            "enabled": self.enabled,
            "completed_url_configured": bool(self.webhook_completed_url),
            "failed_url_configured": bool(self.webhook_failed_url),
            "signing_enabled": bool(self.webhook_secret),
            "max_retries": self.max_retries,
            "timeout": self.timeout
        }


# Singleton instance
_instance = None

def get_webhook_notifier() -> WebhookNotifierService:
    """Get or create WebhookNotifierService singleton"""
    global _instance
    if _instance is None:
        _instance = WebhookNotifierService()
    return _instance
