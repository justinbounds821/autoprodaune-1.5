"""
OAuth Manager pentru AutoPro Daune.

Acest modul implementează managerul OAuth pentru toate platformele de social media,
oferind funcționalități pentru autorizare, obținerea token-urilor și refresh-ul acestora.
"""

import time
import logging
import secrets
import requests
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlencode, parse_qs, urlparse
from datetime import datetime, timedelta

from .social_media_config import SocialMediaConfig, SocialPlatform, get_social_media_config


logger = logging.getLogger(__name__)


class OAuthError(Exception):
    """Excepție pentru erori OAuth."""
    pass


class OAuthManager:
    """
    Manager pentru procesele OAuth cu platformele de social media.
    
    Această clasă gestionează întregul flow OAuth pentru toate platformele
    suportate, inclusiv autorizarea, obținerea token-urilor și refresh-ul acestora.
    """
    
    def __init__(self, config: Optional[SocialMediaConfig] = None):
        """
        Inițializează OAuth Manager-ul.
        
        Args:
            config: Configurația pentru social media (opțional)
        """
        self.config = config or get_social_media_config()
        self.state_storage: Dict[str, Dict[str, Any]] = {}
    
    def generate_auth_url(
        self, 
        platform: SocialPlatform, 
        user_id: Optional[str] = None,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str]:
        """
        Generează URL-ul de autorizare OAuth pentru o platformă.
        
        Args:
            platform: Platforma de social media
            user_id: ID-ul utilizatorului (opțional)
            additional_params: Parametri adiționali pentru URL
            
        Returns:
            Tuple[str, str]: (auth_url, state_token)
            
        Raises:
            OAuthError: Dacă platforma nu este configurată
        """
        if not self.config.is_platform_configured(platform):
            raise OAuthError(f"Platforma {platform.value} nu este configurată")
        
        # Generează un token de state pentru securitate
        state_token = secrets.token_urlsafe(32)
        
        # Păstrează state-ul pentru validare ulterioară
        self.state_storage[state_token] = {
            "platform": platform,
            "user_id": user_id,
            "timestamp": int(time.time()),
            "additional_params": additional_params or {}
        }
        
        # Generează URL-ul de autorizare
        auth_url = self.config.get_auth_url(platform, state_token)
        
        logger.info(f"Generat URL de autorizare pentru {platform.value}: {auth_url}")
        return auth_url, state_token
    
    def handle_callback(
        self, 
        platform: SocialPlatform, 
        code: str, 
        state: str,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Procesează callback-ul OAuth și obține token-urile.
        
        Args:
            platform: Platforma de social media
            code: Codul de autorizare din callback
            state: Token-ul de state pentru validare
            additional_params: Parametri adiționali
            
        Returns:
            Dict[str, Any]: Token-urile și informațiile utilizatorului
            
        Raises:
            OAuthError: Dacă callback-ul este invalid sau apar erori
        """
        # Validează state-ul
        if state not in self.state_storage:
            raise OAuthError("Token de state invalid sau expirat")
        
        stored_data = self.state_storage[state]
        
        # Verifică că platforma se potrivește
        if stored_data["platform"] != platform:
            raise OAuthError("Platforma din state nu se potrivește cu cea din callback")
        
        # Verifică că state-ul nu a expirat (max 10 minute)
        if time.time() - stored_data["timestamp"] > 600:
            del self.state_storage[state]
            raise OAuthError("Token de state expirat")
        
        # Obține token-urile
        try:
            tokens = self._exchange_code_for_tokens(platform, code, additional_params)
            
            # Actualizează credențialele în configurație
            self.config.update_credentials(
                platform=platform,
                access_token=tokens.get("access_token"),
                refresh_token=tokens.get("refresh_token"),
                token_expires_at=tokens.get("expires_in", 0) + int(time.time()) if tokens.get("expires_in") else None,
                long_lived_token=tokens.get("long_lived_token")
            )
            
            # Curăță state-ul folosit
            del self.state_storage[state]
            
            logger.info(f"Token-uri obținute cu succes pentru {platform.value}")
            return tokens
            
        except Exception as e:
            logger.error(f"Eroare la obținerea token-urilor pentru {platform.value}: {e}")
            raise OAuthError(f"Eroare la obținerea token-urilor: {str(e)}")
    
    def _exchange_code_for_tokens(
        self, 
        platform: SocialPlatform, 
        code: str,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Schimbă codul de autorizare pentru token-uri.
        
        Args:
            platform: Platforma de social media
            code: Codul de autorizare
            additional_params: Parametri adiționali
            
        Returns:
            Dict[str, Any]: Token-urile și informațiile utilizatorului
        """
        config = self.config.get_platform_config(platform)
        
        # Pregătește parametrii pentru cerere
        data = {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": config.redirect_uri,
        }
        
        # Adaugă parametri specifici platformei
        if platform == SocialPlatform.TIKTOK:
            data["client_key"] = config.client_id
            data["client_secret"] = config.client_secret
        
        # Adaugă parametri adiționali
        if additional_params:
            data.update(additional_params)
        
        # Face cererea pentru token-uri
        response = requests.post(
            config.token_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        
        if response.status_code != 200:
            error_detail = response.json().get("error_description", "Unknown error")
            raise OAuthError(f"Eroare la obținerea token-urilor: {error_detail}")
        
        token_data = response.json()
        
        # Procesează răspunsul specific platformei
        if platform == SocialPlatform.INSTAGRAM:
            return self._process_instagram_response(token_data)
        elif platform == SocialPlatform.YOUTUBE:
            return self._process_youtube_response(token_data)
        elif platform == SocialPlatform.TIKTOK:
            return self._process_tiktok_response(token_data)
        elif platform == SocialPlatform.FACEBOOK:
            return self._process_facebook_response(token_data)
        
        return token_data
    
    def _process_instagram_response(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesează răspunsul Instagram."""
        result = {
            "access_token": token_data.get("access_token"),
            "expires_in": token_data.get("expires_in"),
            "user_id": token_data.get("user_id")
        }
        
        # Instagram folosește token-uri short-lived, trebuie să obținem long-lived
        if result["access_token"]:
            try:
                long_lived_token = self._get_instagram_long_lived_token(result["access_token"])
                result["long_lived_token"] = long_lived_token
            except Exception as e:
                logger.warning(f"Nu s-a putut obține long-lived token pentru Instagram: {e}")
        
        return result
    
    def _process_youtube_response(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesează răspunsul YouTube."""
        return {
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "expires_in": token_data.get("expires_in"),
            "token_type": token_data.get("token_type", "Bearer"),
            "scope": token_data.get("scope")
        }
    
    def _process_tiktok_response(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesează răspunsul TikTok."""
        return {
            "access_token": token_data.get("access_token"),
            "expires_in": token_data.get("expires_in"),
            "open_id": token_data.get("open_id"),
            "scope": token_data.get("scope"),
            "token_type": token_data.get("token_type", "Bearer")
        }
    
    def _process_facebook_response(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesează răspunsul Facebook."""
        return {
            "access_token": token_data.get("access_token"),
            "expires_in": token_data.get("expires_in"),
            "token_type": token_data.get("token_type", "Bearer")
        }
    
    def _get_instagram_long_lived_token(self, short_lived_token: str) -> str:
        """
        Obține un long-lived token pentru Instagram.
        
        Args:
            short_lived_token: Token-ul short-lived
            
        Returns:
            str: Long-lived token-ul
        """
        config = self.config.get_platform_config(SocialPlatform.INSTAGRAM)
        
        response = requests.get(
            f"{config.api_base_url}/access_token",
            params={
                "grant_type": "ig_exchange_token",
                "client_secret": config.client_secret,
                "access_token": short_lived_token
            },
            timeout=30
        )
        
        if response.status_code != 200:
            raise OAuthError("Nu s-a putut obține long-lived token pentru Instagram")
        
        return response.json()["access_token"]
    
    def refresh_access_token(self, platform: SocialPlatform) -> Dict[str, Any]:
        """
        Reîmprospătează token-ul de acces pentru o platformă.
        
        Args:
            platform: Platforma de social media
            
        Returns:
            Dict[str, Any]: Token-urile actualizate
            
        Raises:
            OAuthError: Dacă refresh-ul eșuează
        """
        creds = self.config.get_credentials(platform)
        
        if not creds.refresh_token:
            raise OAuthError(f"Nu există refresh token pentru {platform.value}")
        
        config = self.config.get_platform_config(platform)
        
        # Pregătește parametrii pentru cerere
        data = {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "refresh_token": creds.refresh_token,
            "grant_type": "refresh_token",
        }
        
        try:
            response = requests.post(
                config.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            
            if response.status_code != 200:
                error_detail = response.json().get("error_description", "Unknown error")
                raise OAuthError(f"Eroare la refresh-ul token-ului: {error_detail}")
            
            token_data = response.json()
            
            # Actualizează credențialele
            self.config.update_credentials(
                platform=platform,
                access_token=token_data.get("access_token"),
                refresh_token=token_data.get("refresh_token", creds.refresh_token),
                token_expires_at=token_data.get("expires_in", 0) + int(time.time()) if token_data.get("expires_in") else None
            )
            
            logger.info(f"Token reîmprospătat cu succes pentru {platform.value}")
            return token_data
            
        except Exception as e:
            logger.error(f"Eroare la refresh-ul token-ului pentru {platform.value}: {e}")
            raise OAuthError(f"Eroare la refresh-ul token-ului: {str(e)}")
    
    def is_token_valid(self, platform: SocialPlatform) -> bool:
        """
        Verifică dacă token-ul pentru o platformă este valid.
        
        Args:
            platform: Platforma de social media
            
        Returns:
            bool: True dacă token-ul este valid, False altfel
        """
        return self.config.validate_credentials(platform)
    
    def get_valid_access_token(self, platform: SocialPlatform) -> Optional[str]:
        """
        Obține un token de acces valid pentru o platformă.
        
        Args:
            platform: Platforma de social media
            
        Returns:
            Optional[str]: Token-ul de acces valid sau None
        """
        creds = self.config.get_credentials(platform)
        
        # Verifică dacă avem un token valid
        if self.is_token_valid(platform):
            return creds.access_token or creds.long_lived_token
        
        # Încearcă să reîmprospăteze token-ul
        try:
            if creds.refresh_token:
                self.refresh_access_token(platform)
                creds = self.config.get_credentials(platform)
                return creds.access_token or creds.long_lived_token
        except OAuthError:
            logger.warning(f"Nu s-a putut reîmprospăta token-ul pentru {platform.value}")
        
        return None
    
    def revoke_token(self, platform: SocialPlatform) -> bool:
        """
        Revocă token-ul pentru o platformă.
        
        Args:
            platform: Platforma de social media
            
        Returns:
            bool: True dacă revocarea a reușit, False altfel
        """
        creds = self.config.get_credentials(platform)
        access_token = creds.access_token or creds.long_lived_token
        
        if not access_token:
            return True
        
        config = self.config.get_platform_config(platform)
        
        try:
            # URL-urile de revocare variază pe platformă
            if platform == SocialPlatform.INSTAGRAM:
                revoke_url = f"{config.api_base_url}/revoke_token"
                params = {"access_token": access_token}
            elif platform == SocialPlatform.YOUTUBE:
                revoke_url = "https://oauth2.googleapis.com/revoke"
                params = {"token": access_token}
            elif platform == SocialPlatform.TIKTOK:
                revoke_url = f"{config.api_base_url}/oauth/revoke"
                params = {
                    "client_key": config.client_id,
                    "access_token": access_token
                }
            else:
                # Pentru alte platforme, doar curățăm credențialele locale
                self.config.update_credentials(platform=platform)
                return True
            
            response = requests.post(revoke_url, params=params, timeout=30)
            
            # Curăță credențialele locale indiferent de răspuns
            self.config.update_credentials(platform=platform)
            
            logger.info(f"Token revocat pentru {platform.value}")
            return response.status_code in [200, 204]
            
        except Exception as e:
            logger.error(f"Eroare la revocarea token-ului pentru {platform.value}: {e}")
            # Curăță credențialele locale chiar dacă revocarea eșuează
            self.config.update_credentials(platform=platform)
            return False
    
    def cleanup_expired_states(self) -> int:
        """
        Curăță state-urile expirate.
        
        Returns:
            int: Numărul de state-uri curățate
        """
        current_time = int(time.time())
        expired_states = [
            state for state, data in self.state_storage.items()
            if current_time - data["timestamp"] > 600  # 10 minute
        ]
        
        for state in expired_states:
            del self.state_storage[state]
        
        if expired_states:
            logger.info(f"Curățate {len(expired_states)} state-uri expirate")
        
        return len(expired_states)
    
    def get_user_info(self, platform: SocialPlatform) -> Dict[str, Any]:
        """
        Obține informațiile utilizatorului pentru o platformă.
        
        Args:
            platform: Platforma de social media
            
        Returns:
            Dict[str, Any]: Informațiile utilizatorului
            
        Raises:
            OAuthError: Dacă nu se pot obține informațiile
        """
        access_token = self.get_valid_access_token(platform)
        if not access_token:
            raise OAuthError(f"Nu există token valid pentru {platform.value}")
        
        config = self.config.get_platform_config(platform)
        
        try:
            if platform == SocialPlatform.INSTAGRAM:
                return self._get_instagram_user_info(access_token, config)
            elif platform == SocialPlatform.YOUTUBE:
                return self._get_youtube_user_info(access_token, config)
            elif platform == SocialPlatform.TIKTOK:
                return self._get_tiktok_user_info(access_token, config)
            elif platform == SocialPlatform.FACEBOOK:
                return self._get_facebook_user_info(access_token, config)
            else:
                raise OAuthError(f"Platforma {platform.value} nu este suportată pentru obținerea informațiilor utilizatorului")
                
        except Exception as e:
            logger.error(f"Eroare la obținerea informațiilor utilizatorului pentru {platform.value}: {e}")
            raise OAuthError(f"Eroare la obținerea informațiilor utilizatorului: {str(e)}")
    
    def _get_instagram_user_info(self, access_token: str, config) -> Dict[str, Any]:
        """Obține informațiile utilizatorului Instagram."""
        response = requests.get(
            f"{config.api_base_url}/me",
            params={
                "fields": "id,username,account_type,media_count",
                "access_token": access_token
            },
            timeout=30
        )
        
        if response.status_code != 200:
            raise OAuthError("Nu s-au putut obține informațiile utilizatorului Instagram")
        
        return response.json()
    
    def _get_youtube_user_info(self, access_token: str, config) -> Dict[str, Any]:
        """Obține informațiile utilizatorului YouTube."""
        response = requests.get(
            f"{config.api_base_url}/channels",
            params={
                "part": "snippet,statistics",
                "mine": "true",
                "access_token": access_token
            },
            timeout=30
        )
        
        if response.status_code != 200:
            raise OAuthError("Nu s-au putut obține informațiile utilizatorului YouTube")
        
        return response.json()
    
    def _get_tiktok_user_info(self, access_token: str, config) -> Dict[str, Any]:
        """Obține informațiile utilizatorului TikTok."""
        response = requests.get(
            f"{config.api_base_url}/user/info",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30
        )
        
        if response.status_code != 200:
            raise OAuthError("Nu s-au putut obține informațiile utilizatorului TikTok")
        
        return response.json()
    
    def _get_facebook_user_info(self, access_token: str, config) -> Dict[str, Any]:
        """Obține informațiile utilizatorului Facebook."""
        response = requests.get(
            f"{config.api_base_url}/me",
            params={
                "fields": "id,name,email",
                "access_token": access_token
            },
            timeout=30
        )
        
        if response.status_code != 200:
            raise OAuthError("Nu s-au putut obține informațiile utilizatorului Facebook")
        
        return response.json()


# Instanța globală a OAuth Manager-ului
oauth_manager = OAuthManager()


def get_oauth_manager() -> OAuthManager:
    """
    Obține instanța globală a OAuth Manager-ului.
    
    Returns:
        OAuthManager: Instanța OAuth Manager-ului
    """
    return oauth_manager
