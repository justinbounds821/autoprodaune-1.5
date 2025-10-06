"""
Video Webhooks Router - Webhook management and logs
Provides endpoints for webhook configuration and delivery logs
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from ..services.webhook_notifier import get_webhook_notifier

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/video/webhooks", tags=["Video Webhooks"])


@router.get("")
async def list_webhooks(
    job_id: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100)
):
    """Get webhook delivery logs"""
    try:
        webhook_service = get_webhook_notifier()
        
        logs = await webhook_service.get_webhook_logs(job_id=job_id, limit=limit)
        
        return {
            "webhooks": logs,
            "total": len(logs),
            "job_id": job_id
        }
    
    except Exception as e:
        logger.error(f"Error listing webhooks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list webhooks: {str(e)}")


@router.get("/{log_id}")
async def get_webhook_log(log_id: str):
    """Get specific webhook log details"""
    try:
        from ..services.supabase_client import get_supabase
        supabase = get_supabase()
        
        response = supabase.table("webhook_logs").select("*").eq("id", log_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Webhook log {log_id} not found")
        
        return response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting webhook log {log_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get webhook log: {str(e)}")


@router.post("/test")
async def test_webhook(url: str, event: str = "test.webhook"):
    """Test webhook delivery to a URL"""
    try:
        webhook_service = get_webhook_notifier()
        
        if not webhook_service.enabled:
            raise HTTPException(status_code=503, detail="Webhooks not enabled")
        
        # Send test webhook
        result = await webhook_service._send_webhook(
            url=url,
            payload={
                "event": event,
                "job_id": "test",
                "timestamp": "2025-10-06T00:00:00Z",
                "data": {"message": "This is a test webhook"}
            }
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test webhook: {str(e)}")


@router.get("/stats/summary")
async def get_webhook_stats():
    """Get webhook delivery statistics"""
    try:
        from ..services.supabase_client import get_supabase
        supabase = get_supabase()
        
        # Count total webhooks
        total_response = supabase.table("webhook_logs").select("*", count="exact").execute()
        total = total_response.count if total_response.count else 0
        
        # Count delivered
        delivered_response = supabase.table("webhook_logs").select("*", count="exact").eq("delivered", True).execute()
        delivered = delivered_response.count if delivered_response.count else 0
        
        # Count failed
        failed_response = supabase.table("webhook_logs").select("*", count="exact").eq("delivered", False).execute()
        failed = failed_response.count if failed_response.count else 0
        
        # Get recent failures
        recent_failures = supabase.table("webhook_logs").select("*").eq("delivered", False).order("sent_at", desc=True).limit(5).execute()
        
        return {
            "total_webhooks": total,
            "delivered": delivered,
            "failed": failed,
            "success_rate": (delivered / total * 100) if total > 0 else 0,
            "recent_failures": recent_failures.data or []
        }
    
    except Exception as e:
        logger.error(f"Error getting webhook stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
