"""
Audio Enhancement Service - Improve audio quality in videos
Single Responsibility: Normalize loudness, reduce noise, enhance clarity
Safe-by-default: Disabled unless ENABLE_AUDIO_ENHANCE=true
"""
import os
import logging
from typing import Dict, Any, Optional
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioEnhanceService:
    """
    Enhance audio quality using FFmpeg filters.
    Normalizes loudness, reduces noise, improves clarity.
    """
    
    def __init__(self):
        self.enabled = os.getenv("ENABLE_AUDIO_ENHANCE", "false").lower() == "true"
        self.target_lufs = float(os.getenv("AUDIO_TARGET_LUFS", "-16"))  # EBU R128 standard
        self.noise_gate_db = float(os.getenv("AUDIO_NOISE_GATE_DB", "-45"))
        self.ffmpeg_available = self._check_ffmpeg()
        
        if not self.enabled:
            logger.info("⚠️ Audio enhancement disabled (ENABLE_AUDIO_ENHANCE=false)")
            return
        
        if not self.ffmpeg_available:
            logger.warning("⚠️ FFmpeg not available, audio enhancement disabled")
            self.enabled = False
        else:
            logger.info(f"✅ Audio enhancement enabled (LUFS={self.target_lufs})")
    
    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            subprocess.run(
                ["ffmpeg", "-version"], 
                capture_output=True, 
                timeout=5,
                check=True
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    async def enhance_audio(
        self, 
        input_path: str, 
        output_path: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Enhance audio in video file.
        Returns dict with output path and quality metrics.
        """
        if not self.enabled:
            logger.debug(f"Audio enhancement disabled for {input_path}")
            return None
        
        if output_path is None:
            path_obj = Path(input_path)
            output_path = str(path_obj.with_stem(f"{path_obj.stem}_enhanced"))
        
        try:
            # Build FFmpeg filter chain
            filters = self._build_filter_chain()
            
            # Run FFmpeg with audio filters
            cmd = [
                "ffmpeg", "-i", input_path,
                "-af", filters,
                "-c:v", "copy",  # Don't re-encode video
                "-c:a", "aac", "-b:a", "192k",  # High quality audio
                "-y",  # Overwrite output
                output_path
            ]
            
            logger.debug(f"Running FFmpeg: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes max
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg failed: {result.stderr}")
                return None
            
            # Analyze output quality
            quality_metrics = await self._analyze_audio_quality(output_path)
            
            return {
                "output_path": output_path,
                "enhanced": True,
                "filters_applied": filters,
                "quality_metrics": quality_metrics
            }
        
        except subprocess.TimeoutExpired:
            logger.error(f"Audio enhancement timed out for {input_path}")
            return None
        except Exception as e:
            logger.error(f"Audio enhancement failed: {e}")
            return None
    
    def _build_filter_chain(self) -> str:
        """Build FFmpeg audio filter chain"""
        filters = []
        
        # 1. Noise gate (remove background noise)
        filters.append(f"agate=threshold={self.noise_gate_db}dB:ratio=3:attack=5:release=50")
        
        # 2. High-pass filter (remove rumble)
        filters.append("highpass=f=80")
        
        # 3. De-esser (reduce sibilance)
        filters.append("deesser=i=0.25:m=2.0:f=6000:s=o")
        
        # 4. Compressor (dynamic range control)
        filters.append("acompressor=threshold=-20dB:ratio=4:attack=5:release=50")
        
        # 5. Loudness normalization (EBU R128)
        filters.append(f"loudnorm=I={self.target_lufs}:TP=-1.5:LRA=11")
        
        return ",".join(filters)
    
    async def _analyze_audio_quality(self, audio_path: str) -> Dict[str, Any]:
        """Analyze audio quality metrics"""
        try:
            # Get loudness info using ffmpeg
            cmd = [
                "ffmpeg", "-i", audio_path,
                "-af", "loudnorm=print_format=json",
                "-f", "null", "-"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse loudnorm output from stderr
            import json
            import re
            
            # Find JSON in stderr
            json_match = re.search(r'\{[^}]+\}', result.stderr)
            if json_match:
                metrics = json.loads(json_match.group())
                return {
                    "integrated_loudness": float(metrics.get("input_i", 0)),
                    "true_peak": float(metrics.get("input_tp", 0)),
                    "loudness_range": float(metrics.get("input_lra", 0)),
                    "threshold": float(metrics.get("input_thresh", 0))
                }
            
            return {"status": "analyzed", "details": "metrics_unavailable"}
        
        except Exception as e:
            logger.warning(f"Audio quality analysis failed: {e}")
            return {"status": "analysis_failed"}
    
    def get_health(self) -> Dict[str, Any]:
        """Health check for audio enhancement"""
        return {
            "enabled": self.enabled,
            "ffmpeg_available": self.ffmpeg_available,
            "target_lufs": self.target_lufs,
            "noise_gate_db": self.noise_gate_db
        }


# Singleton instance
_instance = None

def get_audio_enhancer() -> AudioEnhanceService:
    """Get or create AudioEnhanceService singleton"""
    global _instance
    if _instance is None:
        _instance = AudioEnhanceService()
    return _instance
