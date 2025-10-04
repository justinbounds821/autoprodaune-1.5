from typing import Dict, Any, List
from datetime import datetime
from ..social_models import (
    SocialPosterInterface, PostMetadata, PostResult, PostStatus, ContentType
)
from .api_client import InstagramAPIClient
from .container_manager import ContainerManager
from .uploader import InstagramUploader
from .analytics import InstagramAnalytics

class InstagramPoster(SocialPosterInterface):
    """
    Orchestrator: compune API client + uploader + analytics.
    API-ul rămâne compatibil cu implementarea ta inițială.
    """

    def __init__(self):
        self.api = InstagramAPIClient()
        self.cm = ContainerManager(self.api)
        self.uploader = InstagramUploader(self.api, self.cm)
        self.analytics = InstagramAnalytics(self.api)

    # --- uploads
    def upload_video(self, video_path: str, metadata: PostMetadata, **kwargs) -> PostResult:
        return self.uploader.upload_video(video_path, metadata)

    def upload_image(self, image_path: str, metadata: PostMetadata, **kwargs) -> PostResult:
        return self.uploader.upload_image(image_path, metadata)

    def upload_carousel(self, media_paths: List[str], metadata: PostMetadata, **kwargs) -> PostResult:
        return self.uploader.upload_carousel(media_paths, metadata)

    # --- scheduling (nu e suportat oficial)
    def schedule_post(self, content_type: ContentType, content_data: str,
                      metadata: PostMetadata, scheduled_time: datetime, **kwargs) -> PostResult:
        return PostResult(False, error_message="Instagram nu suportă programare oficială prin API")

    # --- analytics / status / delete
    def get_post_status(self, post_id: str) -> PostStatus:
        return self.analytics.get_post_status(post_id)

    def delete_post(self, post_id: str) -> bool:
        return self.analytics.delete_post(post_id)

    def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        return self.analytics.get_post_analytics(post_id)

    # --- info / auth
    def is_authenticated(self) -> bool:
        return self.api.is_authenticated()

    def get_platform_info(self) -> Dict[str, Any]:
        return {
            "platform": "Instagram",
            "supported_content_types": ["image", "video", "carousel"],
            "max_image_size": "8MB",
            "max_video_size": "100MB",
            "supported_formats": ["jpg", "jpeg", "png", "mp4", "mov"],
            "max_carousel_items": 10,
            "supports_scheduling": False,
            "supports_deletion": True,
            "api_base": self.api.api_base_url,
            "authentication_status": self.is_authenticated(),
        }
