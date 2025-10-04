"""
Modele de date pentru Video Processor.
"""
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum


class VideoQuality(Enum):
    """Calitățile video disponibile."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


class VideoFormat(Enum):
    """Formatele video suportate."""
    MP4 = "mp4"
    MOV = "mov"
    AVI = "avi"
    WEBM = "webm"


@dataclass
class VideoProcessingOptions:
    """Opțiunile pentru procesarea video."""
    quality: VideoQuality = VideoQuality.MEDIUM
    format: VideoFormat = VideoFormat.MP4
    max_duration: Optional[float] = None  # în secunde
    max_size: Optional[int] = None  # în bytes
    target_resolution: Optional[Tuple[int, int]] = None  # (width, height)
    bitrate: Optional[str] = None  # ex: "1M", "2M"
    fps: Optional[int] = None  # frames per second
    audio_bitrate: Optional[str] = None  # ex: "128k", "192k"
    remove_audio: bool = False
    add_watermark: bool = False
    watermark_path: Optional[str] = None
    watermark_position: str = "bottom-right"  # top-left, top-right, bottom-left, bottom-right


@dataclass
class VideoInfo:
    """Informații despre un video."""
    duration: float
    width: int
    height: int
    fps: float
    bitrate: int
    file_size: int
    format: str
    has_audio: bool
    audio_codec: Optional[str] = None
    video_codec: Optional[str] = None


class VideoProcessingError(Exception):
    """Excepție pentru erori de procesare video."""
    pass
