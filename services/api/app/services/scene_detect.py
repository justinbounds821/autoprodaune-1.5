# services/api/app/services/scene_detect.py
"""
Scene detection service.
SRP: Detect scene cuts in video content.
"""
from __future__ import annotations

import os
import subprocess
import logging
from typing import List

logger = logging.getLogger(__name__)


class SceneDetectService:
    """
    Scene detection service using FFmpeg.
    Detects scene changes in video files.
    """

    def __init__(self) -> None:
        """Initialize scene detection service."""
        self.enabled = True
        logger.debug("SceneDetectService initialized")

    def detect_scenes(self, video_path: str, threshold: float = 0.4) -> List[float]:
        """
        Detect scene cuts in video.
        
        Args:
            video_path: Path to video file
            threshold: Scene detection threshold (0.0-1.0)
            
        Returns:
            List of scene cut timestamps in seconds
        """
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return []
        
        try:
            # Use FFmpeg scene detection filter
            cmd = [
                "ffprobe",
                "-f", "lavfi",
                "-i", f"movie={video_path},select='gt(scene,{threshold})',showinfo",
                "-show_entries", "frame=pkt_pts_time",
                "-of", "csv=p=0",
                "-v", "quiet"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.warning(f"Scene detection failed: {result.stderr}")
                return [0.0]  # Fallback to single scene
            
            # Parse timestamps
            timestamps = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    try:
                        ts = float(line)
                        timestamps.append(ts)
                    except ValueError:
                        continue
            
            # Always include 0.0 as first scene
            if not timestamps:
                timestamps = [0.0]
            elif timestamps[0] != 0.0:
                timestamps.insert(0, 0.0)
            
            logger.info(f"Detected {len(timestamps)} scene cuts")
            return timestamps
            
        except subprocess.TimeoutExpired:
            logger.error("Scene detection timed out")
            return [0.0]
        except Exception as e:
            logger.error(f"Scene detection failed: {e}", exc_info=True)
            return [0.0]
