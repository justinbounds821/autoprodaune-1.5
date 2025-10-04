"""
Video Processor principal - orchestrează toate operațiunile video.
"""
import os
import tempfile
import time
import logging
from pathlib import Path
from typing import Optional
from .models import VideoInfo, VideoProcessingError, VideoFormat, VideoProcessingOptions
from .ffmpeg import FFmpegExecutor
from .optimizer import VideoOptimizer

logger = logging.getLogger(__name__)


class VideoProcessor:
    """
    Procesor principal pentru video-uri.
    
    Orchestrează toate operațiunile video folosind FFmpegExecutor și VideoOptimizer.
    """
    
    def __init__(self):
        """Inițializează Video Processor-ul."""
        self.temp_dir = Path(tempfile.gettempdir()) / "autopro_video_processing"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Inițializează componentele
        self.ffmpeg_executor = FFmpegExecutor()
        self.optimizer = VideoOptimizer(self.ffmpeg_executor)
        
        if not self.ffmpeg_executor.is_available():
            logger.warning("FFmpeg nu este disponibil. Procesarea video va fi limitată.")
    
    def is_ffmpeg_available(self) -> bool:
        """Verifică dacă FFmpeg este disponibil."""
        return self.ffmpeg_executor.is_available()
    
    def get_video_info(self, video_path: str) -> VideoInfo:
        """Obține informații despre un video."""
        if not os.path.exists(video_path):
            raise VideoProcessingError(f"Fișierul video nu există: {video_path}")
        
        if self.ffmpeg_executor.is_available():
            return self._get_video_info_with_ffprobe(video_path)
        else:
            return self._get_video_info_fallback(video_path)
    
    def _get_video_info_with_ffprobe(self, video_path: str) -> VideoInfo:
        """Obține informații video folosind FFprobe."""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            
            result = self.ffmpeg_executor.run_ffprobe(cmd)
            
            if result.returncode != 0:
                raise VideoProcessingError(f"Eroare la analiza video-ului: {result.stderr}")
            
            import json
            probe_data = json.loads(result.stdout)
            
            format_info = probe_data.get("format", {})
            duration = float(format_info.get("duration", 0))
            file_size = int(format_info.get("size", 0))
            bitrate = int(format_info.get("bit_rate", 0))
            
            video_stream = None
            audio_stream = None
            
            for stream in probe_data.get("streams", []):
                if stream.get("codec_type") == "video" and video_stream is None:
                    video_stream = stream
                elif stream.get("codec_type") == "audio" and audio_stream is None:
                    audio_stream = stream
            
            if not video_stream:
                raise VideoProcessingError("Nu s-a găsit stream video în fișier")
            
            width = int(video_stream.get("width", 0))
            height = int(video_stream.get("height", 0))
            fps = eval(video_stream.get("r_frame_rate", "30/1"))
            video_codec = video_stream.get("codec_name")
            
            has_audio = audio_stream is not None
            audio_codec = audio_stream.get("codec_name") if audio_stream else None
            
            file_format = Path(video_path).suffix.lower().lstrip('.')
            
            return VideoInfo(
                duration=duration,
                width=width,
                height=height,
                fps=fps,
                bitrate=bitrate,
                file_size=file_size,
                format=file_format,
                has_audio=has_audio,
                audio_codec=audio_codec,
                video_codec=video_codec
            )
            
        except Exception as e:
            logger.error(f"Eroare la obținerea informațiilor video: {e}")
            raise VideoProcessingError(f"Eroare la analiza video-ului: {str(e)}")
    
    def _get_video_info_fallback(self, video_path: str) -> VideoInfo:
        """Fallback pentru obținerea informațiilor video când FFmpeg nu este disponibil."""
        file_size = os.path.getsize(video_path)
        file_format = Path(video_path).suffix.lower().lstrip('.')
        
        return VideoInfo(
            duration=0.0,
            width=1920,
            height=1080,
            fps=30.0,
            bitrate=1000000,
            file_size=file_size,
            format=file_format,
            has_audio=True,
            audio_codec="unknown",
            video_codec="unknown"
        )
    
    def optimize_for_platform(
        self, 
        input_path: str, 
        platform: str, 
        output_path: Optional[str] = None,
        custom_options: Optional[VideoProcessingOptions] = None
    ) -> str:
        """Optimizează un video pentru o platformă specifică."""
        return self.optimizer.optimize_for_platform(input_path, platform, output_path, custom_options)
    
    def compress_video(
        self, 
        input_path: str, 
        target_size_mb: int,
        output_path: Optional[str] = None
    ) -> str:
        """Comprimă un video la o dimensiune țintă."""
        if not self.ffmpeg_executor.is_available():
            raise VideoProcessingError("FFmpeg nu este disponibil pentru comprimare")
        
        if not os.path.exists(input_path):
            raise VideoProcessingError(f"Fișierul video nu există: {input_path}")
        
        if not output_path:
            input_file = Path(input_path)
            timestamp = int(time.time())
            output_filename = f"{input_file.stem}_compressed_{timestamp}.mp4"
            output_path = str(self.temp_dir / output_filename)
        
        try:
            video_info = self.get_video_info(input_path)
            
            target_size_bytes = target_size_mb * 1024 * 1024
            duration_seconds = video_info.duration
            
            if duration_seconds <= 0:
                raise VideoProcessingError("Durata video-ului este invalidă")
            
            target_bitrate = int((target_size_bytes * 8) / duration_seconds)
            video_bitrate = int(target_bitrate * 0.8)
            audio_bitrate = int(target_bitrate * 0.2)
            
            video_bitrate_str = f"{video_bitrate // 1000}k"
            audio_bitrate_str = f"{audio_bitrate // 1000}k"
            
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-b:v", video_bitrate_str,
                "-b:a", audio_bitrate_str,
                "-y", output_path
            ]
            
            result = self.ffmpeg_executor.run_ffmpeg(cmd)
            
            if result.returncode != 0:
                raise VideoProcessingError(f"FFmpeg a eșuat la comprimare: {result.stderr}")
            
            if not os.path.exists(output_path):
                raise VideoProcessingError("Fișierul comprimat nu a fost creat")
            
            logger.info(f"Video comprimat cu succes: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Eroare la comprimarea video-ului: {e}")
            raise VideoProcessingError(f"Eroare la comprimarea video-ului: {str(e)}")
    
    def convert_format(
        self, 
        input_path: str, 
        target_format: VideoFormat,
        output_path: Optional[str] = None
    ) -> str:
        """Convertește un video într-un format diferit."""
        if not self.ffmpeg_executor.is_available():
            raise VideoProcessingError("FFmpeg nu este disponibil pentru conversie")
        
        if not os.path.exists(input_path):
            raise VideoProcessingError(f"Fișierul video nu există: {input_path}")
        
        if not output_path:
            input_file = Path(input_path)
            timestamp = int(time.time())
            output_filename = f"{input_file.stem}_converted_{timestamp}.{target_format.value}"
            output_path = str(self.temp_dir / output_filename)
        
        try:
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-c:v", "libx264",
                "-c:a", "aac",
                "-y", output_path
            ]
            
            result = self.ffmpeg_executor.run_ffmpeg(cmd)
            
            if result.returncode != 0:
                raise VideoProcessingError(f"FFmpeg a eșuat la conversie: {result.stderr}")
            
            if not os.path.exists(output_path):
                raise VideoProcessingError("Fișierul convertit nu a fost creat")
            
            logger.info(f"Video convertit cu succes: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Eroare la conversia video-ului: {e}")
            raise VideoProcessingError(f"Eroare la conversia video-ului: {str(e)}")
    
    def cleanup_temp_files(self) -> int:
        """Curăță fișierele temporare."""
        try:
            deleted_count = 0
            for file_path in self.temp_dir.iterdir():
                if file_path.is_file():
                    file_path.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Șterse {deleted_count} fișiere temporare")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Eroare la curățarea fișierelor temporare: {e}")
            return 0
    
    def get_platform_recommendations(self, platform: str) -> dict:
        """Obține recomandările pentru o platformă specifică."""
        return self.optimizer.get_platform_recommendations(platform)
