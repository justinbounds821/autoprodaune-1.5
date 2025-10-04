# services/api/app/services/compositor_ffmpeg.py
"""
FFmpeg-based video compositor for internal video engine.
SRP: Video composition only, no business logic.
"""
import os
import json
import tempfile
import subprocess
import logging
from typing import Dict, Any, List, Optional
import uuid

logger = logging.getLogger(__name__)

class FFmpegCompositor:
    """FFmpeg-based video compositor for creating final videos."""

    def __init__(self):
        """Initialize compositor with configuration."""
        self.fps = int(os.getenv("VIDEO_ENGINE_FPS", "25"))
        self.canvas = os.getenv("VIDEO_ENGINE_CANVAS", "1280x720")
        self.preset = os.getenv("VIDEO_ENGINE_PRESET", "medium")

        # Parse canvas dimensions
        try:
            self.width, self.height = map(int, self.canvas.split('x'))
        except:
            self.width, self.height = 1280, 720
            logger.warning(f"Invalid canvas format '{self.canvas}', using 1280x720")

        # Preset configurations
        self.preset_configs = {
            "low": {"bitrate": "1000k", "profile": "baseline"},
            "medium": {"bitrate": "2500k", "profile": "main"},
            "high": {"bitrate": "5000k", "profile": "high"}
        }

        logger.info(f"✅ FFmpeg compositor initialized: {self.canvas}@{self.fps}fps, preset={self.preset}")

    def _get_audio_filter(self, audio_path: str) -> str:
        """Generate audio filter for FFmpeg."""
        return f" -i {audio_path} -c:a aac -b:a 128k"

    def _get_video_filter(self, timeline: Dict[str, Any]) -> str:
        """Generate video filter complex for FFmpeg."""
        layers = timeline.get("layers", [])
        filters = []

        # Background layer (always first)
        bg_layer = next((l for l in layers if l.get("type") == "bg"), None)
        if bg_layer:
            bg_filter = self._get_bg_filter(bg_layer)
            if bg_filter:
                filters.append(bg_filter)

        # Avatar layer
        avatar_layer = next((l for l in layers if l.get("type") == "video"), None)
        if avatar_layer:
            avatar_filter = self._get_avatar_filter(avatar_layer)
            if avatar_filter:
                filters.append(avatar_filter)

        # Image overlay
        image_layer = next((l for l in layers if l.get("type") == "image"), None)
        if image_layer:
            image_filter = self._get_image_filter(image_layer)
            if image_filter:
                filters.append(image_filter)

        # Captions layer
        captions_layer = next((l for l in layers if l.get("type") == "captions"), None)
        if captions_layer:
            captions_filter = self._get_captions_filter(captions_layer)
            if captions_filter:
                filters.append(captions_filter)

        # Text overlay
        text_layer = next((l for l in layers if l.get("type") == "text"), None)
        if text_layer:
            text_filter = self._get_text_filter(text_layer)
            if text_filter:
                filters.append(text_filter)

        return ";".join(filters) if filters else "null"

    def _get_bg_filter(self, layer: Dict[str, Any]) -> str:
        """Generate background filter."""
        params = layer.get("params", {})
        bg_type = params.get("type", "color")

        if bg_type == "color":
            color = params.get("color", "black")
            return f"color=c={color}:s={self.canvas}:r={self.fps}"
        elif bg_type == "image":
            image_path = params.get("image_path")
            if image_path and os.path.exists(image_path):
                return f"loop=loop=-1:size=1:start=0:input={image_path}"
        elif bg_type == "gradient":
            color1 = params.get("color1", "black")
            color2 = params.get("color2", "white")
            return f"geq=r=0:g='(X/Y)*255':b='(W-X)/W*255'"

        # Default black background
        return f"color=c=black:s={self.canvas}:r={self.fps}"

    def _get_avatar_filter(self, layer: Dict[str, Any]) -> str:
        """Generate avatar video filter."""
        params = layer.get("params", {})
        video_path = params.get("video_path")
        start_time = layer.get("in", 0)
        end_time = layer.get("out", 0)

        if not video_path or not os.path.exists(video_path):
            return None

        duration = end_time - start_time if end_time > start_time else 0

        # Scale and position avatar
        scale = params.get("scale", 0.8)
        x_pos = params.get("x", self.width * 0.1)
        y_pos = params.get("y", self.height * 0.1)

        return (
            f"[1:v]scale={int(self.width * scale)}:{int(self.height * scale)},"
            f"setpts=PTS-STARTPTS,"
            f"trim={start_time}:{end_time},"
            f"setpts=PTS-STARTPTS[avatar];"
        )

    def _get_image_filter(self, layer: Dict[str, Any]) -> str:
        """Generate image overlay filter."""
        params = layer.get("params", {})
        image_path = params.get("image_path")
        start_time = layer.get("in", 0)

        if not image_path or not os.path.exists(image_path):
            return None

        # Subtle zoom effect
        return (
            f"loop=loop=-1:size=1:start=0:input={image_path}[img];"
            f"[img]scale={self.width}:{self.height},"
            f"zoompan=z='min(1.05,max(1,zoom-0.001))':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'[img_scaled];"
        )

    def _get_captions_filter(self, layer: Dict[str, Any]) -> str:
        """Generate captions filter."""
        params = layer.get("params", {})
        script = params.get("script", "")
        style = params.get("style", "white_text")

        if not script:
            return None

        # Split script into sentences for timing
        sentences = [s.strip() for s in script.split('.') if s.strip()]
        if not sentences:
            return None

        # Simple ASS subtitle generation
        ass_content = self._generate_ass_subtitles(sentences)

        # Save ASS file temporarily
        ass_fd, ass_path = tempfile.mkstemp(suffix=".ass")
        os.close(ass_fd)

        try:
            with open(ass_path, 'w', encoding='utf-8') as f:
                f.write(ass_content)

            return f"subtitles={ass_path}"
        except Exception as e:
            logger.error(f"Failed to create ASS file: {e}")
            return None

    def _generate_ass_subtitles(self, sentences: List[str]) -> str:
        """Generate ASS subtitle format."""
        duration_per_sentence = 3.0  # seconds per sentence

        ass_content = """[Script Info]
Title: Generated Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,48,&Hffffff,&Hffffff,&H0,&H0,0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        current_time = 0.0
        for i, sentence in enumerate(sentences):
            start = current_time
            end = current_time + duration_per_sentence

            # Escape commas in text
            safe_text = sentence.replace(',', '\\,')
            ass_content += f"Dialogue: 0,{self._format_time(start)},{self._format_time(end)},Default,,0,0,0,,{safe_text}\n"

            current_time = end

        return ass_content

    def _format_time(self, seconds: float) -> str:
        """Format seconds as ASS time format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:02.1f}"

    def _get_text_filter(self, layer: Dict[str, Any]) -> str:
        """Generate text overlay filter."""
        params = layer.get("params", {})
        text = params.get("text", "")
        start_time = layer.get("in", 0)
        end_time = layer.get("out", 0)

        if not text:
            return None

        # Simple text overlay
        return (
            f"drawtext=text='{text}':x=(w-text_w)/2:y=h-th-50:"
            f"fontsize=48:fontcolor=white:borderw=2:bordercolor=black"
        )

    def compose_video(self, timeline: Dict[str, Any], audio_path: str, output_path: str) -> bool:
        """
        Compose video using FFmpeg.

        Args:
            timeline: Timeline configuration
            audio_path: Path to audio file
            output_path: Output video path

        Returns:
            True if composition successful, False otherwise
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Generate filter complex
            video_filter = self._get_video_filter(timeline)
            audio_filter = self._get_audio_filter(audio_path)

            # Get preset configuration
            preset_config = self.preset_configs.get(self.preset, self.preset_configs["medium"])

            # Build FFmpeg command
            cmd = [
                "ffmpeg", "-y", "-loglevel", "error"
            ]

            # Add inputs (background + audio)
            cmd.extend(["-f", "lavfi", "-i", video_filter])
            cmd.append("-i")
            cmd.append(audio_path)

            # Add avatar video if exists
            avatar_layer = next((l for l in timeline.get("layers", []) if l.get("type") == "video"), None)
            if avatar_layer and avatar_layer.get("params", {}).get("video_path"):
                cmd.extend(["-i", avatar_layer["params"]["video_path"]])

            # Add image if exists
            image_layer = next((l for l in timeline.get("layers", []) if l.get("type") == "image"), None)
            if image_layer and image_layer.get("params", {}).get("image_path"):
                cmd.extend(["-i", image_layer["params"]["image_path"]])

            # Video codec settings
            cmd.extend([
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-profile:v", preset_config["profile"],
                "-b:v", preset_config["bitrate"],
                "-r", str(self.fps),
                "-s", self.canvas,
                "-shortest",  # Match shortest input
                "-c:a", "aac",
                "-b:a", "128k",
                output_path
            ])

            logger.info(f"Running FFmpeg composition: {' '.join(cmd)}")

            # Execute FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"✅ Video composition completed: {output_path}")
                return True
            else:
                logger.error(f"FFmpeg completed but output file is missing or empty")
                return False

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg composition failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Video composition error: {e}")
            return False

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get video file information.

        Args:
            video_path: Path to video file

        Returns:
            Video information dictionary
        """
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", video_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            format_info = data.get("format", {})
            video_stream = None
            audio_stream = None

            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    video_stream = stream
                elif stream.get("codec_type") == "audio":
                    audio_stream = stream

            return {
                "duration": float(format_info.get("duration", 0)),
                "size": int(format_info.get("size", 0)),
                "bitrate": int(format_info.get("bit_rate", 0)),
                "video": {
                    "codec": video_stream.get("codec_name") if video_stream else None,
                    "width": video_stream.get("width") if video_stream else 0,
                    "height": video_stream.get("height") if video_stream else 0,
                    "fps": video_stream.get("r_frame_rate") if video_stream else "0/0"
                } if video_stream else {},
                "audio": {
                    "codec": audio_stream.get("codec_name") if audio_stream else None,
                    "sample_rate": audio_stream.get("sample_rate") if audio_stream else 0,
                    "channels": audio_stream.get("channels") if audio_stream else 0
                } if audio_stream else {}
            }

        except Exception as e:
            logger.error(f"Failed to get video info for {video_path}: {e}")
            return {}

# Global instance
_compositor = None

def get_compositor() -> FFmpegCompositor:
    """Get or create global compositor instance."""
    global _compositor
    if _compositor is None:
        _compositor = FFmpegCompositor()
    return _compositor