import os
import logging
import requests
from typing import Dict, Optional, Any
from datetime import datetime
from ..oauth_manager import get_oauth_manager
from ..social_media_config import SocialPlatform

logger = logging.getLogger(__name__)

class InstagramAPIClient:
    """
    Client pentru Instagram (Graph).
    Ține doar detalii de auth + URL-uri + headers.
    """

    def __init__(self):
        self.oauth_manager = get_oauth_manager()
        # lasăm endpoint-urile parametrizabile, dar păstrăm fallback compatibil cu codul tău
        self.api_base_url = os.getenv("INSTAGRAM_API_BASE", "https://graph.instagram.com")
        self.media_upload_url = f"{self.api_base_url}/me/media"
        self.media_publish_url = f"{self.api_base_url}/me/media_publish"
        self.container_status_url = f"{self.api_base_url}/{{container_id}}"
        self.media_info_url = f"{self.api_base_url}/{{media_id}}"

    def is_authenticated(self) -> bool:
        return self.oauth_manager.is_token_valid(SocialPlatform.INSTAGRAM)

    def get_access_token(self) -> Optional[str]:
        return self.oauth_manager.get_valid_access_token(SocialPlatform.INSTAGRAM)

    def headers_json(self, access_token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
    
    def get_follower_count(self) -> Dict[str, Any]:
        """
        Get follower count and account metrics from Instagram Business Account.
        
        Returns:
            Dictionary with follower_count, follows_count, media_count, etc.
        """
        try:
            access_token = self.get_access_token()
            
            if not access_token:
                raise RuntimeError("No Instagram access token available")
            
            # Instagram Graph API endpoint for user insights
            # First, get the Instagram Business Account ID
            ig_user_url = f"{self.api_base_url}/me"
            params = {
                "fields": "id,username,followers_count,follows_count,media_count,name",
                "access_token": access_token
            }
            
            response = requests.get(ig_user_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            metrics = {
                "platform": "instagram",
                "follower_count": data.get("followers_count", 0),
                "following_count": data.get("follows_count", 0),
                "media_count": data.get("media_count", 0),
                "username": data.get("username", "Unknown"),
                "name": data.get("name", ""),
                "account_id": data.get("id", ""),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"[Instagram] @{metrics['username']} - Followers: {metrics['follower_count']:,}")
            return metrics
            
        except Exception as e:
            logger.error(f"[Instagram] Error getting follower count: {e}")
            return {
                "platform": "instagram",
                "follower_count": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def get_follower_count() -> Dict[str, Any]:
    """Get Instagram follower count - wrapper function."""
    client = InstagramAPIClient()
    return client.get_follower_count()
