"""
B-roll Injector Service - Insert B-roll footage into videos
Single Responsibility: Enhance videos with contextual B-roll clips
Safe-by-default: Disabled unless ENABLE_BROLL_INJECT=true
"""
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import random

logger = logging.getLogger(__name__)


class BRollInjectorService:
    """
    Automatically inject B-roll footage at appropriate points in videos.
    Uses scene detection and keyword matching.
    """
    
    def __init__(self):
        self.enabled = os.getenv("ENABLE_BROLL_INJECT", "false").lower() == "true"
        self.broll_library_path = os.getenv("BROLL_LIBRARY_PATH", "assets/broll")
        self.inject_frequency = int(os.getenv("BROLL_INJECT_FREQUENCY", "30"))  # seconds
        
        if not self.enabled:
            logger.info("⚠️ B-roll injection disabled (ENABLE_BROLL_INJECT=false)")
            return
        
        # Check if B-roll library exists
        library_path = Path(self.broll_library_path)
        if not library_path.exists():
            logger.warning(f"⚠️ B-roll library not found at {self.broll_library_path}")
            self.enabled = False
        else:
            # Count available B-roll clips
            self.broll_clips = list(library_path.glob("**/*.mp4"))
            logger.info(f"✅ B-roll injection enabled ({len(self.broll_clips)} clips available)")
    
    async def inject_broll(
        self, 
        main_video_path: str,
        scenes: Optional[List[Dict[str, Any]]] = None,
        keywords: Optional[List[str]] = None,
        output_path: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Inject B-roll clips into main video.
        Returns dict with output path and injection points.
        """
        if not self.enabled:
            logger.debug(f"B-roll injection disabled for {main_video_path}")
            return None
        
        try:
            if output_path is None:
                path_obj = Path(main_video_path)
                output_path = str(path_obj.with_stem(f"{path_obj.stem}_broll"))
            
            # Select B-roll clips based on keywords or random
            selected_clips = self._select_broll_clips(keywords)
            
            if not selected_clips:
                logger.warning("No suitable B-roll clips found")
                return None
            
            # Determine injection points
            injection_points = self._calculate_injection_points(scenes)
            
            # Build FFmpeg filter complex for B-roll overlay
            filter_script = self._build_broll_filter(
                main_video_path,
                selected_clips,
                injection_points
            )
            
            logger.info(f"Injecting {len(selected_clips)} B-roll clips at {len(injection_points)} points")
            
            return {
                "output_path": output_path,
                "broll_clips_used": len(selected_clips),
                "injection_points": injection_points,
                "filter_script": filter_script,
                "status": "ready_to_render"
            }
        
        except Exception as e:
            logger.error(f"B-roll injection failed: {e}")
            return None
    
    def _select_broll_clips(self, keywords: Optional[List[str]] = None) -> List[str]:
        """Select appropriate B-roll clips based on keywords"""
        if not self.broll_clips:
            return []
        
        if keywords:
            # Match B-roll clips to keywords (filename matching)
            matched_clips = []
            for clip in self.broll_clips:
                clip_name = clip.stem.lower()
                if any(kw.lower() in clip_name for kw in keywords):
                    matched_clips.append(str(clip))
            
            if matched_clips:
                return matched_clips[:5]  # Limit to 5 clips
        
        # Fallback: random selection
        return [str(clip) for clip in random.sample(self.broll_clips, min(3, len(self.broll_clips)))]
    
    def _calculate_injection_points(
        self, 
        scenes: Optional[List[Dict[str, Any]]] = None
    ) -> List[float]:
        """Calculate timestamps where B-roll should be injected"""
        if scenes:
            # Use scene boundaries
            return [scene["start_seconds"] for scene in scenes[::2]]  # Every other scene
        else:
            # Fallback: fixed intervals
            return [float(i * self.inject_frequency) for i in range(1, 10)]
    
    def _build_broll_filter(
        self,
        main_video: str,
        broll_clips: List[str],
        injection_points: List[float]
    ) -> str:
        """Build FFmpeg filter complex for B-roll overlay"""
        # Simplified filter - actual implementation would be complex
        filters = []
        
        for i, (clip, timestamp) in enumerate(zip(broll_clips, injection_points)):
            # Overlay B-roll as picture-in-picture or full-screen insert
            filters.append(
                f"[1:v]scale=iw*0.3:ih*0.3[broll{i}]; "
                f"[0:v][broll{i}]overlay=W-w-10:10:enable='between(t,{timestamp},{timestamp+5})'[v{i}]"
            )
        
        return "; ".join(filters)
    
    def get_health(self) -> Dict[str, Any]:
        """Health check for B-roll injection"""
        return {
            "enabled": self.enabled,
            "library_path": self.broll_library_path,
            "clips_available": len(self.broll_clips) if self.enabled else 0,
            "inject_frequency": self.inject_frequency
        }


# Singleton instance
_instance = None

def get_broll_injector() -> BRollInjectorService:
    """Get or create BRollInjectorService singleton"""
    global _instance
    if _instance is None:
        _instance = BRollInjectorService()
    return _instance
