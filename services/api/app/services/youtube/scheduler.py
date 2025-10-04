import logging, requests
from typing import Dict, Any
from datetime import datetime
from ..social_poster import PostResult
from .api_client import YouTubeAPIClient

log = logging.getLogger(__name__)

class YouTubeScheduler:
    def __init__(self, api: YouTubeAPIClient): self.api = api

    def schedule_video_publication(self, video_id: str, when: datetime, token: str) -> PostResult:
        # YT nu are API real de "schedule exact" → demo: setăm public
        try:
            r = requests.put(self.api.videos_url, params={"part":"status"},
                             json={"id": video_id, "status": {"privacyStatus": "public"}},
                             headers=self.api.headers(token), timeout=30)
            if r.status_code != 200:
                msg = r.json().get("error",{}).get("message","Unknown error")
                return PostResult(success=False, error_message=f"Programare eșuată: {msg}")
            return PostResult(success=True, post_id=video_id,
                              platform_specific_data={"scheduled": True, "scheduled_time": when.isoformat()})
        except Exception as e:
            return PostResult(success=False, error_message=f"Eroare programare: {e}")