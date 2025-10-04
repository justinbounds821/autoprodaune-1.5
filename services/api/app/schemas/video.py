# services/api/app/schemas/video.py
from pydantic import BaseModel, field_validator
from typing import Literal, Optional

class ManoleGenerateRequest(BaseModel):
    topic: str
    duration_seconds: int
    resolution: Literal["720p", "1080p", "4k"] = "1080p"
    bg_type: Literal["color", "image"] = "color"
    bg_value: str
    voice_mode: str = "romanian_tts"
    lipsync: bool = False
    subtitles: bool = True

    @field_validator("resolution")
    @classmethod
    def _res(cls, v: str) -> str:
        allowed = {"720p", "1080p", "4k"}
        if v not in allowed:
            raise ValueError(f"resolution must be one of {allowed}")
        return v

class VideoGenerateRequest(BaseModel):
    template: str
    text: str
    duration: int = 30
    resolution: Literal["720p", "1080p", "4k"] = "1080p"
    
    @field_validator("resolution")
    @classmethod
    def _res(cls, v: str) -> str:
        allowed = {"720p", "1080p", "4k"}
        if v not in allowed:
            raise ValueError(f"resolution must be one of {allowed}")
        return v

class RetryRequest(BaseModel):
    job_id: str

class JobStatus:
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
