"""
Instagram adapter for AutoPro Daune autoposter.

This module uploads videos to Instagram Reels using the Instagram Graph API.
Publishing requires a Facebook App configured for Instagram Content
Publishing and a long‑lived access token.  The workflow is:

1. Create an upload container by POSTing the video to the `/{ig-user-id}/media` endpoint.
2. Once Facebook returns an `id`, publish the media by POSTing to
   `/{ig-user-id}/media_publish` with the container id.

Environment variables required:

* IG_BUSINESS_ACCOUNT_ID – the Instagram business account ID.
* IG_LONG_LIVED_TOKEN – a long lived user access token with the
  `instagram_content_publish` permission.

Optional:

* IG_CROSSPOST_TO_FB – set to "true" to enable cross‑posting to the
  associated Facebook Page.
* IG_PAGE_ID – Facebook Page ID for cross‑posting.
"""

import os
import requests
import time
import json
import mimetypes
from typing import Any, Dict, Optional
from datetime import datetime, timedelta


class InstagramUploader:
    """Handle Instagram video uploads with proper error handling."""
    
    def __init__(self):
        self.ig_user_id = os.getenv("IG_BUSINESS_ACCOUNT_ID")
        self.token = os.getenv("IG_LONG_LIVED_TOKEN")
        self.fb_app_id = os.getenv("FB_APP_ID")
        self.fb_app_secret = os.getenv("FB_APP_SECRET")
        self.graph_version = "v18.0"
        self.token_cache_file = ".instagram_token_cache.json"
        
        # Load cached token if exists
        self._load_cached_token()
    
    def _load_cached_token(self) -> None:
        """Load token from cache if still valid."""
        if os.path.exists(self.token_cache_file):
            try:
                with open(self.token_cache_file, 'r') as f:
                    data = json.load(f)
                    if datetime.fromisoformat(data['expires_at']) > datetime.now():
                        self.token = data['token']
                        print("[Instagram] Loaded cached access token")
            except Exception as e:
                print(f"[Instagram] Error loading cached token: {e}")
    
    def _save_token_cache(self, token: str, expires_at: datetime) -> None:
        """Save token to cache."""
        try:
            with open(self.token_cache_file, 'w') as f:
                json.dump({
                    'token': token,
                    'expires_at': expires_at.isoformat()
                }, f)
        except Exception as e:
            print(f"[Instagram] Error saving token cache: {e}")
    
    def _refresh_long_lived_token(self) -> bool:
        """Exchange current token for a new long-lived token."""
        if not all([self.fb_app_id, self.fb_app_secret, self.token]):
            return False
            
        url = f"https://graph.facebook.com/{self.graph_version}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.fb_app_id,
            "client_secret": self.fb_app_secret,
            "fb_exchange_token": self.token
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get("access_token"):
                self.token = result["access_token"]
                expires_in = result.get("expires_in", 5184000)  # Default 60 days
                expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                # Update environment variable
                os.environ["IG_LONG_LIVED_TOKEN"] = self.token
                
                # Cache the token
                self._save_token_cache(self.token, expires_at)
                
                print(f"[Instagram] Token refreshed, expires in {expires_in // 86400} days")
                return True
                
        except Exception as e:
            print(f"[Instagram] Failed to refresh token: {e}")
            
        return False
    
    def _validate_video(self, path: str) -> None:
        """Validate video meets Instagram requirements."""
        # Check file exists
        if not os.path.exists(path):
            raise FileNotFoundError(f"Video file not found: {path}")
            
        # Check file size (Instagram limit: 100MB for IGTV, 15MB for feed)
        file_size = os.path.getsize(path)
        if file_size > 100 * 1024 * 1024:
            raise ValueError(f"Video too large: {file_size / 1024 / 1024:.1f}MB (max 100MB)")
            
        # Check file type
        mime_type, _ = mimetypes.guess_type(path)
        if mime_type not in ["video/mp4", "video/quicktime"]:
            raise ValueError(f"Unsupported video type: {mime_type}")
    
    def upload(self, path: str, caption: str) -> None:
        """Upload a video to Instagram Reels."""
        if not all([self.ig_user_id, self.token]):
            raise RuntimeError("Instagram configuration incomplete")
            
        # Validate video
        self._validate_video(path)
        
        # Try upload with current token
        try:
            self._upload_video(path, caption)
            return
        except requests.HTTPError as e:
            if e.response.status_code in [400, 401] and 'token' in str(e.response.text).lower():
                # Token issue, try refresh
                print("[Instagram] Token issue detected, attempting refresh...")
                if self._refresh_long_lived_token():
                    # Retry with new token
                    self._upload_video(path, caption)
                    return
            raise
    
    def _upload_video(self, path: str, caption: str) -> None:
        """Internal method to upload video."""
        print(f"[Instagram] Starting upload for {os.path.basename(path)}...")
        
        # Method 1: Direct file upload (for smaller videos)
        file_size = os.path.getsize(path)
        if file_size < 50 * 1024 * 1024:  # Under 50MB
            self._upload_direct(path, caption)
        else:
            # Method 2: Resumable upload for larger videos
            self._upload_resumable(path, caption)
    
    def _upload_direct(self, path: str, caption: str) -> None:
        """Direct upload for smaller videos."""
        # Step 1: Create media container
        create_url = f"https://graph.facebook.com/{self.graph_version}/{self.ig_user_id}/media"
        
        with open(path, "rb") as f:
            files = {
                "video": (os.path.basename(path), f, "video/mp4")
            }
            data = {
                "caption": caption[:2200],
                "media_type": "REELS",  # Specifically for Reels
                "access_token": self.token,
                "share_to_feed": "true",  # Also share to main feed
                "thumb_offset": "2000"  # Thumbnail at 2 seconds
            }
            
            print("[Instagram] Uploading video...")
            resp = requests.post(create_url, data=data, files=files, timeout=120)
            
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("error"):
            raise RuntimeError(f"Instagram upload failed: {result['error']}")
            
        container_id = result.get("id")
        if not container_id:
            raise RuntimeError(f"No container ID returned: {result}")
            
        print(f"[Instagram] Media container created: {container_id}")
        
        # Step 2: Wait for processing
        self._wait_for_processing(container_id)
        
        # Step 3: Publish
        self._publish_media(container_id)
    
    def _upload_resumable(self, path: str, caption: str) -> None:
        """Resumable upload for larger videos."""
        # Step 1: Initialize resumable upload
        init_url = f"https://graph.facebook.com/{self.graph_version}/{self.ig_user_id}/media"
        
        file_size = os.path.getsize(path)
        
        params = {
            "media_type": "REELS",
            "caption": caption[:2200],
            "access_token": self.token,
            "upload_phase": "start",
            "upload_session_id": f"{int(time.time())}_{os.path.basename(path)}",
            "file_size": str(file_size)
        }
        
        print("[Instagram] Initializing resumable upload...")
        resp = requests.post(init_url, params=params, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("error"):
            raise RuntimeError(f"Instagram init failed: {result['error']}")
            
        upload_id = result.get("upload_id")
        upload_url = result.get("upload_url")
        
        if not upload_url:
            # Fallback to direct upload
            print("[Instagram] Resumable upload not available, using direct method")
            self._upload_direct(path, caption)
            return
            
        # Step 2: Upload video chunks
        print("[Instagram] Uploading video in chunks...")
        chunk_size = 4 * 1024 * 1024  # 4MB chunks
        
        with open(path, "rb") as f:
            offset = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                    
                headers = {
                    "Authorization": f"OAuth {self.token}",
                    "offset": str(offset),
                    "file_size": str(file_size)
                }
                
                chunk_resp = requests.post(
                    upload_url,
                    headers=headers,
                    data=chunk,
                    timeout=60
                )
                chunk_resp.raise_for_status()
                
                offset += len(chunk)
                print(f"[Instagram] Uploaded {offset / 1024 / 1024:.1f}MB / {file_size / 1024 / 1024:.1f}MB")
        
        # Step 3: Finish upload
        finish_params = {
            "media_type": "REELS",
            "caption": caption[:2200],
            "access_token": self.token,
            "upload_phase": "finish",
            "upload_id": upload_id
        }
        
        finish_resp = requests.post(init_url, params=finish_params, timeout=30)
        finish_resp.raise_for_status()
        finish_result = finish_resp.json()
        
        container_id = finish_result.get("id")
        if not container_id:
            raise RuntimeError(f"No container ID after upload: {finish_result}")
            
        # Wait for processing and publish
        self._wait_for_processing(container_id)
        self._publish_media(container_id)
    
    def _wait_for_processing(self, container_id: str) -> None:
        """Wait for Instagram to process the uploaded video."""
        status_url = f"https://graph.facebook.com/{self.graph_version}/{container_id}"
        params = {
            "fields": "status_code",
            "access_token": self.token
        }
        
        print("[Instagram] Waiting for video processing...")
        
        for attempt in range(30):  # Max 5 minutes
            time.sleep(10)
            
            resp = requests.get(status_url, params=params, timeout=10)
            resp.raise_for_status()
            result = resp.json()
            
            status = result.get("status_code")
            
            if status == "FINISHED":
                print("[Instagram] Video processing complete")
                return
            elif status == "ERROR":
                raise RuntimeError(f"Instagram processing failed for container {container_id}")
            else:
                print(f"[Instagram] Processing status: {status}")
                
        raise RuntimeError("Instagram processing timeout after 5 minutes")
    
    def _publish_media(self, container_id: str) -> None:
        """Publish the processed media container."""
        publish_url = f"https://graph.facebook.com/{self.graph_version}/{self.ig_user_id}/media_publish"
        
        data = {
            "creation_id": container_id,
            "access_token": self.token
        }
        
        # Cross-posting to Facebook
        if os.getenv("IG_CROSSPOST_TO_FB") == "true":
            data["crosspost_to_facebook_page"] = "true"
            page_id = os.getenv("IG_PAGE_ID")
            if page_id:
                data["page_id"] = page_id
        
        print("[Instagram] Publishing media...")
        resp = requests.post(publish_url, data=data, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("error"):
            raise RuntimeError(f"Instagram publish failed: {result['error']}")
            
        media_id = result.get("id")
        if media_id:
            print(f"[Instagram] Successfully published! Media ID: {media_id}")
            # Instagram post URL format: https://www.instagram.com/p/{shortcode}/
            # But we need to make another API call to get the shortcode
        else:
            raise RuntimeError(f"No media ID returned: {result}")


# Wrapper function pentru compatibilitate
def upload_video(path: str, caption: str) -> None:
    """Upload a video to Instagram Reels via the Graph API."""
    uploader = InstagramUploader()
    uploader.upload(path, caption)