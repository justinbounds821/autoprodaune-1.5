# services/api/app/models/video_models.py
"""
Video models for internal video engine.
Compatible with existing HeyGen API contracts.
"""
from pydantic import BaseModel, Field, constr, AnyUrl
from typing import Optional, Literal, Dict, Any

# Quality and Style types
Quality = Literal["low", "medium", "high"]
Style = Literal["realistic", "studio", "cinematic"]

class GenerateVideoRequest(BaseModel):
    """
    Request model for internal video generation.
    Compatible with HeyGen API structure.
    """
    script: constr(strip_whitespace=True, min_length=10, max_length=1000)
    quality: Quality = "high"
    style: Style = "realistic"
    voice_id: Optional[str] = None
    
    # Lip-sync inputs (minimum one required for internal engine)
    avatar_image_url: Optional[AnyUrl] = None
    avatar_video_url: Optional[AnyUrl] = None
    
    # Additional parameters
    extra: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "script": "Bună! Sunt avocatul tău virtual AutoPro Daune.",
                "quality": "high",
                "style": "realistic",
                "voice_id": "Rachel",
                "avatar_image_url": "https://example.com/avatar.png",
                "extra": {}
            }
        }

class GenerateVideoResponse(BaseModel):
    """
    Response model for video generation job creation.
    Compatible with HeyGen API structure.
    """
    job_id: str
    provider: Literal["internal"] = "internal"
    status: Literal["queued"] = "queued"
    message: str = "Video generation queued successfully"
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "provider": "internal",
                "status": "queued",
                "message": "Video generation queued successfully"
            }
        }

class JobStatusResponse(BaseModel):
    """
    Response model for job status checking.
    Compatible with HeyGen API structure.
    """
    job_id: str
    status: Literal["queued", "processing", "completed", "failed"]
    video_url: Optional[str] = None
    error: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "completed",
                "video_url": "/api/video/video/heygen/download/123e4567-e89b-12d3-a456-426614174000",
                "error": None,
                "meta": {
                    "backend": "sadtalker",
                    "voice": "Rachel",
                    "processing_time": 45.2
                },
                "created_at": "2024-01-01T12:00:00Z",
                "completed_at": "2024-01-01T12:00:45Z"
            }
        }

class AvatarInfo(BaseModel):
    """
    Avatar information for compatibility with existing UI.
    """
    id: str
    label: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "internal_default",
                "label": "Internal High-Realism",
                "description": "High-quality avatar with realistic lip-sync",
                "thumbnail_url": "/api/assets/avatar_thumb.png"
            }
        }

class AvatarsResponse(BaseModel):
    """
    Response model for available avatars.
    Compatible with HeyGen API structure.
    """
    items: list[AvatarInfo]
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "internal_default",
                        "label": "Internal High-Realism",
                        "description": "High-quality avatar with realistic lip-sync"
                    }
                ]
            }
        }

# Job status constants (compatible with existing system)
class JobStatus:
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Internal engine specific models
class LipSyncBackend(BaseModel):
    """Configuration for lip-sync backend."""
    name: Literal["sadtalker", "wav2lip"]
    enabled: bool = True
    description: str

class TTSConfig(BaseModel):
    """Configuration for Text-to-Speech."""
    provider: Literal["elevenlabs", "local"]
    voice_id: Optional[str] = None
    fallback_enabled: bool = True

class VideoEngineConfig(BaseModel):
    """Configuration for internal video engine."""
    fps: int = Field(default=25, ge=15, le=60)
    canvas: str = Field(default="1280x720")
    background_image: Optional[str] = None
    lipsync_backend: LipSyncBackend
    tts_config: TTSConfig
