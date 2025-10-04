# services/api/app/services/audio_enhance.py
"""
Audio enhancement service for quality improvement.
SRP: Audio processing only, no business logic.
"""
import os
import tempfile
import subprocess
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AudioEnhancer:
    """Service for enhancing audio quality."""

    def __init__(self):
        """Initialize audio enhancer."""
        self.enabled = True  # Always enabled for quality
        self.target_lufs = float(os.getenv("AUDIO_TARGET_LUFS", "-16"))
        self.noise_gate_db = float(os.getenv("AUDIO_NOISE_GATE_DB", "-45"))

        logger.info(f"✅ Audio enhancer initialized: LUFS={self.target_lufs}dB, gate={self.noise_gate_db}dB")

    def enhance_audio(self, input_path: str, output_path: str) -> bool:
        """
        Enhance audio quality with normalization and noise reduction.

        Args:
            input_path: Path to input audio file
            output_path: Path for enhanced output file

        Returns:
            True if enhancement successful, False otherwise
        """
        try:
            logger.info(f"🎵 Enhancing audio: {input_path} -> {output_path}")

            # Build FFmpeg command for audio enhancement
            cmd = [
                "ffmpeg", "-y", "-loglevel", "error",
                "-i", input_path,  # Input audio
                "-af", self._build_audio_filter(),  # Audio filters
                "-c:a", "aac",     # AAC codec
                "-b:a", "128k",    # Bitrate
                "-ar", "44100",    # Sample rate
                "-ac", "2",        # Stereo
                output_path
            ]

            logger.info(f"Running audio enhancement: {' '.join(cmd)}")

            # Execute FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"✅ Audio enhancement completed: {output_path}")
                return True
            else:
                logger.error("Audio enhancement failed - no output file")
                return False

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg audio enhancement failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Audio enhancement error: {e}")
            return False

    def _build_audio_filter(self) -> str:
        """Build FFmpeg audio filter chain."""
        filters = []

        # 1. Loudness normalization (LUFS)
        filters.append(f"loudnorm=I={self.target_lufs}:TP=-1.5:LRA=11")

        # 2. Noise gate for background noise reduction
        if self.noise_gate_db < -60:  # Only if threshold is reasonable
            filters.append(f"agate=threshold={self.noise_gate_db}dB:ratio=10:attack=20:release=250")

        # 3. Light de-noising (optional - can be aggressive)
        # filters.append("afftdn=nf=-40")

        return ",".join(filters)

    def get_audio_quality_score(self, audio_path: str) -> Dict[str, Any]:
        """
        Analyze audio quality and return score.

        Args:
            audio_path: Path to audio file

        Returns:
            Quality analysis results
        """
        try:
            # Use FFmpeg to analyze audio
            cmd = [
                "ffmpeg", "-i", audio_path,
                "-af", "loudnorm=print_format=json",
                "-f", "null", "-"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            # Parse loudness information from stderr
            loudness_info = self._parse_loudness_output(result.stderr)

            # Calculate quality score (0-1)
            quality_score = self._calculate_quality_score(loudness_info)

            return {
                "quality_score": quality_score,
                "loudness_info": loudness_info,
                "target_lufs": self.target_lufs,
                "noise_gate_db": self.noise_gate_db
            }

        except Exception as e:
            logger.error(f"Audio quality analysis failed: {e}")
            return {
                "quality_score": 0.0,
                "error": str(e)
            }

    def _parse_loudness_output(self, ffmpeg_output: str) -> Dict[str, Any]:
        """Parse loudness information from FFmpeg output."""
        loudness = {}

        try:
            # Look for loudness measurements in output
            lines = ffmpeg_output.split('\n')
            for line in lines:
                if 'input_i' in line or 'input_lra' in line or 'input_tp' in line:
                    # Parse key=value pairs
                    parts = line.strip().split()
                    for part in parts:
                        if '=' in part:
                            key, value = part.split('=', 1)
                            try:
                                loudness[key] = float(value)
                            except:
                                loudness[key] = value

        except Exception as e:
            logger.error(f"Failed to parse loudness output: {e}")

        return loudness

    def _calculate_quality_score(self, loudness_info: Dict[str, Any]) -> float:
        """Calculate audio quality score based on loudness metrics."""
        try:
            # Base score
            score = 0.5

            # LUFS target compliance (closer to target = higher score)
            input_i = loudness_info.get('input_i', -23)  # Default EBU R128 level
            lufs_diff = abs(input_i - self.target_lufs)
            if lufs_diff <= 2:
                score += 0.3
            elif lufs_diff <= 5:
                score += 0.2
            elif lufs_diff <= 10:
                score += 0.1

            # Dynamic range (LRA) - prefer reasonable dynamic range
            input_lra = loudness_info.get('input_lra', 8)
            if 5 <= input_lra <= 15:
                score += 0.2

            # Clip detection (no clipping = good)
            # This would need more complex analysis

            # Clamp score to 0-1 range
            return max(0.0, min(1.0, score))

        except Exception as e:
            logger.error(f"Quality score calculation failed: {e}")
            return 0.0

# Global instance
_audio_enhancer = None

def get_audio_enhancer() -> AudioEnhancer:
    """Get or create global audio enhancer instance."""
    global _audio_enhancer
    if _audio_enhancer is None:
        _audio_enhancer = AudioEnhancer()
    return _audio_enhancer