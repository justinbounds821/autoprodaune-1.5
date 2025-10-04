"""
Token Refresh Service pentru AutoPro Daune.

Acest modul implementează serviciul pentru reîmprospătarea automată a token-urilor
OAuth pentru toate platformele de social media, cu suport pentru job-uri periodice.
"""

import time
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from threading import Thread
from dataclasses import dataclass

from .oauth_manager import OAuthManager, OAuthError, get_oauth_manager
from .social_media_config import SocialPlatform, SocialMediaCredentials


logger = logging.getLogger(__name__)


@dataclass
class TokenRefreshResult:
    """Rezultatul operației de refresh a token-ului."""
    platform: SocialPlatform
    success: bool
    error_message: Optional[str] = None
    new_expires_at: Optional[datetime] = None
    refreshed_at: Optional[datetime] = None


class TokenRefreshService:
    """
    Serviciu pentru reîmprospătarea automată a token-urilor OAuth.
    
    Această clasă oferă funcționalități pentru:
    - Reîmprospătarea automată a token-urilor
    - Monitorizarea expirării token-urilor
    - Job-uri periodice pentru refresh
    """
    
    def __init__(self, oauth_manager: Optional[OAuthManager] = None):
        """
        Inițializează Token Refresh Service.
        
        Args:
            oauth_manager: Instanța OAuth Manager-ului (opțional)
        """
        self.oauth_manager = oauth_manager or get_oauth_manager()
        self.refresh_interval = 3600  # 1 oră în secunde
        self.is_running = False
        self.refresh_thread: Optional[Thread] = None
        self.last_refresh_results: Dict[SocialPlatform, TokenRefreshResult] = {}
    
    def refresh_all_tokens(self) -> List[TokenRefreshResult]:
        """
        Reîmprospătează token-urile pentru toate platformele configurate.
        
        Returns:
            List[TokenRefreshResult]: Lista cu rezultatele refresh-ului
        """
        results = []
        configured_platforms = self.oauth_manager.config.get_all_configured_platforms()
        
        for platform in configured_platforms:
            result = self.refresh_platform_token(platform)
            results.append(result)
            self.last_refresh_results[platform] = result
        
        logger.info(f"Refresh completat pentru {len(configured_platforms)} platforme")
        return results
    
    def refresh_platform_token(self, platform: SocialPlatform) -> TokenRefreshResult:
        """
        Reîmprospătează token-ul pentru o platformă specifică.
        
        Args:
            platform: Platforma de social media
            
        Returns:
            TokenRefreshResult: Rezultatul operației de refresh
        """
        try:
            # Verifică dacă platforma este configurată
            if not self.oauth_manager.config.is_platform_configured(platform):
                return TokenRefreshResult(
                    platform=platform,
                    success=False,
                    error_message="Platforma nu este configurată"
                )
            
            # Verifică dacă avem refresh token
            creds = self.oauth_manager.config.get_credentials(platform)
            if not creds.refresh_token:
                return TokenRefreshResult(
                    platform=platform,
                    success=False,
                    error_message="Nu există refresh token"
                )
            
            # Verifică dacă token-ul trebuie reîmprospătat
            if not self._should_refresh_token(platform):
                return TokenRefreshResult(
                    platform=platform,
                    success=True,
                    error_message="Token-ul nu trebuie reîmprospătat încă"
                )
            
            # Reîmprospătează token-ul
            token_data = self.oauth_manager.refresh_access_token(platform)
            
            # Calculează noua dată de expirare
            expires_in = token_data.get("expires_in", 3600)
            new_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            result = TokenRefreshResult(
                platform=platform,
                success=True,
                new_expires_at=new_expires_at,
                refreshed_at=datetime.now()
            )
            
            logger.info(f"Token reîmprospătat cu succes pentru {platform.value}")
            return result
            
        except OAuthError as e:
            logger.error(f"Eroare OAuth la refresh-ul token-ului pentru {platform.value}: {e}")
            return TokenRefreshResult(
                platform=platform,
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Eroare neașteptată la refresh-ul token-ului pentru {platform.value}: {e}")
            return TokenRefreshResult(
                platform=platform,
                success=False,
                error_message=f"Eroare neașteptată: {str(e)}"
            )
    
    def _should_refresh_token(self, platform: SocialPlatform) -> bool:
        """
        Verifică dacă token-ul pentru o platformă trebuie reîmprospătat.
        
        Args:
            platform: Platforma de social media
            
        Returns:
            bool: True dacă token-ul trebuie reîmprospătat, False altfel
        """
        creds = self.oauth_manager.config.get_credentials(platform)
        
        # Dacă nu avem token, nu putem reîmprospăta
        if not creds.access_token and not creds.long_lived_token:
            return False
        
        # Dacă nu avem informație despre expirare, reîmprospătează preventiv
        if not creds.token_expires_at:
            return True
        
        # Verifică dacă token-ul expiră în următoarele 30 de minute
        current_time = int(time.time())
        expires_at = creds.token_expires_at
        buffer_time = 30 * 60  # 30 minute în secunde
        
        return expires_at - current_time <= buffer_time
    
    def get_tokens_needing_refresh(self) -> List[SocialPlatform]:
        """
        Obține lista cu platformele ale căror token-uri trebuie reîmprospătate.
        
        Returns:
            List[SocialPlatform]: Lista cu platformele care necesită refresh
        """
        platforms_needing_refresh = []
        configured_platforms = self.oauth_manager.config.get_all_configured_platforms()
        
        for platform in configured_platforms:
            if self._should_refresh_token(platform):
                platforms_needing_refresh.append(platform)
        
        return platforms_needing_refresh
    
    def start_periodic_refresh(self, interval: Optional[int] = None) -> None:
        """
        Pornește refresh-ul periodic al token-urilor.
        
        Args:
            interval: Intervalul de refresh în secunde (opțional)
        """
        if self.is_running:
            logger.warning("Refresh periodic deja pornit")
            return
        
        if interval:
            self.refresh_interval = interval
        
        self.is_running = True
        self.refresh_thread = Thread(target=self._refresh_loop, daemon=True)
        self.refresh_thread.start()
        
        logger.info(f"Refresh periodic pornit cu interval de {self.refresh_interval} secunde")
    
    def stop_periodic_refresh(self) -> None:
        """Oprește refresh-ul periodic al token-urilor."""
        if not self.is_running:
            logger.warning("Refresh periodic nu este pornit")
            return
        
        self.is_running = False
        if self.refresh_thread:
            self.refresh_thread.join(timeout=5)
        
        logger.info("Refresh periodic oprit")
    
    def _refresh_loop(self) -> None:
        """Loop-ul principal pentru refresh-ul periodic."""
        while self.is_running:
            try:
                # Obține platformele care necesită refresh
                platforms_to_refresh = self.get_tokens_needing_refresh()
                
                if platforms_to_refresh:
                    logger.info(f"Reîmprospătare token-uri pentru {len(platforms_to_refresh)} platforme")
                    
                    for platform in platforms_to_refresh:
                        result = self.refresh_platform_token(platform)
                        self.last_refresh_results[platform] = result
                        
                        if not result.success:
                            logger.error(f"Eșec la refresh-ul token-ului pentru {platform.value}: {result.error_message}")
                else:
                    logger.debug("Nu există token-uri care necesită reîmprospătare")
                
                # Așteaptă intervalul specificat
                time.sleep(self.refresh_interval)
                
            except Exception as e:
                logger.error(f"Eroare în loop-ul de refresh periodic: {e}")
                time.sleep(60)  # Așteaptă 1 minut înainte de a reîncerca
    
    def get_refresh_status(self) -> Dict[str, Any]:
        """
        Obține statusul curent al refresh-ului token-urilor.
        
        Returns:
            Dict[str, Any]: Statusul refresh-ului pentru toate platformele
        """
        status = {
            "periodic_refresh_running": self.is_running,
            "refresh_interval": self.refresh_interval,
            "platforms": {}
        }
        
        configured_platforms = self.oauth_manager.config.get_all_configured_platforms()
        
        for platform in configured_platforms:
            creds = self.oauth_manager.config.get_credentials(platform)
            last_result = self.last_refresh_results.get(platform)
            
            platform_status: Dict[str, Any] = {
                "configured": True,
                "has_access_token": bool(creds.access_token or creds.long_lived_token),
                "has_refresh_token": bool(creds.refresh_token),
                "token_expires_at": creds.token_expires_at,
                "needs_refresh": self._should_refresh_token(platform),
                "is_valid": self.oauth_manager.is_token_valid(platform)
            }
            
            if last_result:
                platform_status["last_refresh"] = {
                    "success": last_result.success,
                    "error_message": last_result.error_message,
                    "refreshed_at": last_result.refreshed_at.isoformat() if last_result.refreshed_at else None,
                    "new_expires_at": last_result.new_expires_at.isoformat() if last_result.new_expires_at else None
                }
            
            status["platforms"][platform.value] = platform_status
        
        return status
    
    def force_refresh_all(self) -> List[TokenRefreshResult]:
        """
        Forțează refresh-ul pentru toate platformele, indiferent de statusul token-ului.
        
        Returns:
            List[TokenRefreshResult]: Rezultatele refresh-ului forțat
        """
        results = []
        configured_platforms = self.oauth_manager.config.get_all_configured_platforms()
        
        for platform in configured_platforms:
            creds = self.oauth_manager.config.get_credentials(platform)
            
            if creds.refresh_token:
                result = self.refresh_platform_token(platform)
                results.append(result)
                self.last_refresh_results[platform] = result
            else:
                result = TokenRefreshResult(
                    platform=platform,
                    success=False,
                    error_message="Nu există refresh token"
                )
                results.append(result)
        
        logger.info(f"Refresh forțat completat pentru {len(results)} platforme")
        return results
    
    async def async_refresh_all_tokens(self) -> List[TokenRefreshResult]:
        """
        Versiunea async pentru reîmprospătarea token-urilor.
        
        Returns:
            List[TokenRefreshResult]: Rezultatele refresh-ului
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.refresh_all_tokens)
    
    def schedule_refresh(self, platform: SocialPlatform, delay_seconds: int) -> None:
        """
        Programează un refresh pentru o platformă specifică după un delay.
        
        Args:
            platform: Platforma de social media
            delay_seconds: Delay-ul în secunde
        """
        def delayed_refresh():
            time.sleep(delay_seconds)
            if self.is_running:
                result = self.refresh_platform_token(platform)
                self.last_refresh_results[platform] = result
                logger.info(f"Refresh programat completat pentru {platform.value}")
        
        thread = Thread(target=delayed_refresh, daemon=True)
        thread.start()
        
        logger.info(f"Refresh programat pentru {platform.value} în {delay_seconds} secunde")


# Instanța globală a Token Refresh Service-ului
token_refresh_service = TokenRefreshService()


def get_token_refresh_service() -> TokenRefreshService:
    """
    Obține instanța globală a Token Refresh Service-ului.
    
    Returns:
        TokenRefreshService: Instanța Token Refresh Service-ului
    """
    return token_refresh_service
