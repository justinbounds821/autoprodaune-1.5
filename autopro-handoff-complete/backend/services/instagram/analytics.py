import requests
import logging
from typing import Dict, Any
from ..social_poster import PostStatus
from .api_client import InstagramAPIClient

logger = logging.getLogger(__name__)

class InstagramAnalytics:
    def __init__(self, api: InstagramAPIClient):
        self.api = api

    def get_post_status(self, post_id: str) -> PostStatus:
        try:
            if not self.api.is_authenticated():
                return PostStatus.FAILED
            token = self.api.get_access_token()
            if not token:
                return PostStatus.FAILED
            res = requests.get(self.api.media_info_url.format(media_id=post_id),
                               params={"access_token": token}, timeout=30)
            return PostStatus.PUBLISHED if res.status_code == 200 else PostStatus.FAILED
        except Exception as e:
            logger.error("Eroare status Instagram: %s", e)
            return PostStatus.FAILED

    def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        try:
            if not self.api.is_authenticated():
                return {}
            token = self.api.get_access_token()
            if not token:
                return {}
            res = requests.get(
                self.api.media_info_url.format(media_id=post_id),
                params={
                    "fields": "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,like_count,comments_count",
                    "access_token": token,
                },
                timeout=30,
            )
            if res.status_code != 200:
                return {}
            data = res.json()
            likes = int(data.get("like_count", 0) or 0)
            comments = int(data.get("comments_count", 0) or 0)
            # NOTE: impressions cere Business API; dacă nu există, tratăm ca 0 fără a crăpa
            views = int(data.get("impressions", 0) or 0)
            er = 0.0 if views == 0 else round(((likes + comments) / views) * 100, 2)
            return {"likes": likes, "comments": comments, "views": views, "engagement_rate": er}
        except Exception as e:
            logger.error("Eroare analytics Instagram: %s", e)
            return {}

    def delete_post(self, post_id: str) -> bool:
        try:
            if not self.api.is_authenticated():
                return False
            token = self.api.get_access_token()
            if not token:
                return False
            res = requests.delete(self.api.media_info_url.format(media_id=post_id),
                                  params={"access_token": token}, timeout=30)
            return res.status_code == 200
        except Exception as e:
            logger.error("Eroare delete Instagram: %s", e)
            return False
