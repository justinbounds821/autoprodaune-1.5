import os
import time
import logging
from typing import List
import requests
from datetime import datetime
from ..social_models import PostMetadata, PostResult
from .api_client import InstagramAPIClient

logger = logging.getLogger(__name__)

class ContainerManager:
    """
    Operații de nivel jos cu containerele Instagram:
    - create image/video/carousel
    - wait processing
    - publish
    """

    def __init__(self, api: InstagramAPIClient):
        self.api = api

    # ---- helpers

    @staticmethod
    def format_caption(md: PostMetadata) -> str:
        parts = []
        if md.title:
            parts.append(md.title)
        if md.description:
            parts.append(md.description)
        if md.hashtags:
            parts.append(" ".join(f"#{t}" for t in md.hashtags))
        return "\n\n".join(parts)

    # ---- create containers

    def create_image_container(self, image_path: str, md: PostMetadata, access_token: str) -> PostResult:
        try:
            with open(image_path, "rb") as f:
                files = {"image": (os.path.basename(image_path), f, "image/jpeg")}
                data = {"caption": self.format_caption(md), "media_type": "IMAGE"}
                res = requests.post(self.api.media_upload_url, files=files, data=data,
                                    params={"access_token": access_token}, timeout=60)
            if res.status_code != 200:
                err = res.json().get("error", {}).get("message", "Unknown error")
                return PostResult(False, error_message=f"Eroare create image container: {err}")
            cid = res.json().get("id")
            if not cid:
                return PostResult(False, error_message="ID container imagine lipsă")
            return PostResult(True, post_id=cid, platform_specific_data=res.json())
        except Exception as e:
            return PostResult(False, error_message=f"Exceptie create image container: {e}")

    def create_video_container(self, video_path: str, md: PostMetadata, access_token: str) -> PostResult:
        try:
            with open(video_path, "rb") as f:
                files = {"video": (os.path.basename(video_path), f, "video/mp4")}
                data = {"caption": self.format_caption(md), "media_type": "VIDEO"}
                res = requests.post(self.api.media_upload_url, files=files, data=data,
                                    params={"access_token": access_token}, timeout=300)
            if res.status_code != 200:
                err = res.json().get("error", {}).get("message", "Unknown error")
                return PostResult(False, error_message=f"Eroare create video container: {err}")
            cid = res.json().get("id")
            if not cid:
                return PostResult(False, error_message="ID container video lipsă")
            return PostResult(True, post_id=cid, platform_specific_data=res.json())
        except Exception as e:
            return PostResult(False, error_message=f"Exceptie create video container: {e}")

    def create_carousel_container(self, container_ids: List[str], md: PostMetadata, access_token: str) -> PostResult:
        try:
            data = {"media_type": "CAROUSEL", "children": ",".join(container_ids), "caption": self.format_caption(md)}
            res = requests.post(self.api.media_upload_url, data=data,
                                params={"access_token": access_token}, timeout=60)
            if res.status_code != 200:
                err = res.json().get("error", {}).get("message", "Unknown error")
                return PostResult(False, error_message=f"Eroare create carousel container: {err}")
            cid = res.json().get("id")
            if not cid:
                return PostResult(False, error_message="ID container carousel lipsă")
            return PostResult(True, post_id=cid, platform_specific_data=res.json())
        except Exception as e:
            return PostResult(False, error_message=f"Exceptie create carousel container: {e}")

    # ---- processing + publish

    def wait_processing(self, container_id: str, access_token: str, max_wait: int = 300) -> bool:
        start = time.time()
        while time.time() - start < max_wait:
            try:
                res = requests.get(
                    self.api.container_status_url.format(container_id=container_id),
                    params={"fields": "status_code", "access_token": access_token},
                    timeout=30,
                )
                if res.status_code == 200:
                    status = res.json().get("status_code")
                    if status == "FINISHED":
                        return True
                    if status == "ERROR":
                        logger.error("Container %s a intrat în starea ERROR", container_id)
                        return False
            except Exception as e:
                logger.error("Eroare check container %s: %s", container_id, e)
            time.sleep(5)
        return False

    def publish(self, container_id: str, access_token: str) -> PostResult:
        try:
            res = requests.post(self.api.media_publish_url, data={"creation_id": container_id},
                                params={"access_token": access_token}, timeout=60)
            if res.status_code != 200:
                err = res.json().get("error", {}).get("message", "Unknown error")
                return PostResult(False, error_message=f"Eroare publish media: {err}")
            media_id = res.json().get("id")
            if not media_id:
                return PostResult(False, error_message="ID media publicat lipsă")
            return PostResult(
                True,
                post_id=media_id,
                platform_post_url=f"https://www.instagram.com/p/{media_id}/",
                published_at=datetime.now(),
                platform_specific_data=res.json(),
            )
        except Exception as e:
            return PostResult(False, error_message=f"Exceptie publish media: {e}")
