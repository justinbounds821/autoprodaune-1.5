"""
HeyGen Service - Serviciu pentru generarea de videoclipuri AI folosind HeyGen API
"""

import os
import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Configurează logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeyGenVideoStyle(Enum):
    """Stiluri de video suportate de HeyGen"""
    REALISTIC = "realistic"
    ANIMATED = "animated"
    CARTOON = "cartoon"
    DOCUMENTARY = "documentary"
    PRESENTATION = "presentation"

class HeyGenVideoQuality(Enum):
    """Calități de video suportate"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

@dataclass
class HeyGenVideoRequest:
    """Request pentru generarea unui video HeyGen"""
    script: str
    voice_id: Optional[str] = None
    avatar_id: Optional[str] = None
    style: HeyGenVideoStyle = HeyGenVideoStyle.REALISTIC
    quality: HeyGenVideoQuality = HeyGenVideoQuality.HIGH
    background_music: bool = False
    subtitles: bool = True
    language: str = "en"
    speed: float = 1.0  # viteza vocii (0.5 - 2.0)

@dataclass
class HeyGenVideoResponse:
    """Response de la HeyGen API"""
    success: bool
    video_id: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    status: str = "pending"
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    duration: Optional[float] = None

class HeyGenService:
    """Serviciu pentru integrarea cu HeyGen API"""
    
    def __init__(self):
        self.api_key = os.getenv("HEYGEN_API_KEY")
        self.base_url = os.getenv("HEYGEN_BASE_URL", "https://api.heygen.com/v1")
        self.timeout = int(os.getenv("HEYGEN_TIMEOUT", "600"))  # 10 minute
        self.max_retries = int(os.getenv("HEYGEN_MAX_RETRIES", "3"))
        
        if not self.api_key:
            logger.warning("HEYGEN_API_KEY nu este configurat. Serviciul va funcționa în mod limitat.")
    
    async def generate_video(self, request: HeyGenVideoRequest) -> HeyGenVideoResponse:
        """
        Generează un video folosind HeyGen API
        
        Args:
            request: Parametrii pentru generarea video
            
        Returns:
            HeyGenVideoResponse cu rezultatul generării
        """
        if not self.api_key:
            return HeyGenVideoResponse(
                success=False,
                error_message="HEYGEN_API_KEY nu este configurat"
            )
        
        try:
            # Pregătește payload-ul pentru API
            payload = {
                "script": request.script,
                "style": request.style.value,
                "quality": request.quality.value,
                "background_music": request.background_music,
                "subtitles": request.subtitles,
                "language": request.language,
                "speed": request.speed
            }
            
            if request.voice_id:
                payload["voice_id"] = request.voice_id
            
            if request.avatar_id:
                payload["avatar_id"] = request.avatar_id
            
            # Face cererea către HeyGen API
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                async with session.post(
                    f"{self.base_url}/video/generate",
                    json=payload,
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        return HeyGenVideoResponse(
                            success=True,
                            video_id=data.get("video_id"),
                            status=data.get("status", "processing"),
                            created_at=datetime.now(),
                            estimated_completion=datetime.now() if data.get("estimated_completion") else None,
                            duration=data.get("estimated_duration")
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"Eroare HeyGen API: {response.status} - {error_text}")
                        
                        return HeyGenVideoResponse(
                            success=False,
                            error_message=f"API Error {response.status}: {error_text}"
                        )
                        
        except asyncio.TimeoutError:
            logger.error("Timeout la generarea video HeyGen")
            return HeyGenVideoResponse(
                success=False,
                error_message="Timeout la generarea video"
            )
        except Exception as e:
            logger.error(f"Eroare la generarea video HeyGen: {str(e)}")
            return HeyGenVideoResponse(
                success=False,
                error_message=f"Eroare internă: {str(e)}"
            )
    
    async def get_video_status(self, video_id: str) -> HeyGenVideoResponse:
        """
        Verifică statusul unui video în generare
        
        Args:
            video_id: ID-ul video-ului
            
        Returns:
            HeyGenVideoResponse cu statusul actual
        """
        if not self.api_key:
            return HeyGenVideoResponse(
                success=False,
                error_message="HEYGEN_API_KEY nu este configurat"
            )
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                
                async with session.get(
                    f"{self.base_url}/video/{video_id}",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        return HeyGenVideoResponse(
                            success=True,
                            video_id=video_id,
                            video_url=data.get("video_url"),
                            thumbnail_url=data.get("thumbnail_url"),
                            status=data.get("status"),
                            created_at=datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else None,
                            duration=data.get("duration")
                        )
                    else:
                        error_text = await response.text()
                        return HeyGenVideoResponse(
                            success=False,
                            error_message=f"API Error {response.status}: {error_text}"
                        )
                        
        except Exception as e:
            logger.error(f"Eroare la verificarea statusului video: {str(e)}")
            return HeyGenVideoResponse(
                success=False,
                error_message=f"Eroare la verificarea statusului: {str(e)}"
            )
    
    async def download_video(self, video_url: str, output_path: str) -> bool:
        """
        Descarcă un video generat
        
        Args:
            video_url: URL-ul video-ului
            output_path: Calea unde să salveze video-ul
            
        Returns:
            True dacă descărcarea a reușit
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url) as response:
                    if response.status == 200:
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        
                        with open(output_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        
                        logger.info(f"Video HeyGen descărcat cu succes: {output_path}")
                        return True
                    else:
                        logger.error(f"Eroare la descărcarea video: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Eroare la descărcarea video: {str(e)}")
            return False
    
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Returnează lista de voci disponibile
        
        Returns:
            Lista cu voci disponibile
        """
        if not self.api_key:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                
                async with session.get(
                    f"{self.base_url}/voices",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return data.get("voices", [])
                    else:
                        logger.error(f"Eroare la obținerea vocilor: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Eroare la obținerea vocilor: {str(e)}")
            return []
    
    async def get_available_avatars(self) -> List[Dict[str, Any]]:
        """
        Returnează lista de avatare disponibile
        
        Returns:
            Lista cu avatare disponibile
        """
        if not self.api_key:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                
                async with session.get(
                    f"{self.base_url}/avatars",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return data.get("avatars", [])
                    else:
                        logger.error(f"Eroare la obținerea avatarurilor: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Eroare la obținerea avatarurilor: {str(e)}")
            return []
    
    def estimate_cost(self, request: HeyGenVideoRequest) -> float:
        """
        Estimează costul generării video
        
        Args:
            request: Parametrii pentru generarea video
            
        Returns:
            Costul estimat în dolari
        """
        # Prețuri HeyGen (exemple - trebuie actualizate cu prețurile reale)
        base_cost_per_second = 0.03  # $0.03 per secundă
        
        # Factor de complexitate bazat pe stil
        style_multipliers = {
            HeyGenVideoStyle.REALISTIC: 1.0,
            HeyGenVideoStyle.ANIMATED: 1.3,
            HeyGenVideoStyle.CARTOON: 0.9,
            HeyGenVideoStyle.DOCUMENTARY: 1.1,
            HeyGenVideoStyle.PRESENTATION: 0.8
        }
        
        # Factor bazat pe calitate
        quality_multipliers = {
            HeyGenVideoQuality.LOW: 0.5,
            HeyGenVideoQuality.MEDIUM: 0.8,
            HeyGenVideoQuality.HIGH: 1.0,
            HeyGenVideoQuality.ULTRA: 1.5
        }
        
        # Estimează durata pe baza scriptului (aproximativ 150 cuvinte per minut)
        word_count = len(request.script.split())
        estimated_duration = max(1, word_count / 150 * 60)  # în secunde
        
        base_cost = estimated_duration * base_cost_per_second
        style_cost = base_cost * style_multipliers.get(request.style, 1.0)
        final_cost = style_cost * quality_multipliers.get(request.quality, 1.0)
        
        # Adaugă cost pentru background music
        if request.background_music:
            final_cost += 0.05
        
        return round(final_cost, 2)
    
    def get_supported_formats(self) -> List[str]:
        """Returnează formatele de video suportate"""
        return ["mp4", "webm"]
    
    def get_max_duration(self) -> int:
        """Returnează durata maximă suportată în secunde"""
        return 600  # HeyGen suportă până la 10 minute
    
    def get_max_resolution(self) -> Dict[str, int]:
        """Returnează rezoluția maximă suportată"""
        return {
            "width": 1920,
            "height": 1080
        }
    
    def get_supported_languages(self) -> List[str]:
        """Returnează limbile suportate"""
        return ["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar", "hi"]

# Singleton instance
_heygen_service = None

def get_heygen_service() -> HeyGenService:
    """Returnează instanța singleton a HeyGenService"""
    global _heygen_service
    if _heygen_service is None:
        _heygen_service = HeyGenService()
    return _heygen_service

# Funcții helper pentru integrare rapidă
async def generate_video_async(script: str, style: str = "realistic", quality: str = "high") -> HeyGenVideoResponse:
    """
    Funcție helper pentru generarea rapidă a unui video
    
    Args:
        script: Scriptul pentru generarea video
        style: Stilul video-ului
        quality: Calitatea video-ului
        
    Returns:
        HeyGenVideoResponse cu rezultatul
    """
    service = get_heygen_service()
    request = HeyGenVideoRequest(
        script=script,
        style=HeyGenVideoStyle(style),
        quality=HeyGenVideoQuality(quality)
    )
    return await service.generate_video(request)

def estimate_video_cost(script: str, style: str = "realistic", quality: str = "high") -> float:
    """
    Funcție helper pentru estimarea costului unui video
    
    Args:
        script: Scriptul pentru generarea video
        style: Stilul video-ului
        quality: Calitatea video-ului
        
    Returns:
        Costul estimat în dolari
    """
    service = get_heygen_service()
    request = HeyGenVideoRequest(
        script=script,
        style=HeyGenVideoStyle(style),
        quality=HeyGenVideoQuality(quality)
    )
    return service.estimate_cost(request)
