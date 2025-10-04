# services/api/app/services/metadata_probe.py
"""
Video metadata extraction using ffprobe.
SRP: Metadata extraction only, no business logic.
"""
import os
import json
import subprocess
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MetadataProbe:
    """Service for extracting video metadata using ffprobe."""

    def __init__(self):
        """Initialize metadata probe."""
        logger.info("✅ Metadata probe initialized")

    def get_video_metadata(self, video_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract comprehensive metadata from video file.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video metadata or None if failed
        """
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return None

        try:
            # Get format information
            format_cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", video_path
            ]

            format_result = subprocess.run(format_cmd, capture_output=True, text=True, check=True)
            format_data = json.loads(format_result.stdout)

            # Get stream information
            streams_cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_streams", video_path
            ]

            streams_result = subprocess.run(streams_cmd, capture_output=True, text=True, check=True)
            streams_data = json.loads(streams_result.stdout)

            # Parse metadata
            metadata = self._parse_metadata(format_data, streams_data)

            logger.info(f"Extracted metadata for {video_path}: {metadata}")
            return metadata

        except subprocess.CalledProcessError as e:
            logger.error(f"ffprobe failed for {video_path}: {e.stderr}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse ffprobe output for {video_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Metadata extraction error for {video_path}: {e}")
            return None

    def _parse_metadata(self, format_data: Dict[str, Any], streams_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse ffprobe output into structured metadata."""
        format_info = format_data.get("format", {})
        streams = streams_data.get("streams", [])

        # Find video and audio streams
        video_stream = None
        audio_stream = None

        for stream in streams:
            if stream.get("codec_type") == "video":
                video_stream = stream
            elif stream.get("codec_type") == "audio":
                audio_stream = stream

        metadata = {
            "duration": float(format_info.get("duration", 0)),
            "size": int(format_info.get("size", 0)),
            "bitrate": int(format_info.get("bit_rate", 0)),
            "format": format_info.get("format_name", ""),
            "video": {},
            "audio": {}
        }

        # Video metadata
        if video_stream:
            metadata["video"] = {
                "codec": video_stream.get("codec_name", ""),
                "width": video_stream.get("width", 0),
                "height": video_stream.get("height", 0),
                "fps": self._parse_fps(video_stream.get("r_frame_rate", "0/0")),
                "bitrate": video_stream.get("bit_rate", 0),
                "pix_fmt": video_stream.get("pix_fmt", ""),
                "profile": video_stream.get("profile", ""),
                "level": video_stream.get("level", 0)
            }

        # Audio metadata
        if audio_stream:
            metadata["audio"] = {
                "codec": audio_stream.get("codec_name", ""),
                "sample_rate": audio_stream.get("sample_rate", 0),
                "channels": audio_stream.get("channels", 0),
                "bitrate": audio_stream.get("bit_rate", 0),
                "channel_layout": audio_stream.get("channel_layout", "")
            }

        return metadata

    def _parse_fps(self, fps_string: str) -> float:
        """Parse FPS string (e.g., '25/1') to float."""
        try:
            if '/' in fps_string:
                num, den = fps_string.split('/')
                return float(num) / float(den)
            else:
                return float(fps_string)
        except:
            return 25.0  # Default fallback

    def get_basic_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get basic video information (duration, size, dimensions).

        Args:
            video_path: Path to video file

        Returns:
            Basic video information dictionary
        """
        metadata = self.get_video_metadata(video_path)

        if not metadata:
            return {}

        return {
            "duration": metadata["duration"],
            "size": metadata["size"],
            "width": metadata["video"].get("width", 0),
            "height": metadata["video"].get("height", 0),
            "fps": metadata["video"].get("fps", 25.0),
            "bitrate": metadata.get("bitrate", 0)
        }

    def validate_video_file(self, video_path: str) -> Dict[str, Any]:
        """
        Validate video file and return detailed information.

        Args:
            video_path: Path to video file

        Returns:
            Validation result with metadata or error info
        """
        result = {
            "valid": False,
            "error": None,
            "metadata": None
        }

        try:
            metadata = self.get_video_metadata(video_path)

            if metadata:
                result["valid"] = True
                result["metadata"] = metadata

                # Basic validation checks
                if metadata["duration"] <= 0:
                    result["error"] = "Invalid video duration"
                    result["valid"] = False

                if metadata["video"].get("width", 0) <= 0 or metadata["video"].get("height", 0) <= 0:
                    result["error"] = "Invalid video dimensions"
                    result["valid"] = False

            else:
                result["error"] = "Failed to extract metadata"

        except Exception as e:
            result["error"] = f"Validation error: {str(e)}"

        return result

# Global instance
_metadata_probe = None

def get_metadata_probe() -> MetadataProbe:
    """Get or create global metadata probe instance."""
    global _metadata_probe
    if _metadata_probe is None:
        _metadata_probe = MetadataProbe()
    return _metadata_probe