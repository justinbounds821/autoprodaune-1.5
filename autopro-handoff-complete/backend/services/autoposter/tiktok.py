"""
TikTok adapter for AutoPro Daune autoposter.

This module implements a minimal interface to the TikTok Open API for
uploading short videos.  Uploading through the official API requires
obtaining an access token via the OAuth2 process and then calling the
`/post/publish/video/` endpoint with a valid upload ID and caption.  Full
documentation is available on TikTok’s developer portal【564548360441287†L1482-L1523】.

Note: TikTok enforces strict content policies and may reject uploads
programmatically.  To remain compliant, ensure videos meet TikTok’s
community guidelines and include required disclosures (e.g. ads).  If
the API returns an error that cannot be retried (e.g. policy violation),
the autoposter will fall back to using the Publer integrator as a
secondary publishing mechanism【564548360441287†L1616-L1655】.

Environment variables required:

* TIKTOK_CLIENT_KEY – the client key obtained from TikTok developer portal.
* TIKTOK_CLIENT_SECRET – the client secret for the application.
* TIKTOK_ACCESS_TOKEN – an OAuth2 access token with `upload.video` scope.
* TIKTOK_USER_ID – the business account ID or user ID that will own the
  published video.
"""

import os
import requests
import time
import json
from typing import Any, Dict, Optional
from datetime import datetime, timedelta


