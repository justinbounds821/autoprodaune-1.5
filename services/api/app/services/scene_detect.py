# services/api/app/services/scene_detect.py
"""
Scene detection service for video content analysis.
SRP: Scene detection only, no business logic.
"""
import os
import json
import logging
import tempfile
import subprocess
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class SceneDetector:
    """Service for detecting scene changes in videos."""

    def __init__(self):
        """Initialize scene detector."""
        self.enabled = os.getenv("AI_ENABLE_SCENE_DETECT", "false").lower() in ("1", "true", "yes")

        if not self.enabled:
            logger.info("Scene detection disabled")
            return

        logger.info("✅ Scene detector initialized")

    def detect_scenes(self, video_path: str) -> Dict[str, Any]:
        """
        Detect scene changes in video.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with scene detection results
        """
        if not self.enabled:
            logger.debug("Scene detection disabled, skipping")
            return {"enabled": False}

        try:
            logger.info(f"🎬 Detecting scenes in: {video_path}")

            # Method 1: Try PySceneDetect (more accurate)
            try:
                scenes = self._detect_scenes_pyscenedetect(video_path)
                if scenes:
                    return {
                        "enabled": True,
                        "success": True,
                        "method": "pyscenedetect",
                        "scenes": scenes,
                        "scene_count": len(scenes)
                    }
            except ImportError:
                logger.warning("PySceneDetect not available, falling back to FFmpeg")
            except Exception as e:
                logger.warning(f"PySceneDetect failed: {e}, falling back to FFmpeg")

            # Method 2: FFmpeg scene detection (fallback)
            scenes = self._detect_scenes_ffmpeg(video_path)

            return {
                "enabled": True,
                "success": True,
                "method": "ffmpeg",
                "scenes": scenes,
                "scene_count": len(scenes)
            }

        except Exception as e:
            logger.error(f"Scene detection failed for {video_path}: {e}")
            return {
                "enabled": True,
                "success": False,
                "error": str(e)
            }

    def _detect_scenes_pyscenedetect(self, video_path: str) -> Optional[List[Dict[str, Any]]]:
        """Detect scenes using PySceneDetect."""
        try:
            from scenedetect import detect, ContentDetector

            logger.info("Using PySceneDetect for scene detection")

            # Detect scenes using content detector (threshold can be adjusted)
            scenes = detect(video_path, ContentDetector(threshold=30.0))

            scene_data = []
            for i, scene in enumerate(scenes):
                scene_data.append({
                    "scene_id": i + 1,
                    "start_time": scene[0].get_seconds(),
                    "end_time": scene[1].get_seconds(),
                    "duration": scene[1].get_seconds() - scene[0].get_seconds()
                })

            logger.info(f"PySceneDetect found {len(scene_data)} scenes")
            return scene_data

        except ImportError:
            logger.warning("PySceneDetect not installed")
            return None
        except Exception as e:
            logger.error(f"PySceneDetect error: {e}")
            return None

    def _detect_scenes_ffmpeg(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect scenes using FFmpeg scene detection."""
        try:
            logger.info("Using FFmpeg for scene detection")

            # Use FFmpeg's scene detection filter
            cmd = [
                "ffmpeg", "-i", video_path,
                "-vf", "select='gt(scene,0.3)',metadata=print:file=-",
                "-f", "null", "-"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            # Parse scene change timestamps from output
            scenes = self._parse_ffmpeg_scene_output(result.stderr)

            if not scenes:
                # Fallback: use simple time-based detection
                logger.warning("FFmpeg scene detection found no scenes, using fallback method")
                scenes = self._fallback_scene_detection(video_path)

            logger.info(f"FFmpeg scene detection found {len(scenes)} scenes")
            return scenes

        except Exception as e:
            logger.error(f"FFmpeg scene detection error: {e}")
            return []

    def _parse_ffmpeg_scene_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse scene detection output from FFmpeg."""
        scenes = []
        scene_times = []

        try:
            lines = output.split('\n')
            for line in lines:
                if 'pts_time:' in line:
                    # Extract timestamp
                    parts = line.split('pts_time:')
                    if len(parts) > 1:
                        try:
                            timestamp = float(parts[1].split()[0])
                            scene_times.append(timestamp)
                        except:
                            continue

            # Convert timestamps to scene data
            for i, timestamp in enumerate(scene_times):
                start_time = timestamp
                end_time = scene_times[i + 1] if i + 1 < len(scene_times) else start_time + 5.0  # Assume 5s for last scene

                scenes.append({
                    "scene_id": i + 1,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": end_time - start_time
                })

        except Exception as e:
            logger.error(f"Failed to parse FFmpeg scene output: {e}")

        return scenes

    def _fallback_scene_detection(self, video_path: str) -> List[Dict[str, Any]]:
        """Fallback scene detection method."""
        try:
            # Get video duration
            cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", video_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)
            duration = float(data.get("format", {}).get("duration", 30))

            # Simple time-based scene detection (every 10 seconds)
            scenes = []
            for i in range(0, int(duration), 10):
                start_time = float(i)
                end_time = min(start_time + 10.0, duration)

                scenes.append({
                    "scene_id": len(scenes) + 1,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": end_time - start_time
                })

            logger.info(f"Fallback scene detection created {len(scenes)} scenes")
            return scenes

        except Exception as e:
            logger.error(f"Fallback scene detection failed: {e}")
            return []

    def analyze_scenes_for_content(self, video_path: str, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze scenes for content characteristics.

        Args:
            video_path: Path to video file
            scenes: List of scene data

        Returns:
            Content analysis results
        """
        try:
            content_analysis = {
                "total_scenes": len(scenes),
                "avg_scene_duration": sum(s["duration"] for s in scenes) / len(scenes) if scenes else 0,
                "scene_distribution": self._analyze_scene_distribution(scenes),
                "content_type": self._classify_content_type(scenes)
            }

            logger.info(f"Content analysis completed: {content_analysis}")
            return content_analysis

        except Exception as e:
            logger.error(f"Scene content analysis failed: {e}")
            return {"error": str(e)}

    def _analyze_scene_distribution(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze scene duration distribution."""
        if not scenes:
            return {}

        durations = [s["duration"] for s in scenes]

        return {
            "min_duration": min(durations),
            "max_duration": max(durations),
            "avg_duration": sum(durations) / len(durations),
            "short_scenes": len([d for d in durations if d < 3]),
            "long_scenes": len([d for d in durations if d > 15])
        }

    def _classify_content_type(self, scenes: List[Dict[str, Any]]) -> str:
        """Classify content type based on scene patterns."""
        if not scenes:
            return "unknown"

        avg_duration = sum(s["duration"] for s in scenes) / len(scenes)

        # Simple heuristics for content classification
        if avg_duration < 5:
            return "dynamic"  # Fast-paced content
        elif avg_duration > 20:
            return "static"   # Slow-paced, long scenes
        else:
            return "moderate" # Balanced content

# Global instance
_scene_detector = None

def get_scene_detector() -> SceneDetector:
    """Get or create global scene detector instance."""
    global _scene_detector
    if _scene_detector is None:
        _scene_detector = SceneDetector()
    return _scene_detector