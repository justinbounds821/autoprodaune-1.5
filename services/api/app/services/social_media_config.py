"""
Configurația pentru serviciile de social media - AutoPro Daune.

Acest modul conține configurația pentru toate platformele de social media
folosite în sistem, inclusiv cheile API, endpoint-urile și setările OAuth.
"""

import os
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class SocialPlatform(Enum):
    """Platformele de social media suportate."""
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"


class OAuthScope(Enum):
    """Scope-urile OAuth pentru fiecare platformă."""
    # TikTok
    TIKTOK_USER_INFO_BASIC = "user.info.basic"
    TIKTOK_VIDEO_PUBLISH = "video.publish"
    TIKTOK_VIDEO_LIST = "video.list"
    
    # Instagram
    INSTAGRAM_BASIC = "instagram_basic"
    INSTAGRAM_CONTENT_PUBLISH = "instagram_content_publish"
    
    # YouTube
    YOUTUBE_READONLY = "https://www.googleapis.com/auth/youtube.readonly"
    YOUTUBE_UPLOAD = "https://www.googleapis.com/auth/youtube.upload"
    YOUTUBE_CHANNEL_MANAGE = "https://www.googleapis.com/auth/youtube.channel-memberships.creator"
    
    # Facebook
    FACEBOOK_PAGES_SHOW_LIST = "pages_show_list"
    FACEBOOK_PAGES_MANAGE_POSTS = "pages_manage_posts"


@dataclass
class OAuthConfig:
    """Configurația OAuth pentru o platformă."""
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: list[str]
    auth_url: str
    token_url: str
    api_base_url: str
    version: Optional[str] = None


@dataclass
class SocialMediaCredentials:
    """Credențialele pentru o platformă de social media."""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[int] = None
    long_lived_token: Optional[str] = None


