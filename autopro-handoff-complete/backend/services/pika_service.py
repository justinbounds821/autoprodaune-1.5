"""
Pika Service - Serviciu pentru generarea de videoclipuri AI folosind Pika API
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

class VideoStyle(Enum):
    """Stiluri de video suportate de Pika"""
    ANIME = "anime"
    REALISTIC = "realistic"
    CARTOON = "cartoon"
    CINEMATIC = "cinematic"
    DOCUMENTARY = "documentary"

class VideoAspectRatio(Enum):
    """Rapoarte de aspect suportate"""
    SQUARE = "1:1"
    LANDSCAPE = "16:9"
    PORTRAIT = "9:16"
    WIDE = "21:9"

@dataclass
class PikaVideoRequest:
    """Request pentru generarea unui video Pika"""
    prompt: str
    style: VideoStyle = VideoStyle.CINEMATIC
    aspect_ratio: VideoAspectRatio = VideoAspectRatio.LANDSCAPE
    duration: int = 5  # secunde
    seed: Optional[int] = None
    negative_prompt: Optional[str] = None
    guidance_scale: float = 7.5
    num_inference_steps: int = 20

@dataclass
class PikaVideoResponse:
    """Response de la Pika API"""
    success: bool
    video_id: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    status: str = "pending"
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None

class PikaService:
    """Serviciu pentru integrarea cu Pika API"""
    
    def __init__(self):
        self.api_key = os.getenv("PIKA_API_KEY")
        self.base_url = os.getenv("PIKA_BASE_URL", "https://api.pika.art/v1")
        self.timeout = int(os.getenv("PIKA_TIMEOUT", "300"))  # 5 minute
        self.max_retries = int(os.getenv("PIKA_MAX_RETRIES", "3"))
        
        if not self.api_key:
            logger.warning("PIKA_API_KEY nu este configurat. Serviciul va funcționa în mod limitat.")
    
    async def generate_video(self, request: PikaVideoRequest) -> PikaVideoResponse:
        """
        Generează un video folosind Pika API
        
        Args:
            request: Parametrii pentru generarea video
            
        Returns:
            PikaVideoResponse cu rezultatul generării
        """
        if not self.api_key:
            return PikaVideoResponse(
                success=False,
                error_message="PIKA_API_KEY nu este configurat"
            )
        
        try:
            # Pregătește payload-ul pentru API
            payload = {
                "prompt": request.prompt,
                "style": request.style.value,
                "aspect_ratio": request.aspect_ratio.value,
                "duration": request.duration,
                "guidance_scale": request.guidance_scale,
                "num_inference_steps": request.num_inference_steps
            }
            
            if request.seed:
                payload["seed"] = request.seed
            
            if request.negative_prompt:
                payload["negative_prompt"] = request.negative_prompt
            
            # Face cererea către Pika API
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                async with session.post(
                    f"{self.base_url}/generate",
                    json=payload,
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        return PikaVideoResponse(
                            success=True,
                            video_id=data.get("id"),
                            status=data.get("status", "processing"),
                            created_at=datetime.now(),
                            estimated_completion=datetime.now() if data.get("estimated_completion") else None
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"Eroare Pika API: {response.status} - {error_text}")
                        
                        return PikaVideoResponse(
                            success=False,
                            error_message=f"API Error {response.status}: {error_text}"
                        )
                        
        except asyncio.TimeoutError:
            logger.error("Timeout la generarea video Pika")
            return PikaVideoResponse(
                success=False,
                error_message="Timeout la generarea video"
            )
        except Exception as e:
            logger.error(f"Eroare la generarea video Pika: {str(e)}")
            return PikaVideoResponse(
                success=False,
                error_message=f"Eroare internă: {str(e)}"
            )
    
    async def get_video_status(self, video_id: str) -> PikaVideoResponse:
        """
        Verifică statusul unui video în generare
        
        Args:
            video_id: ID-ul video-ului
            
        Returns:
            PikaVideoResponse cu statusul actual
        """
        if not self.api_key:
            return PikaVideoResponse(
                success=False,
                error_message="PIKA_API_KEY nu este configurat"
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
                        
                        return PikaVideoResponse(
                            success=True,
                            video_id=video_id,
                            video_url=data.get("video_url"),
                            thumbnail_url=data.get("thumbnail_url"),
                            status=data.get("status"),
                            created_at=datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else None
                        )
                    else:
                        error_text = await response.text()
                        return PikaVideoResponse(
                            success=False,
                            error_message=f"API Error {response.status}: {error_text}"
                        )
                        
        except Exception as e:
            logger.error(f"Eroare la verificarea statusului video: {str(e)}")
            return PikaVideoResponse(
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
                        
                        logger.info(f"Video descărcat cu succes: {output_path}")
                        return True
                    else:
                        logger.error(f"Eroare la descărcarea video: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Eroare la descărcarea video: {str(e)}")
            return False
    
    def estimate_cost(self, request: PikaVideoRequest) -> float:
        """
        Estimează costul generării video
        
        Args:
            request: Parametrii pentru generarea video
            
        Returns:
            Costul estimat în dolari
        """
        # Prețuri Pika (exemple - trebuie actualizate cu prețurile reale)
        base_cost_per_second = 0.05  # $0.05 per secundă
        
        # Factor de complexitate bazat pe stil
        style_multipliers = {
            VideoStyle.ANIME: 1.0,
            VideoStyle.REALISTIC: 1.5,
            VideoStyle.CARTOON: 0.8,
            VideoStyle.CINEMATIC: 1.3,
            VideoStyle.DOCUMENTARY: 1.1
        }
        
        # Factor bazat pe raportul de aspect
        aspect_multipliers = {
            VideoAspectRatio.SQUARE: 1.0,
            VideoAspectRatio.LANDSCAPE: 1.2,
            VideoAspectRatio.PORTRAIT: 1.1,
            VideoAspectRatio.WIDE: 1.4
        }
        
        base_cost = request.duration * base_cost_per_second
        style_cost = base_cost * style_multipliers.get(request.style, 1.0)
        final_cost = style_cost * aspect_multipliers.get(request.aspect_ratio, 1.0)
        
        return round(final_cost, 2)
    
    def get_supported_formats(self) -> List[str]:
        """Returnează formatele de video suportate"""
        return ["mp4", "mov", "avi", "webm"]
    
    def get_max_duration(self) -> int:
        """Returnează durata maximă suportată în secunde"""
        return 30  # Pika suportă până la 30 secunde
    
    def get_max_resolution(self) -> Dict[str, int]:
        """Returnează rezoluția maximă suportată"""
        return {
            "width": 1920,
            "height": 1080
        }

# Singleton instance
_pika_service = None

def get_pika_service() -> PikaService:
    """Returnează instanța singleton a PikaService"""
    global _pika_service
    if _pika_service is None:
        _pika_service = PikaService()
    return _pika_service

# Funcții helper pentru integrare rapidă
async def generate_video_async(prompt: str, style: str = "cinematic", duration: int = 5) -> PikaVideoResponse:
    """
    Funcție helper pentru generarea rapidă a unui video
    
    Args:
        prompt: Textul pentru generarea video
        style: Stilul video-ului
        duration: Durata în secunde
        
    Returns:
        PikaVideoResponse cu rezultatul
    """
    service = get_pika_service()
    request = PikaVideoRequest(
        prompt=prompt,
        style=VideoStyle(style),
        duration=duration
    )
    return await service.generate_video(request)

def estimate_video_cost(prompt: str, style: str = "cinematic", duration: int = 5) -> float:
    """
    Funcție helper pentru estimarea costului unui video
    
    Args:
        prompt: Textul pentru generarea video
        style: Stilul video-ului
        duration: Durata în secunde
        
    Returns:
        Costul estimat în dolari
    """
    service = get_pika_service()
    request = PikaVideoRequest(
        prompt=prompt,
        style=VideoStyle(style),
        duration=duration
    )
    return service.estimate_cost(request)
