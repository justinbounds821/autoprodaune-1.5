import os, logging, requests
from typing import Dict, Any, List
from datetime import datetime
from ..social_poster import SocialPosterInterface, PostMetadata, PostResult, PostStatus, ContentType
from .api_client import YouTubeAPIClient
from .uploader import YouTubeUploader
from .analytics import YouTubeAnalytics
from .scheduler import YouTubeScheduler

log = logging.getLogger(__name__)

class YouTubePoster(SocialPosterInterface):
    def __init__(self) -> None:
        self.api = YouTubeAPIClient()
        self.uploader = YouTubeUploader(self.api)
        self.analytics = YouTubeAnalytics(self.api)
        self.scheduler = YouTubeScheduler(self.api)

    # uploads
    def upload_video(self, video_path: str, metadata: PostMetadata, **_) -> PostResult:
        return self.uploader.upload_video(video_path, metadata)

    def upload_image(self, *_ , **__)->PostResult:
        return PostResult(success=False, error_message="YouTube nu suportă upload de imagini")

    def upload_carousel(self, *_, **__)->PostResult:
        return PostResult(success=False, error_message="YouTube nu suportă carousel posts")

    # schedule
    def schedule_post(self, content_type: ContentType, content_data: str,
                      metadata: PostMetadata, scheduled_time: datetime, **_) -> PostResult:
        if content_type != ContentType.VIDEO:
            return PostResult(success=False, error_message="YouTube suportă doar videoclipuri")
        if not os.path.exists(content_data):
            return PostResult(success=False, error_message=f"Fișierul video nu există: {content_data}")
        if not self.api.is_authenticated():
            return PostResult(success=False, error_message="Nu este autentificat pe YouTube")

        token = self.api.get_access_token()
        if not token: return PostResult(success=False, error_message="Nu s-a putut obține access token.")
        ch = self.api.get_channel_id(token)
        if not ch: return PostResult(success=False, error_message="Nu s-a putut obține channel id.")
        meta = self.uploader.prepare_video_metadata(metadata, ch)
        meta["status"]["privacyStatus"] = "private"

        up = self.uploader.upload_video_file(content_data, meta, token)
        if not up.success: return up
        return self.scheduler.schedule_video_publication(up.post_id, scheduled_time, token)

    # status/analytics/deletion
    def get_post_status(self, post_id: str) -> PostStatus:
        return self.analytics.get_post_status(post_id)

    def delete_post(self, post_id: str) -> bool:
        try:
            if not self.api.is_authenticated(): return False
            token = self.api.get_access_token()
            if not token: return False
            r = requests.delete(self.api.videos_url, params={"id": post_id},
                                headers=self.api.headers(token), timeout=30)
            return r.status_code == 204
        except Exception as e:
            log.error("YT delete error: %s", e)
            return False

    def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        return self.analytics.get_post_analytics(post_id)

    def is_authenticated(self) -> bool:
        return self.api.is_authenticated()

    def get_platform_info(self) -> Dict[str, Any]:
        return {
            "platform": "YouTube",
            "supported_content_types": ["video"],
            "max_video_size": "256GB",
            "supported_formats": ["mp4","mov","avi","wmv","flv","webm"],
            "max_duration": "12 hours",
            "supports_scheduling": True,
            "supports_deletion": True,
            "api_version": "v3",
            "authentication_status": self.is_authenticated(),
        }