class SocialMediaConfig:
    """
    Configurația centralizată pentru toate platformele de social media.
    
    Această clasă oferă acces la configurația OAuth și credențialele
    pentru toate platformele suportate.
    """
    
    def __init__(self):
        """Inițializează configurația din variabilele de mediu."""
        self.platforms = {
            SocialPlatform.TIKTOK: self._get_tiktok_config(),
            SocialPlatform.INSTAGRAM: self._get_instagram_config(),
            SocialPlatform.YOUTUBE: self._get_youtube_config(),
            SocialPlatform.FACEBOOK: self._get_facebook_config(),
        }
        
        self.credentials = {
            SocialPlatform.TIKTOK: SocialMediaCredentials(),
            SocialPlatform.INSTAGRAM: SocialMediaCredentials(),
            SocialPlatform.YOUTUBE: SocialMediaCredentials(),
            SocialPlatform.FACEBOOK: SocialMediaCredentials(),
        }
    
    def _get_tiktok_config(self) -> OAuthConfig:
        """Configurația pentru TikTok."""
        return OAuthConfig(
            client_id=os.getenv("TIKTOK_CLIENT_KEY", ""),
            client_secret=os.getenv("TIKTOK_CLIENT_SECRET", ""),
            redirect_uri=os.getenv("TIKTOK_REDIRECT_URI", "http://localhost:8000/auth/tiktok/callback"),
            scopes=[
                OAuthScope.TIKTOK_USER_INFO_BASIC.value,
                OAuthScope.TIKTOK_VIDEO_PUBLISH.value,
                OAuthScope.TIKTOK_VIDEO_LIST.value,
            ],
            auth_url="https://www.tiktok.com/auth/authorize",
            token_url="https://open-api.tiktok.com/oauth/access_token",
            api_base_url="https://open-api.tiktok.com",
            version="v1.3"
        )
    
    def _get_instagram_config(self) -> OAuthConfig:
        """Configurația pentru Instagram."""
        return OAuthConfig(
            client_id=os.getenv("IG_CLIENT_ID", ""),
            client_secret=os.getenv("IG_CLIENT_SECRET", ""),
            redirect_uri=os.getenv("IG_REDIRECT_URI", "http://localhost:8000/auth/instagram/callback"),
            scopes=[
                OAuthScope.INSTAGRAM_BASIC.value,
                OAuthScope.INSTAGRAM_CONTENT_PUBLISH.value,
            ],
            auth_url="https://api.instagram.com/oauth/authorize",
            token_url="https://api.instagram.com/oauth/access_token",
            api_base_url="https://graph.instagram.com",
            version="v18.0"
        )
    
    def _get_youtube_config(self) -> OAuthConfig:
        """Configurația pentru YouTube."""
        return OAuthConfig(
            client_id=os.getenv("YOUTUBE_CLIENT_ID", ""),
            client_secret=os.getenv("YOUTUBE_CLIENT_SECRET", ""),
            redirect_uri=os.getenv("YOUTUBE_REDIRECT_URI", "http://localhost:8000/auth/youtube/callback"),
            scopes=[
                OAuthScope.YOUTUBE_READONLY.value,
                OAuthScope.YOUTUBE_UPLOAD.value,
                OAuthScope.YOUTUBE_CHANNEL_MANAGE.value,
            ],
            auth_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            api_base_url="https://www.googleapis.com/youtube/v3",
            version="v3"
        )
    
    def _get_facebook_config(self) -> OAuthConfig:
        """Configurația pentru Facebook."""
        return OAuthConfig(
            client_id=os.getenv("FB_CLIENT_ID", ""),
            client_secret=os.getenv("FB_CLIENT_SECRET", ""),
            redirect_uri=os.getenv("FB_REDIRECT_URI", "http://localhost:8000/auth/facebook/callback"),
            scopes=[
                OAuthScope.FACEBOOK_PAGES_SHOW_LIST.value,
                OAuthScope.FACEBOOK_PAGES_MANAGE_POSTS.value,
            ],
            auth_url="https://www.facebook.com/v18.0/dialog/oauth",
            token_url="https://graph.facebook.com/v18.0/oauth/access_token",
            api_base_url="https://graph.facebook.com",
            version="v18.0"
        )
    
    def get_platform_config(self, platform: SocialPlatform) -> OAuthConfig:
        """
        Obține configurația pentru o platformă specifică.
        
        Args:
            platform: Platforma de social media
            
        Returns:
            OAuthConfig: Configurația OAuth pentru platforma specificată
            
        Raises:
            ValueError: Dacă platforma nu este suportată
        """
        if platform not in self.platforms:
            raise ValueError(f"Platforma {platform} nu este suportată")
        
        return self.platforms[platform]
    
    def get_credentials(self, platform: SocialPlatform) -> SocialMediaCredentials:
        """
        Obține credențialele pentru o platformă specifică.
        
        Args:
            platform: Platforma de social media
            
        Returns:
            SocialMediaCredentials: Credențialele pentru platforma specificată
        """
        return self.credentials[platform]
    
    def update_credentials(
        self, 
        platform: SocialPlatform, 
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        token_expires_at: Optional[int] = None,
        long_lived_token: Optional[str] = None
    ) -> None:
        """
        Actualizează credențialele pentru o platformă specifică.
        
        Args:
            platform: Platforma de social media
            access_token: Token-ul de acces
            refresh_token: Token-ul de refresh
            token_expires_at: Timpul de expirare al token-ului (timestamp)
            long_lived_token: Token-ul long-lived (pentru Instagram)
        """
        creds = self.credentials[platform]
        
        if access_token is not None:
            creds.access_token = access_token
        if refresh_token is not None:
            creds.refresh_token = refresh_token
        if token_expires_at is not None:
            creds.token_expires_at = token_expires_at
        if long_lived_token is not None:
            creds.long_lived_token = long_lived_token
    
    def is_platform_configured(self, platform: SocialPlatform) -> bool:
        """
        Verifică dacă o platformă este configurată corect.
        
        Args:
            platform: Platforma de social media
            
        Returns:
            bool: True dacă platforma este configurată, False altfel
        """
        config = self.get_platform_config(platform)
        return bool(config.client_id and config.client_secret)
    
    def get_auth_url(self, platform: SocialPlatform, state: Optional[str] = None) -> str:
        """
        Generează URL-ul de autorizare OAuth pentru o platformă.
        
        Args:
            platform: Platforma de social media
            state: Parametrul de state pentru securitate
            
        Returns:
            str: URL-ul de autorizare OAuth
        """
        config = self.get_platform_config(platform)
        
        # Construiește parametrii pentru URL
        params = {
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "scope": " ".join(config.scopes),
            "response_type": "code",
        }
        
        if state:
            params["state"] = state
        
        # Adaugă parametri specifici platformei
        if platform == SocialPlatform.TIKTOK:
            params["scope"] = ",".join(config.scopes)
        
        # Construiește URL-ul
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{config.auth_url}?{param_string}"
    
    def get_all_configured_platforms(self) -> list[SocialPlatform]:
        """
        Obține lista cu toate platformele configurate corect.
        
        Returns:
            list[SocialPlatform]: Lista cu platformele configurate
        """
        return [platform for platform in SocialPlatform if self.is_platform_configured(platform)]
    
    def validate_credentials(self, platform: SocialPlatform) -> bool:
        """
        Validează credențialele pentru o platformă.
        
        Args:
            platform: Platforma de social media
            
        Returns:
            bool: True dacă credențialele sunt valide, False altfel
        """
        creds = self.get_credentials(platform)
        
        # Verifică dacă există un token de acces
        if not creds.access_token and not creds.long_lived_token:
            return False
        
        # Verifică dacă token-ul nu a expirat (dacă avem informație despre expirare)
        if creds.token_expires_at and creds.token_expires_at < int(time.time()):
            return False
        
        return True


# Instanța globală de configurație
social_media_config = SocialMediaConfig()


def get_social_media_config() -> SocialMediaConfig:
    """
    Obține instanța globală de configurație pentru social media.
    
    Returns:
        SocialMediaConfig: Instanța de configurație
    """
    return social_media_config
