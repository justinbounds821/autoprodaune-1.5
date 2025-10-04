import os, logging, requests
from typing import Dict, Any, Tuple
from datetime import datetime
from ..social_poster import PostMetadata, PostResult
from .api_client import YouTubeAPIClient

log = logging.getLogger(__name__)

class YouTubeUploader:
    def __init__(self, api: YouTubeAPIClient):
        self.api = api
        self.max_file_size = 256 * 1024 * 1024 * 1024  # 256GB

    # --- validation ---
    def validate_video_file(self, path: str) -> Tuple[bool, str]:
        if not os.path.exists(path):
            return False, f"Fișierul video nu există: {path}"
        if os.path.getsize(path) > self.max_file_size:
            return False, "Fișierul video este prea mare."
        return True, ""

    # --- metadata ---
    def prepare_video_metadata(self, md: PostMetadata, channel_id: str) -> Dict[str, Any]:
        desc = (md.description or "")
        if md.hashtags: desc += ("\n\n" + " ".join(f"#{t}" for t in md.hashtags))
        tags = (md.hashtags or [])[:10]

        priv = {"private":"private","unlisted":"unlisted"}.get((md.privacy or "").lower(),"public")
        category = "22"  # People & Blogs
        if md.category:
            m = {"automotive":"2","business":"25","education":"27","entertainment":"24","lifestyle":"22","technology":"28"}
            category = m.get(md.category.lower(), category)

        return {
            "snippet": {
                "title": md.title or "Video AutoPro Daune",
                "description": desc, "tags": tags, "categoryId": category, "channelId": channel_id
            },
            "status": {"privacyStatus": priv, "selfDeclaredMadeForKids": False},
        }

    # --- upload ---
    def upload_video_file(self, path: str, meta: Dict[str, Any], token: str) -> PostResult:
        try:
            init = requests.post(
                self.api.upload_url, params={"part":"snippet,status","uploadType":"resumable"},
                json=meta, headers=self.api.headers(token), timeout=30
            )
            if init.status_code != 200:
                msg = init.json().get("error",{}).get("message","Unknown error")
                return PostResult(success=False, error_message=f"Init upload eșuat: {msg}")

            upload_url = init.headers.get("Location")
            if not upload_url:
                return PostResult(success=False, error_message="Lipsește upload URL (Location).")

            with open(path, "rb") as fh:
                resp = requests.put(upload_url, data=fh,
                                    headers={"Content-Length": str(os.path.getsize(path)),
                                             "Content-Type": "video/*"},
                                    timeout=3600)

            if resp.status_code != 200:
                msg = (resp.json().get("error",{}).get("message","Unknown error")
                       if resp.headers.get("Content-Type","").startswith("application/json") else resp.text)
                return PostResult(success=False, error_message=f"Upload eșuat: {msg}")

            data = resp.json(); vid = data.get("id")
            if not vid:
                return PostResult(success=False, error_message="Nu s-a obținut ID-ul video.")
            info = self.api.get_video_info(vid, token)
            return PostResult(
                success=True, post_id=vid, platform_post_url=f"https://www.youtube.com/watch?v={vid}",
                published_at=datetime.now(), platform_specific_data=data, engagement_data=info
            )
        except Exception as e:
            return PostResult(success=False, error_message=f"Eroare upload: {e}")

    def upload_video(self, path: str, md: PostMetadata) -> PostResult:
        if not self.api.is_authenticated():
            return PostResult(success=False, error_message="Nu este autentificat pe YouTube")
        ok, err = self.validate_video_file(path)
        if not ok: return PostResult(success=False, error_message=err)

        token = self.api.get_access_token()
        if not token: return PostResult(success=False, error_message="Nu s-a putut obține access token.")
        channel_id = self.api.get_channel_id(token)
        if not channel_id: return PostResult(success=False, error_message="Nu s-a putut obține channel id.")
        meta = self.prepare_video_metadata(md, channel_id)
        return self.upload_video_file(path, meta, token)