"""
YouTube adapter for AutoPro Daune autoposter.

This module uploads videos to YouTube Shorts via the YouTube Data API v3.
Videos must be vertical (≤60 seconds) and include "#Shorts" for best
discovery.  The adapter uses OAuth2 credentials provided via
environment variables.  Be mindful of API quotas and refresh token
expiration.

Environment variables required:

* YOUTUBE_CLIENT_ID – OAuth2 client ID for a project with YouTube Data API enabled.
* YOUTUBE_CLIENT_SECRET – OAuth2 client secret.
* YOUTUBE_REFRESH_TOKEN – Refresh token authorised for uploads.
* YOUTUBE_CHANNEL_ID – Target channel ID.

Optional:

* YOUTUBE_CATEGORY_ID – Video category ID (default 22 – People & Blogs).
* YOUTUBE_PRIVACY_STATUS – Privacy setting (public, unlisted, private).
"""

import os
import json
import time
from typing import Any, Dict, Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


class YouTubeUploader:
    """Handle YouTube video uploads with proper OAuth2 flow."""
    
    def __init__(self):
        self.client_id = os.getenv("YOUTUBE_CLIENT_ID")
        self.client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
        self.refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
        self.channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
        self.token_cache_file = ".youtube_token_cache.json"
        self.creds = None
        
        # Initialize credentials
        self._init_credentials()
    
    def _init_credentials(self) -> None:
        """Initialize OAuth2 credentials."""
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            return
            
        # Try to load from cache first
        if os.path.exists(self.token_cache_file):
            try:
                with open(self.token_cache_file, 'r') as f:
                    token_data = json.load(f)
                    
                self.creds = Credentials(
                    token=token_data.get('access_token'),
                    refresh_token=self.refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    scopes=["https://www.googleapis.com/auth/youtube.upload"]
                )
                
                # Check if token needs refresh
                if self.creds.expired:
                    self._refresh_credentials()
                else:
                    print("[YouTube] Loaded cached access token")
                    
            except Exception as e:
                print(f"[YouTube] Error loading cached token: {e}")
                self._create_new_credentials()
        else:
            self._create_new_credentials()
    
    def _create_new_credentials(self) -> None:
        """Create new credentials from refresh token."""
        self.creds = Credentials(
            token=None,
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=["https://www.googleapis.com/auth/youtube.upload"]
        )
        self._refresh_credentials()
    
    def _refresh_credentials(self) -> None:
        """Refresh the access token."""
        try:
            self.creds.refresh(Request())
            
            # Save to cache
            with open(self.token_cache_file, 'w') as f:
                json.dump({
                    'access_token': self.creds.token,
                    'token_type': 'Bearer',
                    'expires_at': self.creds.expiry.isoformat() if self.creds.expiry else None
                }, f)
                
            print("[YouTube] Access token refreshed successfully")
            
        except Exception as e:
            print(f"[YouTube] Failed to refresh credentials: {e}")
            raise
    
    def _validate_video(self, path: str) -> None:
        """Validate video meets YouTube requirements."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Video file not found: {path}")
            
        # Check file size (YouTube limit: 128GB but we'll be reasonable)
        file_size = os.path.getsize(path)
        if file_size > 1024 * 1024 * 1024:  # 1GB limit for safety
            raise ValueError(f"Video too large: {file_size / 1024 / 1024:.1f}MB")
    
    def upload(self, path: str, caption: str) -> None:
        """Upload a video to YouTube Shorts."""
        if not all([self.client_id, self.client_secret, self.refresh_token, self.channel_id]):
            raise RuntimeError("YouTube configuration incomplete")
            
        if not self.creds:
            raise RuntimeError("YouTube credentials not initialized")
            
        # Validate video
        self._validate_video(path)
        
        # Build YouTube service
        youtube = build("youtube", "v3", credentials=self.creds)
        
        # Prepare metadata
        title = self._prepare_title(caption)
        description = self._prepare_description(caption)
        tags = self._extract_tags(caption)
        
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": os.getenv("YOUTUBE_CATEGORY_ID", "22"),
                "defaultLanguage": "ro",
                "defaultAudioLanguage": "ro"
            },
            "status": {
                "privacyStatus": os.getenv("YOUTUBE_PRIVACY_STATUS", "public"),
                "selfDeclaredMadeForKids": False,
                "embeddable": True,
                "publicStatsViewable": True
            }
        }
        
        # Call the API's videos.insert method
        media = MediaFileUpload(
            path,
            mimetype="video/mp4",
            resumable=True,
            chunksize=50 * 1024 * 1024  # 50MB chunks
        )
        
        print(f"[YouTube] Starting upload for {os.path.basename(path)}...")
        
        try:
            request = youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            # Execute upload with resumable support
            response = None
            error_count = 0
            max_retries = 3
            
            while response is None:
                try:
                    status, response = request.next_chunk()
                    
                    if status:
                        progress = int(status.progress() * 100)
                        print(f"[YouTube] Upload progress: {progress}%")
                        
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        # Retry on server errors
                        error_count += 1
                        if error_count > max_retries:
                            raise
                            
                        time.sleep(5 ** error_count)  # Exponential backoff
                        print(f"[YouTube] Server error, retrying... ({error_count}/{max_retries})")
                        continue
                        
                    elif e.resp.status == 401:
                        # Try to refresh token
                        print("[YouTube] Authentication error, refreshing token...")
                        self._refresh_credentials()
                        youtube = build("youtube", "v3", credentials=self.creds)
                        request = youtube.videos().insert(
                            part=",".join(body.keys()),
                            body=body,
                            media_body=media
                        )
                        continue
                        
                    else:
                        raise
                        
                except Exception as e:
                    print(f"[YouTube] Upload error: {e}")
                    raise
            
            if response and "id" in response:
                video_id = response["id"]
                video_url = f"https://youtube.com/watch?v={video_id}"
                
                print(f"[YouTube] Upload successful!")
                print(f"[YouTube] Video ID: {video_id}")
                print(f"[YouTube] Video URL: {video_url}")
                
                # Check if it's a Short
                if self._is_short_format(path, response):
                    print("[YouTube] Video will appear as YouTube Short")
                    
            else:
                raise RuntimeError(f"YouTube upload failed: {response}")
                
        except HttpError as e:
            error_content = json.loads(e.content.decode('utf-8'))
            error_message = error_content.get('error', {}).get('message', str(e))
            
            # Common error handling
            if 'quotaExceeded' in str(e):
                raise RuntimeError("YouTube API quota exceeded. Try again tomorrow.")
            elif 'videoNotFound' in str(e):
                raise RuntimeError("Video processing failed on YouTube's side.")
            else:
                raise RuntimeError(f"YouTube API error: {error_message}")
    
    def _prepare_title(self, caption: str) -> str:
        """Prepare video title from caption."""
        # Extract first sentence or up to 100 chars
        title = caption.split('.')[0].strip()
        
        if len(title) > 95:
            title = title[:95] + "..."
            
        # Ensure #Shorts is included for Shorts discovery
        if "#shorts" not in title.lower():
            if len(title) <= 85:
                title += " #Shorts"
                
        return title
    
    def _prepare_description(self, caption: str) -> str:
        """Prepare video description."""
        description = caption
        
        # Add default hashtags if not present
        default_tags = ["#Shorts", "#AutoProDaune", "#Romania", "#AsigurareAuto"]
        
        for tag in default_tags:
            if tag.lower() not in description.lower():
                description += f" {tag}"
                
        # Add CTA
        description += "\n\n🚗 Ai avut un accident? Te ajutăm cu dosarul de daună!"
        description += "\n💰 Recomandă un prieten și primești 200 lei!"
        description += f"\n🔗 {os.getenv('BASE_URL', 'https://autopro-daune.ro')}"
        
        return description[:5000]  # YouTube description limit
    
    def _extract_tags(self, caption: str) -> list:
        """Extract hashtags from caption as tags."""
        import re
        
        # Find all hashtags
        hashtags = re.findall(r'#\w+', caption)
        
        # Clean and prepare tags
        tags = [tag[1:] for tag in hashtags]  # Remove #
        
        # Add default tags
        default_tags = ["Shorts", "AutoProDaune", "Romania", "AsigurareAuto", 
                       "AccidentAuto", "Despagubiri", "ConstatareAmiabila"]
        
        for tag in default_tags:
            if tag not in tags:
                tags.append(tag)
                
        # YouTube allows max 500 chars for all tags combined
        # and max 30 tags
        tags = tags[:30]
        
        # Ensure total length is under 500 chars
        total_length = sum(len(tag) + 1 for tag in tags)  # +1 for comma
        while total_length > 500 and tags:
            tags.pop()
            total_length = sum(len(tag) + 1 for tag in tags)
            
        return tags
    
    def _is_short_format(self, path: str, response: dict) -> bool:
        """Check if video qualifies as a YouTube Short."""
        # YouTube Shorts criteria:
        # - Vertical or square aspect ratio
        # - 60 seconds or less
        # - Has #Shorts in title or description
        
        duration = response.get('contentDetails', {}).get('duration', 'PT0S')
        
        # Parse ISO 8601 duration
        import re
        match = re.match(r'PT(?:(\d+)M)?(?:(\d+)S)?', duration)
        if match:
            minutes = int(match.group(1) or 0)
            seconds = int(match.group(2) or 0)
            total_seconds = minutes * 60 + seconds
            
            if total_seconds <= 60:
                return True
                
        return False


# Wrapper function pentru compatibilitate
def upload_video(path: str, caption: str) -> None:
    """Upload a video to YouTube Shorts."""
    uploader = YouTubeUploader()
    uploader.upload(path, caption)