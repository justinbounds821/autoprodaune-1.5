"""
Video optimization și platform-specific processing.
"""
import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from .models import VideoProcessingOptions, VideoQuality, VideoFormat, VideoProcessingError
from .ffmpeg import FFmpegExecutor

logger = logging.getLogger(__name__)


class VideoOptimizer:
    """Optimizator pentru video-uri pe platforme specifice."""
    
    def __init__(self, ffmpeg_executor: FFmpegExecutor):
        self.ffmpeg = ffmpeg_executor
        self.platform_configs = self._get_platform_configs()
    
    def _get_platform_configs(self) -> Dict[str, VideoProcessingOptions]:
        """Returnează configurațiile pentru diferite platforme."""
        return {
            "tiktok": VideoProcessingOptions(
                quality=VideoQuality.HIGH,
                format=VideoFormat.MP4,
                max_duration=600,  # 10 minute
                max_size=287 * 1024 * 1024,  # 287MB
                target_resolution=(1080, 1920),  # 9:16 aspect ratio
                bitrate="2M",
                fps=30,
                audio_bitrate="128k"
            ),
            "instagram": VideoProcessingOptions(
                quality=VideoQuality.HIGH,
                format=VideoFormat.MP4,
                max_duration=60,  # 1 minut pentru feed
                max_size=100 * 1024 * 1024,  # 100MB
                target_resolution=(1080, 1080),  # 1:1 aspect ratio
                bitrate="1.5M",
                fps=30,
                audio_bitrate="128k"
            ),
            "youtube": VideoProcessingOptions(
                quality=VideoQuality.ULTRA,
                format=VideoFormat.MP4,
                max_duration=12 * 3600,  # 12 ore
                max_size=256 * 1024 * 1024 * 1024,  # 256GB
                target_resolution=(1920, 1080),  # 16:9 aspect ratio
                bitrate="5M",
                fps=30,
                audio_bitrate="192k"
            )
        }
    
    def optimize_for_platform(
        self, 
        input_path: str, 
        platform: str, 
        output_path: Optional[str] = None,
        custom_options: Optional[VideoProcessingOptions] = None
    ) -> str:
        """Optimizează un video pentru o platformă specifică."""
        if not os.path.exists(input_path):
            raise VideoProcessingError(f"Fișierul video nu există: {input_path}")
        
        if platform not in self.platform_configs:
            raise VideoProcessingError(f"Platforma {platform} nu este suportată")
        
        options = custom_options or self.platform_configs[platform]
        
        if not output_path:
            output_path = self._generate_output_path(input_path, platform)
        
        if self.ffmpeg.is_available():
            return self._process_with_ffmpeg(input_path, output_path, options)
        else:
            logger.warning("FFmpeg nu este disponibil. Copiez fișierul fără procesare.")
            import shutil
            shutil.copy2(input_path, output_path)
            return output_path
    
    def _generate_output_path(self, input_path: str, platform: str) -> str:
        """Generează o cale de ieșire pentru video-ul procesat."""
        input_file = Path(input_path)
        timestamp = int(time.time())
        output_filename = f"{input_file.stem}_{platform}_{timestamp}.mp4"
        temp_dir = Path(input_file.parent) / "processed"
        temp_dir.mkdir(exist_ok=True)
        return str(temp_dir / output_filename)
    
    def _process_with_ffmpeg(
        self, 
        input_path: str, 
        output_path: str, 
        options: VideoProcessingOptions
    ) -> str:
        """Procesează video-ul folosind FFmpeg."""
        cmd = ["ffmpeg", "-i", input_path]
        
        video_filters = []
        
        if options.target_resolution:
            width, height = options.target_resolution
            video_filters.append(f"scale={width}:{height}")
        
        if options.add_watermark and options.watermark_path:
            watermark_filter = self._get_watermark_filter(
                options.watermark_path, options.watermark_position
            )
            if watermark_filter:
                video_filters.append(watermark_filter)
        
        if video_filters:
            cmd.extend(["-vf", ",".join(video_filters)])
        
        if options.bitrate:
            cmd.extend(["-b:v", options.bitrate])
        
        if options.fps:
            cmd.extend(["-r", str(options.fps)])
        
        if options.remove_audio:
            cmd.append("-an")
        elif options.audio_bitrate:
            cmd.extend(["-b:a", options.audio_bitrate])
        
        if options.max_duration:
            cmd.extend(["-t", str(options.max_duration)])
        
        cmd.extend(["-y", output_path])
        
        result = self.ffmpeg.run_ffmpeg(cmd)
        
        if result.returncode != 0:
            raise VideoProcessingError(f"FFmpeg a eșuat: {result.stderr}")
        
        if not os.path.exists(output_path):
            raise VideoProcessingError("Fișierul de ieșire nu a fost creat")
        
        if options.max_size:
            file_size = os.path.getsize(output_path)
            if file_size > options.max_size:
                logger.warning(f"Fișierul procesat ({file_size} bytes) depășește limita ({options.max_size} bytes)")
        
        logger.info(f"Video procesat cu succes: {output_path}")
        return output_path
    
    def _get_watermark_filter(self, watermark_path: str, position: str) -> Optional[str]:
        """Generează filtrul FFmpeg pentru watermark."""
        if not os.path.exists(watermark_path):
            logger.warning(f"Fișierul watermark nu există: {watermark_path}")
            return None
        
        position_map = {
            "top-left": "10:10",
            "top-right": "W-w-10:10",
            "bottom-left": "10:H-h-10",
            "bottom-right": "W-w-10:H-h-10"
        }
        
        coordinates = position_map.get(position, "W-w-10:H-h-10")
        return f"movie={watermark_path}[watermark];[in][watermark]overlay={coordinates}[out]"
    
    def get_platform_recommendations(self, platform: str) -> Dict[str, Any]:
        """Obține recomandările pentru o platformă specifică."""
        if platform not in self.platform_configs:
            return {}
        
        config = self.platform_configs[platform]
        
        return {
            "quality": config.quality.value,
            "format": config.format.value,
            "max_duration": config.max_duration,
            "max_size_mb": config.max_size // (1024 * 1024) if config.max_size else None,
            "recommended_resolution": config.target_resolution,
            "recommended_bitrate": config.bitrate,
            "recommended_fps": config.fps,
            "audio_bitrate": config.audio_bitrate
        }
