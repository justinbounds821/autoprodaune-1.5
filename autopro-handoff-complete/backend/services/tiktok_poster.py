"""
Serviciu pentru postarea pe TikTok - AutoPro Daune.

Acest modul implementează serviciul de postare pe TikTok, oferind
funcționalități pentru upload de videoclipuri și gestionarea postărilor.
"""

import os
import json
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime

from .social_models import (
    SocialPosterInterface, PostMetadata, PostResult,
    PostStatus, ContentType
)
from .oauth_manager import get_oauth_manager
from .social_media_config import SocialPlatform


logger = logging.getLogger(__name__)


class TikTokPosterError(Exception):
    """Excepție pentru erori TikTok Poster."""
    pass


class TikTokPoster(SocialPosterInterface):
    """
    Serviciu pentru postarea pe TikTok.
    
    Această clasă implementează interfața SocialPosterInterface
    pentru platforma TikTok, oferind funcționalități complete de postare.
    """
    
    def __init__(self):
        """Inițializează TikTok Poster-ul."""
        self.oauth_manager = get_oauth_manager()
        self.api_base_url = "https://open-api.tiktok.com"
        self.upload_api_url = f"{self.api_base_url}/share/video/upload"
        self.publish_api_url = f"{self.api_base_url}/share/video/publish"
        self.video_info_url = f"{self.api_base_url}/video/list"
    
    def upload_video(
        self,
        video_path: str,
        metadata: PostMetadata,
        **kwargs
    ) -> PostResult:
        """
        Upload un videoclip pe TikTok.
        
        Args:
            video_path: Calea către fișierul video
            metadata: Metadata pentru postare
            **kwargs: Parametri adiționali
            
        Returns:
            PostResult: Rezultatul operației de upload
        """
        try:
            # Verifică autentificarea
            if not self.is_authenticated():
                return PostResult(
                    success=False,
                    error_message="Nu este autentificat pe TikTok"
                )
            
            # Verifică dacă fișierul video există
            if not os.path.exists(video_path):
                return PostResult(
                    success=False,
                    error_message=f"Fișierul video nu există: {video_path}"
                )
            
            # Verifică dimensiunea fișierului (max 287MB pentru TikTok)
            file_size = os.path.getsize(video_path)
            max_size = 287 * 1024 * 1024  # 287MB în bytes
            
            if file_size > max_size:
                return PostResult(
                    success=False,
                    error_message=f"Fișierul video este prea mare. Maxim permis: {max_size} bytes"
                )
            
            # Obține token-ul de acces
            access_token = self.oauth_manager.get_valid_access_token(SocialPlatform.TIKTOK)
            if not access_token:
                return PostResult(
                    success=False,
                    error_message="Nu s-a putut obține token-ul de acces pentru TikTok"
                )
            
            # Pregătește fișierul pentru upload
            with open(video_path, 'rb') as video_file:
                files = {
                    'video': (os.path.basename(video_path), video_file, 'video/mp4')
                }
                
                # Pregătește datele pentru upload
                data = {
                    'source_info': json.dumps({
                        'source': 'FILE_UPLOAD',
                        'video_size': file_size,
                        'chunk_size': min(file_size, 10 * 1024 * 1024),  # 10MB chunks
                        'total_chunk_count': 1
                    })
                }
                
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'multipart/form-data'
                }
                
                # Face upload-ul video-ului
                logger.info(f"Începe upload-ul video-ului pe TikTok: {video_path}")
                response = requests.post(
                    self.upload_api_url,
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=300  # 5 minute timeout pentru upload
                )
            
            if response.status_code != 200:
                error_detail = response.json().get('error', {}).get('message', 'Unknown error')
                return PostResult(
                    success=False,
                    error_message=f"Eroare la upload-ul video-ului: {error_detail}"
                )
            
            upload_data = response.json()
            video_id = upload_data.get('data', {}).get('publish_id')
            
            if not video_id:
                return PostResult(
                    success=False,
                    error_message="Nu s-a putut obține ID-ul video-ului după upload"
                )
            
            # Publică video-ul
            publish_result = self._publish_video(video_id, metadata, access_token)
            
            if publish_result.success:
                logger.info(f"Video uploadat și publicat cu succes pe TikTok: {video_id}")
                return PostResult(
                    success=True,
                    post_id=video_id,
                    platform_post_url=f"https://www.tiktok.com/@user/video/{video_id}",
                    published_at=datetime.now(),
                    platform_specific_data=upload_data
                )
            else:
                return publish_result
                
        except Exception as e:
            error_msg = f"Eroare neașteptată la upload-ul pe TikTok: {str(e)}"
            logger.error(error_msg)
            return PostResult(success=False, error_message=error_msg)
    
    def _publish_video(
        self, 
        video_id: str, 
        metadata: PostMetadata, 
        access_token: str
    ) -> PostResult:
        """
        Publică un video pe TikTok.
        
        Args:
            video_id: ID-ul video-ului
            metadata: Metadata pentru postare
            access_token: Token-ul de acces
            
        Returns:
            PostResult: Rezultatul publicării
        """
        try:
            # Pregătește datele pentru publicare
            publish_data = {
                'post_info': {
                    'title': metadata.title or '',
                    'description': metadata.description or '',
                    'privacy_level': 'PUBLIC_TO_EVERYONE',  # TikTok specific
                    'disable_duet': False,
                    'disable_comment': False,
                    'disable_stitch': False,
                    'video_cover_timestamp_ms': 1000  # Cover la 1 secunda
                },
                'source_info': {
                    'source': 'FILE_UPLOAD',
                    'publish_id': video_id
                }
            }
            
            # Adaugă hashtag-urile
            if metadata.hashtags:
                hashtag_text = ' '.join([f'#{tag}' for tag in metadata.hashtags])
                if 'post_info' in publish_data and 'description' in publish_data['post_info']:
                    publish_data['post_info']['description'] += f' {hashtag_text}'
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.publish_api_url,
                json=publish_data,
                headers=headers,
                timeout=60
            )
            
            if response.status_code != 200:
                error_detail = response.json().get('error', {}).get('message', 'Unknown error')
                return PostResult(
                    success=False,
                    error_message=f"Eroare la publicarea video-ului: {error_detail}"
                )
            
            publish_response = response.json()
            published_video_id = publish_response.get('data', {}).get('publish_id')
            
            return PostResult(
                success=True,
                post_id=published_video_id or video_id,
                platform_post_url=f"https://www.tiktok.com/@user/video/{published_video_id or video_id}",
                published_at=datetime.now(),
                platform_specific_data=publish_response
            )
            
        except Exception as e:
            return PostResult(
                success=False,
                error_message=f"Eroare la publicarea video-ului: {str(e)}"
            )
    
    def upload_image(
        self,
        image_path: str,
        metadata: PostMetadata,
        **kwargs
    ) -> PostResult:
        """
        Upload o imagine pe TikTok (nu este suportat direct).
        
        Args:
            image_path: Calea către fișierul imagine
            metadata: Metadata pentru postare
            **kwargs: Parametri adiționali
            
        Returns:
            PostResult: Rezultatul operației de upload
        """
        return PostResult(
            success=False,
            error_message="TikTok nu suportă upload direct de imagini"
        )
    
    def upload_carousel(
        self,
        media_paths: List[str],
        metadata: PostMetadata,
        **kwargs
    ) -> PostResult:
        """
        Upload un carousel pe TikTok (nu este suportat).
        
        Args:
            media_paths: Lista cu căile către fișierele media
            metadata: Metadata pentru postare
            **kwargs: Parametri adiționali
            
        Returns:
            PostResult: Rezultatul operației de upload
        """
        return PostResult(
            success=False,
            error_message="TikTok nu suportă carousel posts"
        )
    
    def schedule_post(
        self,
        content_type: ContentType,
        content_data: str | list[str],
        metadata: PostMetadata,
        scheduled_time: datetime,
        **kwargs
    ) -> PostResult:
        """
        Programează o postare pe TikTok (nu este suportat oficial).
        
        Args:
            content_type: Tipul de conținut
            content_data: Datele conținutului
            metadata: Metadata pentru postare
            scheduled_time: Momentul programat
            **kwargs: Parametri adiționali
            
        Returns:
            PostResult: Rezultatul operației de programare
        """
        return PostResult(
            success=False,
            error_message="TikTok nu suportă postări programate oficial"
        )
    
    def get_post_status(self, post_id: str) -> PostStatus:
        """
        Obține statusul unei postări pe TikTok.
        
        Args:
            post_id: ID-ul postării
            
        Returns:
            PostStatus: Statusul curent al postării
        """
        try:
            if not self.is_authenticated():
                return PostStatus.FAILED
            
            access_token = self.oauth_manager.get_valid_access_token(SocialPlatform.TIKTOK)
            if not access_token:
                return PostStatus.FAILED
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'fields': 'id,title,description,create_time,cover_image_url,share_url,embed_html,embed_link,like_count,comment_count,share_count,view_count',
                'video_ids': post_id
            }
            
            response = requests.get(
                self.video_info_url,
                params=params,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                return PostStatus.FAILED
            
            data = response.json()
            videos = data.get('data', {}).get('videos', [])
            
            if not videos:
                return PostStatus.FAILED
            
            video = videos[0]
            if video.get('id'):
                return PostStatus.PUBLISHED
            else:
                return PostStatus.PROCESSING
                
        except Exception as e:
            logger.error(f"Eroare la obținerea statusului postării TikTok: {e}")
            return PostStatus.FAILED
    
    def delete_post(self, post_id: str) -> bool:
        """
        Șterge o postare de pe TikTok.
        
        Args:
            post_id: ID-ul postării
            
        Returns:
            bool: True dacă ștergerea a reușit, False altfel
        """
        try:
            if not self.is_authenticated():
                return False
            
            access_token = self.oauth_manager.get_valid_access_token(SocialPlatform.TIKTOK)
            if not access_token:
                return False
            
            # TikTok nu oferă un API oficial pentru ștergerea postărilor
            # prin API-ul public, doar prin aplicația mobilă
            logger.warning(f"Ștergerea postării TikTok {post_id} nu este suportată prin API")
            return False
            
        except Exception as e:
            logger.error(f"Eroare la ștergerea postării TikTok: {e}")
            return False
    
    def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """
        Obține analytics pentru o postare pe TikTok.
        
        Args:
            post_id: ID-ul postării
            
        Returns:
            Dict[str, Any]: Datele de analytics
        """
        try:
            if not self.is_authenticated():
                return {}
            
            access_token = self.oauth_manager.get_valid_access_token(SocialPlatform.TIKTOK)
            if not access_token:
                return {}
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'fields': 'like_count,comment_count,share_count,view_count',
                'video_ids': post_id
            }
            
            response = requests.get(
                self.video_info_url,
                params=params,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                return {}
            
            data = response.json()
            videos = data.get('data', {}).get('videos', [])
            
            if not videos:
                return {}
            
            video = videos[0]
            return {
                'likes': video.get('like_count', 0),
                'comments': video.get('comment_count', 0),
                'shares': video.get('share_count', 0),
                'views': video.get('view_count', 0),
                'engagement_rate': self._calculate_engagement_rate(video)
            }
            
        except Exception as e:
            logger.error(f"Eroare la obținerea analytics pentru TikTok: {e}")
            return {}
    
    def _calculate_engagement_rate(self, video_data: Dict[str, Any]) -> float:
        """
        Calculează rata de engagement pentru un video TikTok.
        
        Args:
            video_data: Datele video-ului
            
        Returns:
            float: Rata de engagement
        """
        try:
            views = video_data.get('view_count', 0)
            likes = video_data.get('like_count', 0)
            comments = video_data.get('comment_count', 0)
            shares = video_data.get('share_count', 0)
            
            if views == 0:
                return 0.0
            
            total_engagement = likes + comments + shares
            engagement_rate = (total_engagement / views) * 100
            
            return round(engagement_rate, 2)
            
        except Exception:
            return 0.0
    
    def is_authenticated(self) -> bool:
        """
        Verifică dacă serviciul este autentificat pe TikTok.
        
        Returns:
            bool: True dacă este autentificat, False altfel
        """
        return self.oauth_manager.is_token_valid(SocialPlatform.TIKTOK)
    
    def get_platform_info(self) -> Dict[str, Any]:
        """
        Obține informații despre platforma TikTok.
        
        Returns:
            Dict[str, Any]: Informații despre platformă
        """
        return {
            'platform': 'TikTok',
            'supported_content_types': ['video'],
            'max_video_size': '287MB',
            'supported_formats': ['mp4', 'mov', 'avi'],
            'max_duration': '10 minutes',
            'supports_scheduling': False,
            'supports_deletion': False,
            'api_version': 'v1.3',
            'authentication_status': self.is_authenticated()
        }


# Instanța globală a TikTok Poster-ului
tiktok_poster = TikTokPoster()


def get_tiktok_poster() -> TikTokPoster:
    """
    Obține instanța globală a TikTok Poster-ului.
    
    Returns:
        TikTokPoster: Instanța TikTok Poster-ului
    """
    return tiktok_poster
