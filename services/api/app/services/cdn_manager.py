"""
CDN Manager Service - Manage CDN caching and delivery
Single Responsibility: Handle CDN integration, cache purging, URL signing
Safe-by-default: Disabled unless ENABLE_CDN_CACHE=true
"""
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import hashlib
import hmac

logger = logging.getLogger(__name__)


class CDNManagerService:
    """
    Manage CDN integration for video delivery.
    Supports Cloudflare R2, cache purging, signed URLs.
    """
    
    def __init__(self):
        self.enabled = os.getenv("ENABLE_CDN_CACHE", "false").lower() == "true"
        self.cdn_provider = os.getenv("CDN_PROVIDER", "cloudflare_r2")
        self.cdn_domain = os.getenv("CDN_DOMAIN", "")
        self.cdn_zone_id = os.getenv("CDN_ZONE_ID", "")
        self.cdn_api_token = os.getenv("CDN_API_TOKEN", "")
        self.url_signing_secret = os.getenv("CDN_URL_SIGNING_SECRET", "")
        self.default_ttl = int(os.getenv("CDN_DEFAULT_TTL", "3600"))  # 1 hour
        
        if not self.enabled:
            logger.info("⚠️ CDN caching disabled (ENABLE_CDN_CACHE=false)")
            return
        
        if not self.cdn_domain:
            logger.warning("⚠️ CDN_DOMAIN not set, CDN features limited")
            self.enabled = False
        else:
            logger.info(f"✅ CDN manager enabled (provider={self.cdn_provider})")
    
    async def get_cdn_url(
        self, 
        job_id: str, 
        signed: bool = False,
        ttl_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate CDN URL for job output.
        Optionally sign URL for expiring access.
        """
        if not self.enabled:
            return {"cdn_url": None, "is_signed": False}
        
        # Build base CDN URL
        cdn_url = f"https://{self.cdn_domain}/videos/{job_id}/output.mp4"
        
        if signed and self.url_signing_secret:
            ttl = ttl_seconds or self.default_ttl
            cdn_url = self._sign_url(cdn_url, ttl)
            is_signed = True
        else:
            is_signed = False
        
        return {
            "job_id": job_id,
            "cdn_url": cdn_url,
            "is_signed": is_signed,
            "ttl_seconds": ttl_seconds if signed else None,
            "expires_at": (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat() if signed and ttl_seconds else None
        }
    
    def _sign_url(self, url: str, ttl_seconds: int) -> str:
        """Generate signed URL with expiration"""
        expires = int((datetime.utcnow() + timedelta(seconds=ttl_seconds)).timestamp())
        
        # Create signature
        message = f"{url}{expires}".encode()
        signature = hmac.new(
            self.url_signing_secret.encode(),
            message,
            hashlib.sha256
        ).hexdigest()
        
        # Append signature and expiration
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}expires={expires}&signature={signature}"
    
    async def purge_cache(self, job_id: str) -> Dict[str, Any]:
        """
        Purge CDN cache for specific job.
        Forces CDN to fetch fresh content.
        """
        if not self.enabled:
            return {"purged": False, "reason": "cdn_disabled"}
        
        try:
            if self.cdn_provider == "cloudflare_r2":
                return await self._purge_cloudflare(job_id)
            else:
                logger.warning(f"Unsupported CDN provider: {self.cdn_provider}")
                return {"purged": False, "reason": "unsupported_provider"}
        
        except Exception as e:
            logger.error(f"Cache purge failed for {job_id}: {e}")
            return {"purged": False, "error": str(e)}
    
    async def _purge_cloudflare(self, job_id: str) -> Dict[str, Any]:
        """Purge Cloudflare CDN cache"""
        if not self.cdn_api_token or not self.cdn_zone_id:
            return {"purged": False, "reason": "missing_credentials"}
        
        try:
            import httpx
            
            url = f"https://api.cloudflare.com/client/v4/zones/{self.cdn_zone_id}/purge_cache"
            headers = {
                "Authorization": f"Bearer {self.cdn_api_token}",
                "Content-Type": "application/json"
            }
            
            # Purge specific files for this job
            files_to_purge = [
                f"https://{self.cdn_domain}/videos/{job_id}/output.mp4",
                f"https://{self.cdn_domain}/videos/{job_id}/thumbnail.jpg"
            ]
            
            payload = {"files": files_to_purge}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                
                # Log purge to database
                try:
                    from ..services.supabase_client import get_supabase
                    supabase = get_supabase()
                    
                    supabase.table("cdn_purge_history").insert({
                        "job_id": job_id,
                        "purged_urls": files_to_purge,
                        "purged_by": "system"
                    }).execute()
                except Exception as log_error:
                    logger.error(f"Failed to log CDN purge: {log_error}")
                
                return {
                    "purged": result.get("success", False),
                    "purged_objects": len(files_to_purge),
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Cloudflare purge failed: {e}")
            return {"purged": False, "error": str(e)}
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get CDN cache statistics"""
        if not self.enabled:
            return {"enabled": False}
        
        # Get purge history from database
        try:
            from ..services.supabase_client import get_supabase
            supabase = get_supabase()
            
            # Count total purges
            response = supabase.table("cdn_purge_history").select("*", count="exact").execute()
            total_purges = response.count if response.count else 0
            
            # Get recent purges
            recent = supabase.table("cdn_purge_history").select("*").order("purged_at", desc=True).limit(10).execute()
            
            return {
                "enabled": True,
                "provider": self.cdn_provider,
                "total_purges": total_purges,
                "recent_purges": recent.data or [],
                "note": "For detailed CDN stats, check your CDN provider dashboard"
            }
        except Exception as e:
            logger.error(f"Failed to get CDN stats: {e}")
            return {
                "enabled": True,
                "provider": self.cdn_provider,
                "error": str(e)
            }
    
    def get_health(self) -> Dict[str, Any]:
        """Health check for CDN manager"""
        return {
            "enabled": self.enabled,
            "provider": self.cdn_provider,
            "domain_configured": bool(self.cdn_domain),
            "signing_enabled": bool(self.url_signing_secret),
            "default_ttl": self.default_ttl
        }


# Singleton instance
_instance = None

def get_cdn_manager() -> CDNManagerService:
    """Get or create CDNManagerService singleton"""
    global _instance
    if _instance is None:
        _instance = CDNManagerService()
    return _instance