class TikTokUploader:
    """Handle TikTok video uploads with token refresh."""
    
    def __init__(self):
        self.client_key = os.getenv("TIKTOK_CLIENT_KEY")
        self.client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
        self.access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        self.refresh_token = os.getenv("TIKTOK_REFRESH_TOKEN")
        self.user_id = os.getenv("TIKTOK_USER_ID")
        self.token_file = ".tiktok_token_cache.json"
        
        # Load cached token if exists
        self._load_cached_token()
    
    def _load_cached_token(self) -> None:
        """Load access token from cache if valid."""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    if datetime.fromisoformat(data['expires_at']) > datetime.now():
                        self.access_token = data['access_token']
                        print("[TikTok] Loaded cached access token")
            except Exception as e:
                print(f"[TikTok] Error loading cached token: {e}")
    
    def _save_token_cache(self, access_token: str, expires_in: int) -> None:
        """Save access token to cache."""
        try:
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            with open(self.token_file, 'w') as f:
                json.dump({
                    'access_token': access_token,
                    'expires_at': expires_at.isoformat()
                }, f)
        except Exception as e:
            print(f"[TikTok] Error saving token cache: {e}")
    
    def _refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token."""
        if not self.refresh_token:
            return False
            
        url = "https://open.tiktokapis.com/v2/oauth/token/"
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get("access_token"):
                self.access_token = result["access_token"]
                self.refresh_token = result.get("refresh_token", self.refresh_token)
                expires_in = result.get("expires_in", 86400)
                
                # Update environment variable
                os.environ["TIKTOK_ACCESS_TOKEN"] = self.access_token
                if result.get("refresh_token"):
                    os.environ["TIKTOK_REFRESH_TOKEN"] = result["refresh_token"]
                
                # Cache the token
                self._save_token_cache(self.access_token, expires_in)
                
                print("[TikTok] Successfully refreshed access token")
                return True
                
        except Exception as e:
            print(f"[TikTok] Failed to refresh token: {e}")
            
        return False

    def upload(self, path: str, caption: str) -> None:
        """Upload a video to TikTok."""
        if not all([self.client_key, self.client_secret, self.user_id]):
            raise RuntimeError("TikTok configuration incomplete")
            
        # Check file size (TikTok limit: 287MB)
        file_size = os.path.getsize(path)
        if file_size > 287 * 1024 * 1024:
            raise ValueError(f"Video too large: {file_size / 1024 / 1024:.1f}MB (max 287MB)")
            
        # Try upload with current token
        try:
            self._upload_video(path, caption)
            return
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                # Token expired, try refresh
                print("[TikTok] Access token expired, attempting refresh...")
                if self._refresh_access_token():
                    # Retry with new token
                    self._upload_video(path, caption)
                    return
            raise
    
    def _upload_video(self, path: str, caption: str) -> None:
        """Internal method to upload video."""
        if not self.access_token:
            raise RuntimeError("No TikTok access token available")
            
        # Step 1: Initialize upload
        print(f"[TikTok] Initializing upload for {os.path.basename(path)}...")
        
        init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        init_payload = {
            "post_info": {
                "title": caption[:150],  # TikTok title limit
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
                "video_cover_timestamp_ms": 1000  # Cover at 1 second
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": os.path.getsize(path),
                "chunk_size": 10 * 1024 * 1024,  # 10MB chunks
                "total_chunk_count": 1  # Single chunk for small videos
            }
        }
        
        init_resp = requests.post(init_url, json=init_payload, headers=headers, timeout=30)
        init_resp.raise_for_status()
        init_data = init_resp.json()
        
        if init_data.get("error", {}).get("code") != "ok":
            raise RuntimeError(f"TikTok init failed: {init_data}")
            
        upload_url = init_data.get("data", {}).get("upload_url")
        publish_id = init_data.get("data", {}).get("publish_id")
        
        if not upload_url or not publish_id:
            raise RuntimeError(f"Missing upload URL or publish ID: {init_data}")

        # Step 2: Upload video file
        print("[TikTok] Uploading video file...")
        
        with open(path, "rb") as f:
            video_data = f.read()
            
        upload_headers = {
            "Content-Type": "video/mp4",
            "Content-Length": str(len(video_data)),
            "Content-Range": f"bytes 0-{len(video_data)-1}/{len(video_data)}"
        }
        
        upload_resp = requests.put(
            upload_url, 
            data=video_data, 
            headers=upload_headers, 
            timeout=120  # 2 minutes for upload
        )
        upload_resp.raise_for_status()
        
        print("[TikTok] Video uploaded successfully")

        # Step 3: Check status
        print("[TikTok] Checking upload status...")
        
        status_url = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"
        status_payload = {
            "publish_id": publish_id
        }
        
        # Poll for completion (max 30 seconds)
        for attempt in range(6):
            time.sleep(5)
            
            status_resp = requests.post(
                status_url, 
                json=status_payload, 
                headers=headers, 
                timeout=10
            )
            status_resp.raise_for_status()
            status_data = status_resp.json()
            
            if status_data.get("error", {}).get("code") != "ok":
                raise RuntimeError(f"TikTok status check failed: {status_data}")
                
            status = status_data.get("data", {}).get("status")
            
            if status == "PUBLISH_COMPLETE":
                post_id = status_data.get("data", {}).get("share_id")
                print(f"[TikTok] Video published successfully! ID: {post_id}")
                return
            elif status == "FAILED":
                fail_reason = status_data.get("data", {}).get("fail_reason")
                raise RuntimeError(f"TikTok publish failed: {fail_reason}")
            else:
                print(f"[TikTok] Status: {status}, waiting...")
                
        raise RuntimeError("TikTok publish timeout after 30 seconds")
    
    def get_follower_count(self) -> Dict[str, Any]:
        """
        Get follower count and account metrics from TikTok.
        
        Returns:
            Dictionary with follower_count, following_count, video_count, likes_count
        """
        try:
            # Refresh token if needed
            self._ensure_valid_token()
            
            # TikTok API endpoint for user info
            url = "https://open.tiktokapis.com/v2/user/info/"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "fields": ["follower_count", "following_count", "video_count", "likes_count", "display_name"]
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get("error", {}).get("code") != "ok":
                raise RuntimeError(f"TikTok API error: {result.get('error', {}).get('message')}")
            
            data = result.get("data", {}).get("user", {})
            
            metrics = {
                "platform": "tiktok",
                "follower_count": data.get("follower_count", 0),
                "following_count": data.get("following_count", 0),
                "video_count": data.get("video_count", 0),
                "likes_count": data.get("likes_count", 0),
                "display_name": data.get("display_name", "Unknown"),
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"[TikTok] Followers: {metrics['follower_count']:,}")
            return metrics
            
        except Exception as e:
            print(f"[TikTok] Error getting follower count: {e}")
            return {
                "platform": "tiktok",
                "follower_count": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _ensure_valid_token(self) -> None:
        """Ensure access token is valid, refresh if needed."""
        if not self.access_token:
            if self.refresh_token:
                print("[TikTok] Access token missing, attempting refresh...")
                self._refresh_access_token()
            else:
                raise RuntimeError("No TikTok access token or refresh token available")


# Wrapper function pentru compatibilitate
def upload_video(path: str, caption: str) -> None:
    """Upload a video to TikTok via the Open API."""
    uploader = TikTokUploader()
    uploader.upload(path, caption)

def get_follower_count() -> Dict[str, Any]:
    """Get TikTok follower count."""
    uploader = TikTokUploader()
    return uploader.get_follower_count()