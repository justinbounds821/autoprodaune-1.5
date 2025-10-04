"""
Wrapper compat pentru vechiul `video_processor.py`.
Păstrează API-ul existent cu aceeași interfață.
"""
from .video.processor import VideoProcessor
from .video.models import VideoQuality, VideoFormat, VideoProcessingOptions, VideoInfo, VideoProcessingError

# Instanța globală a Video Processor-ului
video_processor = VideoProcessor()

def get_video_processor() -> VideoProcessor:
    """
    Obține instanța globală a Video Processor-ului.
    
    Returns:
        VideoProcessor: Instanța Video Processor-ului
    """
    return video_processor

__all__ = [
    "VideoProcessor",
    "VideoQuality", 
    "VideoFormat",
    "VideoProcessingOptions",
    "VideoInfo",
    "VideoProcessingError",
    "video_processor",
    "get_video_processor",
]
