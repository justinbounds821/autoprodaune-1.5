"""
Scene Detection Service - Identify scene cuts in videos
Single Responsibility: Detect scene boundaries for smart editing
Safe-by-default: Disabled unless ENABLE_SCENE_DETECT=true
"""
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SceneDetectService:
    """
    Detect scene changes in video for smart cutting/editing.
    Falls back to fixed intervals if detection unavailable.
    """
    
    def __init__(self):
        self.enabled = os.getenv("ENABLE_SCENE_DETECT", "false").lower() == "true"
        self.threshold = float(os.getenv("SCENE_DETECT_THRESHOLD", "30.0"))
        self.scenedetect_available = False
        
        if not self.enabled:
            logger.info("⚠️ Scene detection disabled (ENABLE_SCENE_DETECT=false)")
            return
        
        # Check if scenedetect is available
        try:
            from scenedetect import detect, ContentDetector
            self.scenedetect_available = True
            logger.info(f"✅ Scene detection enabled (threshold={self.threshold})")
        except ImportError:
            logger.warning("⚠️ scenedetect not installed, using fallback intervals")
            self.enabled = False
    
    async def detect_scenes(self, video_path: str) -> List[Dict[str, Any]]:
        """
        Detect scene boundaries in video.
        Returns list of scene markers with timestamps.
        """
        if not self.enabled or not self.scenedetect_available:
            return self._fallback_fixed_intervals(video_path)
        
        try:
            from scenedetect import detect, ContentDetector
            
            # Detect scenes using content-aware algorithm
            scene_list = detect(video_path, ContentDetector(threshold=self.threshold))
            
            scenes = []
            for i, (start_time, end_time) in enumerate(scene_list):
                scenes.append({
                    "scene_id": i + 1,
                    "start_seconds": start_time.get_seconds(),
                    "end_seconds": end_time.get_seconds(),
                    "duration": end_time.get_seconds() - start_time.get_seconds(),
                    "start_frame": start_time.get_frames(),
                    "end_frame": end_time.get_frames()
                })
            
            logger.info(f"Detected {len(scenes)} scenes in {video_path}")
            return scenes
        
        except Exception as e:
            logger.error(f"Scene detection failed for {video_path}: {e}")
            return self._fallback_fixed_intervals(video_path)
    
    def _fallback_fixed_intervals(self, video_path: str, interval: int = 10) -> List[Dict[str, Any]]:
        """Fallback: divide video into fixed-duration scenes"""
        try:
            # Get video duration using ffprobe
            import subprocess
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            duration = float(result.stdout.strip())
            
            # Create scenes at fixed intervals
            scenes = []
            for i in range(0, int(duration), interval):
                scenes.append({
                    "scene_id": len(scenes) + 1,
                    "start_seconds": i,
                    "end_seconds": min(i + interval, duration),
                    "duration": min(interval, duration - i),
                    "start_frame": i * 25,  # assume 25fps
                    "end_frame": min((i + interval) * 25, int(duration * 25))
                })
            
            logger.debug(f"Using fallback intervals: {len(scenes)} scenes")
            return scenes
        
        except Exception as e:
            logger.error(f"Fallback scene detection failed: {e}")
            return []
    
    def get_scene_summary(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from scene list"""
        if not scenes:
            return {"total_scenes": 0, "average_duration": 0, "shortest": 0, "longest": 0}
        
        durations = [s["duration"] for s in scenes]
        return {
            "total_scenes": len(scenes),
            "average_duration": sum(durations) / len(durations),
            "shortest": min(durations),
            "longest": max(durations),
            "total_duration": sum(durations)
        }
    
    def get_health(self) -> Dict[str, Any]:
        """Health check for scene detection"""
        return {
            "enabled": self.enabled,
            "threshold": self.threshold,
            "library_available": self.scenedetect_available
        }


# Singleton instance
_instance = None

def get_scene_detector() -> SceneDetectService:
    """Get or create SceneDetectService singleton"""
    global _instance
    if _instance is None:
        _instance = SceneDetectService()
    return _instance
