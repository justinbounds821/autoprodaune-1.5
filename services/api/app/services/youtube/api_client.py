import logging, requests
from typing import Dict, Any, Optional
from datetime import datetime
from ..oauth_manager import get_oauth_manager
from ..social_media_config import SocialPlatform

log = logging.getLogger(__name__)

class YouTubeAPIClient:
    api_base_url = "https://www.googleapis.com/youtube/v3"
    upload_url   = "https://www.googleapis.com/upload/youtube/v3/videos"
    channels_url = f"{api_base_url}/channels"
    videos_url   = f"{api_base_url}/videos"
    playlists_url= f"{api_base_url}/playlists"

    def __init__(self) -> None:
        self.oauth_manager = get_oauth_manager()

    # --- auth ---
    def is_authenticated(self) -> bool:
        return self.oauth_manager.is_token_valid(SocialPlatform.YOUTUBE)

    def get_access_token(self) -> Optional[str]:
        return self.oauth_manager.get_valid_access_token(SocialPlatform.YOUTUBE)

    # --- http helpers ---
    @staticmethod
    def headers(token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # --- API calls ---
    def get_channel_id(self, token: str) -> Optional[str]:
        try:
            r = requests.get(self.channels_url, params={"part":"id","mine":"true"},
                             headers=self.headers(token), timeout=30)
            if r.status_code != 200: return None
            items = r.json().get("items", [])
            return items[0]["id"] if items else None
        except Exception as e:
            log.error("YT channel id error: %s", e)
            return None

    def get_video_info(self, video_id: str, token: str) -> Dict[str, Any]:
        try:
            r = requests.get(self.videos_url,
                             params={"part":"snippet,statistics,status","id":video_id},
                             headers=self.headers(token), timeout=30)
            if r.status_code != 200: return {}
            items = r.json().get("items", [])
            if not items: return {}
            v = items[0]; sn=v.get("snippet",{}); st=v.get("statistics",{}); s=v.get("status",{})
            to_int = lambda x: int(x) if str(x).isdigit() else 0
            return {
                "title": sn.get("title"),
                "description": sn.get("description"),
                "channel_title": sn.get("channelTitle"),
                "published_at": sn.get("publishedAt"),
                "view_count": to_int(st.get("viewCount",0)),
                "like_count": to_int(st.get("likeCount",0)),
                "comment_count": to_int(st.get("commentCount",0)),
                "privacy_status": s.get("privacyStatus"),
                "upload_status": s.get("uploadStatus"),
            }
        except Exception as e:
            log.error("YT get_video_info error: %s", e)
            return {}
    
    def get_follower_count(self) -> Dict[str, Any]:
        """
        Get subscriber count and channel statistics from YouTube.
        
        Returns:
            Dictionary with subscriber_count, video_count, view_count, etc.
        """
        try:
            token = self.get_access_token()
            
            if not token:
                raise RuntimeError("No YouTube access token available")
            
            # YouTube Data API endpoint for channel statistics
            params = {
                "part": "snippet,statistics,contentDetails",
                "mine": "true"  # Get authenticated user's channel
            }
            
            response = requests.get(
                self.channels_url,
                params=params,
                headers=self.headers(token),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            items = data.get("items", [])
            
            if not items:
                raise RuntimeError("No YouTube channel found for this account")
            
            channel = items[0]
            snippet = channel.get("snippet", {})
            statistics = channel.get("statistics", {})
            
            # Helper to convert string numbers to int
            to_int = lambda x: int(x) if str(x).isdigit() else 0
            
            metrics = {
                "platform": "youtube",
                "subscriber_count": to_int(statistics.get("subscriberCount", 0)),
                "video_count": to_int(statistics.get("videoCount", 0)),
                "view_count": to_int(statistics.get("viewCount", 0)),
                "channel_title": snippet.get("title", "Unknown"),
                "channel_id": channel.get("id", ""),
                "custom_url": snippet.get("customUrl", ""),
                "description": snippet.get("description", "")[:100],  # First 100 chars
                "published_at": snippet.get("publishedAt", ""),
                "hidden_subscriber_count": statistics.get("hiddenSubscriberCount", False),
                "timestamp": datetime.now().isoformat()
            }
            
            log.info(f"[YouTube] {metrics['channel_title']} - Subscribers: {metrics['subscriber_count']:,}")
            return metrics
            
        except Exception as e:
            log.error(f"[YouTube] Error getting follower count: {e}")
            return {
                "platform": "youtube",
                "subscriber_count": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def get_follower_count() -> Dict[str, Any]:
    """Get YouTube subscriber count - wrapper function."""
    client = YouTubeAPIClient()
    return client.get_follower_count()