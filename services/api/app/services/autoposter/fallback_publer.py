"""
Publer fallback adapter for AutoPro Daune autoposter.

When native platform APIs (TikTok, Instagram, YouTube) reject an upload
or are unavailable, the autoposter can fall back to Publer, a social
media scheduler.  This module uploads the video to Publer and schedules
immediate publication on all configured profiles.

Environment variables required:

* PUBLER_API_KEY – API key for Publer.

Optional:

* PUBLER_PROFILE_IDS – Comma‑separated list of profile IDs to publish to.
* PUBLER_TIMEZONE – IANA time zone string (default Europe/Bucharest).
"""

import os
import requests
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class PublerUploader:
    """Handle video uploads to Publer as fallback."""
    
    def __init__(self):
        self.api_key = os.getenv("PUBLER_API_KEY")
        self.profile_ids = self._parse_profile_ids()
        self.timezone = os.getenv("PUBLER_TIMEZONE", "Europe/Bucharest")
        self.base_url = "https://api.publer.io/v1"
        
    def _parse_profile_ids(self) -> List[str]:
        """Parse profile IDs from environment variable."""
        profile_ids_env = os.getenv("PUBLER_PROFILE_IDS", "")
        if not profile_ids_env:
            return []
            
        return [pid.strip() for pid in profile_ids_env.split(",") if pid.strip()]
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
    
    def _validate_video(self, path: str) -> None:
        """Validate video file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Video file not found: {path}")
            
        # Publer has generous limits but let's be reasonable
        file_size = os.path.getsize(path)
        if file_size > 500 * 1024 * 1024:  # 500MB limit
            raise ValueError(f"Video too large: {file_size / 1024 / 1024:.1f}MB")
    
    def _get_workspaces(self) -> List[Dict[str, Any]]:
        """Get available workspaces."""
        url = f"{self.base_url}/workspaces"
        
        response = requests.get(url, headers=self._get_headers(), timeout=10)
        response.raise_for_status()
        
        result = response.json()
        return result.get("workspaces", [])
    
    def _get_profiles(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get social media profiles for a workspace."""
        url = f"{self.base_url}/workspaces/{workspace_id}/profiles"
        
        response = requests.get(url, headers=self._get_headers(), timeout=10)
        response.raise_for_status()
        
        result = response.json()
        return result.get("profiles", [])
    
    def upload(self, path: str, caption: str) -> None:
        """Upload video to Publer and schedule for immediate posting."""
        if not self.api_key:
            raise RuntimeError("Publer configuration incomplete: PUBLER_API_KEY missing")
            
        # Validate video
        self._validate_video(path)
        
        print(f"[Publer] Starting fallback upload for {os.path.basename(path)}...")
        
        # Get workspace (use first available)
        workspaces = self._get_workspaces()
        if not workspaces:
            raise RuntimeError("No Publer workspaces found")
            
        workspace_id = workspaces[0]["id"]
        print(f"[Publer] Using workspace: {workspaces[0].get('name', workspace_id)}")
        
        # Get profiles if not specified
        if not self.profile_ids:
            profiles = self._get_profiles(workspace_id)
            self.profile_ids = [p["id"] for p in profiles if p.get("status") == "active"]
            
            if not self.profile_ids:
                raise RuntimeError("No active social profiles found in Publer")
                
            print(f"[Publer] Found {len(self.profile_ids)} active profiles")
        
        # Step 1: Upload media
        media_id = self._upload_media(workspace_id, path)
        
        # Step 2: Create post
        post_id = self._create_post(workspace_id, media_id, caption)
        
        # Step 3: Schedule for immediate publishing
        self._schedule_post(workspace_id, post_id)
        
        print(f"[Publer] Successfully scheduled post for {len(self.profile_ids)} profiles")
    
    def _upload_media(self, workspace_id: str, path: str) -> str:
        """Upload media file to Publer."""
        url = f"{self.base_url}/workspaces/{workspace_id}/media"
        
        print("[Publer] Uploading video file...")
        
        with open(path, "rb") as f:
            files = {
                "file": (os.path.basename(path), f, "video/mp4")
            }
            
            headers = self._get_headers()
            # Remove Content-Type for multipart upload
            headers.pop("Content-Type", None)
            
            response = requests.post(
                url,
                headers=headers,
                files=files,
                timeout=120  # 2 minutes for upload
            )
            
        response.raise_for_status()
        result = response.json()
        
        media_id = result.get("media", {}).get("id")
        if not media_id:
            raise RuntimeError(f"Media upload failed: {result}")
            
        print(f"[Publer] Media uploaded successfully: {media_id}")
        
        # Wait for processing
        self._wait_for_media_processing(workspace_id, media_id)
        
        return media_id
    
    def _wait_for_media_processing(self, workspace_id: str, media_id: str) -> None:
        """Wait for media to be processed."""
        url = f"{self.base_url}/workspaces/{workspace_id}/media/{media_id}"
        
        print("[Publer] Waiting for media processing...")
        
        for attempt in range(30):  # Max 5 minutes
            time.sleep(10)
            
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            result = response.json()
            
            media = result.get("media", {})
            status = media.get("status")
            
            if status == "ready":
                print("[Publer] Media processing complete")
                return
            elif status == "failed":
                raise RuntimeError(f"Media processing failed: {media.get('error', 'Unknown error')}")
            else:
                print(f"[Publer] Processing status: {status}")
                
        raise RuntimeError("Media processing timeout after 5 minutes")
    
    def _create_post(self, workspace_id: str, media_id: str, caption: str) -> str:
        """Create a post with the uploaded media."""
        url = f"{self.base_url}/workspaces/{workspace_id}/posts"
        
        # Prepare post data
        post_data = {
            "profiles": self.profile_ids,
            "media": [media_id],
            "text": self._prepare_caption(caption),
            "options": {
                "facebook": {
                    "type": "reel"  # Post as Facebook Reel
                },
                "instagram": {
                    "type": "reel",  # Post as Instagram Reel
                    "share_to_feed": True
                },
                "tiktok": {
                    "disable_comments": False,
                    "disable_duet": False,
                    "disable_stitch": False
                },
                "youtube": {
                    "title": caption.split('.')[0][:100],  # First sentence as title
                    "privacy": "public",
                    "made_for_kids": False
                }
            }
        }
        
        print("[Publer] Creating post...")
        
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=post_data,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        post_id = result.get("post", {}).get("id")
        if not post_id:
            raise RuntimeError(f"Post creation failed: {result}")
            
        print(f"[Publer] Post created: {post_id}")
        return post_id
    
    def _schedule_post(self, workspace_id: str, post_id: str) -> None:
        """Schedule post for immediate publishing."""
        url = f"{self.base_url}/workspaces/{workspace_id}/posts/{post_id}/schedule"
        
        # Schedule for now (immediate posting)
        schedule_data = {
            "scheduled_at": datetime.now(timezone.utc).isoformat(),
            "timezone": self.timezone
        }
        
        print("[Publer] Scheduling post for immediate publishing...")
        
        response = requests.put(
            url,
            headers=self._get_headers(),
            json=schedule_data,
            timeout=30
        )
        
        response.raise_for_status()
        
        print("[Publer] Post scheduled successfully!")
    
    def _prepare_caption(self, caption: str) -> str:
        """Prepare caption for all platforms."""
        # Publer will handle platform-specific limits
        # But let's ensure we have good formatting
        
        # Add call-to-action if not present
        if "200 lei" not in caption and "recomand" not in caption.lower():
            caption += "\n\n💰 Recomandă un prieten și primești 200 lei!"
            
        # Add link if not present
        base_url = os.getenv("BASE_URL", "https://autopro-daune.ro")
        if base_url not in caption:
            caption += f"\n\n🔗 {base_url}"
            
        # Ensure hashtags
        if "#autoprodaune" not in caption.lower():
            caption += "\n\n#AutoProDaune #AsigurareAuto #Romania"
            
        return caption


# Wrapper function pentru compatibilitate
def upload_video(path: str, caption: str) -> None:
    """Upload a video to Publer for fallback publishing."""
    uploader = PublerUploader()
    uploader.upload(path, caption)