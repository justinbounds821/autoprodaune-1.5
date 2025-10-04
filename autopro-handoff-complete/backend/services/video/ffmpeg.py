"""
FFmpeg detection și execution helpers.
"""
import os
import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class FFmpegDetector:
    """Detector pentru disponibilitatea FFmpeg."""
    
    @staticmethod
    def is_ffmpeg_available() -> bool:
        """Verifică dacă FFmpeg este disponibil în sistem."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    @staticmethod
    def is_ffprobe_available() -> bool:
        """Verifică dacă FFprobe este disponibil în sistem."""
        try:
            result = subprocess.run(
                ["ffprobe", "-version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False


class FFmpegExecutor:
    """Executor pentru comenzi FFmpeg."""
    
    def __init__(self):
        self.ffmpeg_available = FFmpegDetector.is_ffmpeg_available()
        self.ffprobe_available = FFmpegDetector.is_ffprobe_available()
        
        if not self.ffmpeg_available:
            logger.warning("FFmpeg nu este disponibil")
        if not self.ffprobe_available:
            logger.warning("FFprobe nu este disponibil")
    
    def run_ffprobe(self, cmd: list, timeout: int = 30) -> subprocess.CompletedProcess:
        """Rulează o comandă FFprobe."""
        if not self.ffprobe_available:
            raise RuntimeError("FFprobe nu este disponibil")
        
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    
    def run_ffmpeg(self, cmd: list, timeout: int = 1800) -> subprocess.CompletedProcess:
        """Rulează o comandă FFmpeg."""
        if not self.ffmpeg_available:
            raise RuntimeError("FFmpeg nu este disponibil")
        
        logger.info(f"Rulez FFmpeg: {' '.join(cmd)}")
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    
    def is_available(self) -> bool:
        """Verifică dacă FFmpeg este disponibil."""
        return self.ffmpeg_available
