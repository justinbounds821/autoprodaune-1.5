# services/api/app/services/thumbnailer.py
"""
Video thumbnail generator using FFmpeg.
SRP: Thumbnail generation only, no business logic.
"""
import os
import tempfile
import subprocess
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class Thumbnailer:
    """Service for generating video thumbnails."""

    def __init__(self):
        """Initialize thumbnailer."""
        self.thumbnail_size = "320x180"  # Standard thumbnail size
        self.thumbnail_quality = 85  # JPEG quality

        logger.info("✅ Thumbnailer initialized")

    def generate_thumbnail(self, video_path: str, output_path: str = None, timestamp: float = 1.0) -> Optional[str]:
        """
        Generate thumbnail from video at specified timestamp.

        Args:
            video_path: Path to input video file
            output_path: Path for output thumbnail (optional, auto-generated if None)
            timestamp: Timestamp in seconds for thumbnail (default: 1 second)

        Returns:
            Path to generated thumbnail or None if failed
        """
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return None

        if not output_path:
            # Generate output path
            output_path = video_path.replace('.mp4', '_thumb.jpg')

        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # FFmpeg command for thumbnail generation
            cmd = [
                "ffmpeg", "-y", "-loglevel", "error",
                "-ss", str(timestamp),  # Seek to timestamp
                "-i", video_path,       # Input video
                "-frames:v", "1",       # Extract 1 frame
                "-vf", f"scale=iw*min({self.thumbnail_size.split('x')[0]}/iw\\,{self.thumbnail_size.split('x')[1]}/ih):ih*min({self.thumbnail_size.split('x')[0]}/iw\\,{self.thumbnail_size.split('x')[1]}/ih):force_original_aspect_ratio=decrease",
                "-q:v", str(self.thumbnail_quality),  # JPEG quality
                output_path
            ]

            logger.info(f"Generating thumbnail: {video_path} -> {output_path}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"✅ Thumbnail generated successfully: {output_path}")
                return output_path
            else:
                logger.error(f"Thumbnail generation failed - no output file")
                return None

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg thumbnail generation failed: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"Thumbnail generation error: {e}")
            return None

    def generate_multiple_thumbnails(self, video_path: str, timestamps: list, output_dir: str = None) -> list:
        """
        Generate multiple thumbnails at different timestamps.

        Args:
            video_path: Path to input video file
            timestamps: List of timestamps in seconds
            output_dir: Directory for output thumbnails (optional)

        Returns:
            List of generated thumbnail paths
        """
        if not output_dir:
            output_dir = os.path.dirname(video_path)

        generated_thumbnails = []

        for i, timestamp in enumerate(timestamps):
            output_path = os.path.join(output_dir, f"thumb_{i"02d"}_{timestamp}s.jpg")

            thumbnail_path = self.generate_thumbnail(video_path, output_path, timestamp)
            if thumbnail_path:
                generated_thumbnails.append(thumbnail_path)

        logger.info(f"Generated {len(generated_thumbnails)} thumbnails for {video_path}")
        return generated_thumbnails

    def get_video_duration(self, video_path: str) -> Optional[float]:
        """
        Get video duration using ffprobe.

        Args:
            video_path: Path to video file

        Returns:
            Duration in seconds or None if failed
        """
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", video_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            import json
            data = json.loads(result.stdout)
            duration = float(data.get("format", {}).get("duration", 0))

            return duration

        except Exception as e:
            logger.error(f"Failed to get video duration for {video_path}: {e}")
            return None

    def generate_smart_thumbnail(self, video_path: str, output_path: str = None) -> Optional[str]:
        """
        Generate smart thumbnail by analyzing video content.

        Args:
            video_path: Path to input video file
            output_path: Path for output thumbnail (optional)

        Returns:
            Path to generated thumbnail or None if failed
        """
        # For now, use the 1-second mark as a simple smart thumbnail
        # In a more advanced implementation, this could analyze scenes for best frame
        return self.generate_thumbnail(video_path, output_path, timestamp=1.0)

# Global instance
_thumbnailer = None

def get_thumbnailer() -> Thumbnailer:
    """Get or create global thumbnailer instance."""
    global _thumbnailer
    if _thumbnailer is None:
        _thumbnailer = Thumbnailer()
    return _thumbnailer