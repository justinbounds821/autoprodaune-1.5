import os
from typing import List
from ..social_models import PostMetadata, PostResult
from .api_client import InstagramAPIClient
from .container_manager import ContainerManager

class InstagramUploader:
    """Nivel "orchestration" pentru upload (delegă la ContainerManager)."""

    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB

    def __init__(self, api: InstagramAPIClient, cm: ContainerManager):
        self.api = api
        self.cm = cm

    def upload_image(self, image_path: str, md: PostMetadata) -> PostResult:
        if not self.api.is_authenticated():
            return PostResult(False, error_message="Nu ești autentificat pe Instagram")
        if not os.path.exists(image_path):
            return PostResult(False, error_message=f"Fișier inexistent: {image_path}")

        token = self.api.get_access_token()
        if not token:
            return PostResult(False, error_message="Nu s-a putut obține access token")

        c = self.cm.create_image_container(image_path, md, token)
        if not c.success:
            return c
        if not self.cm.wait_processing(c.post_id, token):
            return PostResult(False, error_message="Imaginea nu a fost procesată în timp util")
        return self.cm.publish(c.post_id, token)

    def upload_video(self, video_path: str, md: PostMetadata) -> PostResult:
        if not self.api.is_authenticated():
            return PostResult(False, error_message="Nu ești autentificat pe Instagram")
        if not os.path.exists(video_path):
            return PostResult(False, error_message=f"Fișier inexistent: {video_path}")
        if os.path.getsize(video_path) > self.MAX_VIDEO_SIZE:
            return PostResult(False, error_message="Fișier video prea mare (max 100MB)")

        token = self.api.get_access_token()
        if not token:
            return PostResult(False, error_message="Nu s-a putut obține access token")

        c = self.cm.create_video_container(video_path, md, token)
        if not c.success:
            return c
        if not self.cm.wait_processing(c.post_id, token):
            return PostResult(False, error_message="Video-ul nu a fost procesat în timp util")
        return self.cm.publish(c.post_id, token)

    def upload_carousel(self, media_paths: List[str], md: PostMetadata) -> PostResult:
        if not self.api.is_authenticated():
            return PostResult(False, error_message="Nu ești autentificat pe Instagram")
        if len(media_paths) < 2 or len(media_paths) > 10:
            return PostResult(False, error_message="Carousel-ul trebuie să aibă 2–10 imagini")
        for p in media_paths:
            if not os.path.exists(p):
                return PostResult(False, error_message=f"Fișier inexistent: {p}")

        token = self.api.get_access_token()
        if not token:
            return PostResult(False, error_message="Nu s-a putut obține access token")

        container_ids = []
        for p in media_paths:
            c = self.cm.create_image_container(p, md, token)
            if not c.success:
                return c
            container_ids.append(c.post_id)

        car = self.cm.create_carousel_container(container_ids, md, token)
        if not car.success:
            return car
        if not self.cm.wait_processing(car.post_id, token):
            return PostResult(False, error_message="Carousel-ul nu a fost procesat în timp util")
        return self.cm.publish(car.post_id, token)
