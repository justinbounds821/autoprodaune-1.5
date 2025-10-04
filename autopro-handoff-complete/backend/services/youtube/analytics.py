import logging, requests
from typing import Dict, Any
from ..social_poster import PostStatus
from .api_client import YouTubeAPIClient

log = logging.getLogger(__name__)

class YouTubeAnalytics:
    def __init__(self, api: YouTubeAPIClient): self.api = api

    @staticmethod
    def engagement_rate(views: int, likes: int, comments: int) -> float:
        if views <= 0: return 0.0
        return round(((likes + comments) / views) * 100, 2)

    def get_post_status(self, post_id: str) -> PostStatus:
        try:
            if not self.api.is_authenticated(): return PostStatus.FAILED
            token = self.api.get_access_token()
            if not token: return PostStatus.FAILED

            r = requests.get(self.api.videos_url, params={"part":"status","id":post_id},
                             headers=self.api.headers(token), timeout=30)
            if r.status_code != 200: return PostStatus.FAILED
            items = r.json().get("items",[])
            if not items: return PostStatus.FAILED
            st = items[0].get("status",{})
            if st.get("uploadStatus") == "uploaded" and st.get("privacyStatus") == "public":
                return PostStatus.PUBLISHED
            if st.get("uploadStatus") == "processing": return PostStatus.PROCESSING
            if st.get("uploadStatus") == "uploaded" and st.get("privacyStatus") in ("private","unlisted"):
                return PostStatus.SCHEDULED
            return PostStatus.FAILED
        except Exception as e:
            log.error("YT get_post_status error: %s", e)
            return PostStatus.FAILED

    def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        try:
            if not self.api.is_authenticated(): return {}
            token = self.api.get_access_token()
            if not token: return {}
            r = requests.get(self.api.videos_url, params={"part":"statistics,snippet","id":post_id},
                             headers=self.api.headers(token), timeout=30)
            if r.status_code != 200: return {}
            items = r.json().get("items",[])
            if not items: return {}
            v = items[0]; st=v.get("statistics",{}); sn=v.get("snippet",{})
            to_int = lambda x: int(x) if str(x).isdigit() else 0
            views, likes, comments = to_int(st.get("viewCount",0)), to_int(st.get("likeCount",0)), to_int(st.get("commentCount",0))
            return {
                "views": views, "likes": likes, "comments": comments,
                "title": sn.get("title"), "published_at": sn.get("publishedAt"),
                "engagement_rate": self.engagement_rate(views, likes, comments)
            }
        except Exception as e:
            log.error("YT analytics error: %s", e)
            return {}