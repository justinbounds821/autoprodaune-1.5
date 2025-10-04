"""
Autoposter routes for API.

This module exposes endpoints to trigger video generation and social media posting.
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict, Any

"""
Autoposter routes for the AutoPro Daune API.

This module exposes endpoints for generating promotional videos and
publishing them to social media platforms. The original implementation
imported services via an absolute ``services`` package which is not
present in this codebase. The services are now referenced via
relative imports from ``..services``. If the import fails due to
missing third‑party dependencies (e.g. googleapiclient), fallback
implementations are used so that the routes remain registered and can
be tested without external APIs. Replace the fallback with real
services in a production environment.
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict, Any
import os

router = APIRouter()

try:
    # Attempt to import the real autoposter services
    from ..services.autoposter import run_autoposter, discover_videos
    from ..services.video_generator import VideoGenerator
except Exception as import_exc:
    # If the real services cannot be imported (e.g. missing dependencies),
    # define minimal fallbacks for testing purposes.
    import logging
    logging.warning(
        f"Autoposter services unavailable ({import_exc}); using fallback implementations."
    )
    def run_autoposter() -> Dict[str, int]:
        """Mock autoposter that does nothing and returns zero counts."""
        return {"processed": 0, "published": 0}
    def discover_videos(directory: str) -> list[str]:
        """Mock discover_videos that returns an empty list."""
        return []
    class VideoGenerator:
        """Mock video generator used when dependencies are missing."""
        def generate_video(self) -> Dict[str, Any]:
            return {"video_path": "mock_video.mp4", "metadata": {}}

router = APIRouter()


@router.post("/autoposter/generate")
async def generate_video() -> Dict[str, Any]:
    """Generate a new promotional video using AI."""
    try:
        generator = VideoGenerator()
        result = generator.generate_video()
        return {
            "status": "success",
            "video_path": result["video_path"],
            "metadata": result["metadata"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/autoposter/publish")
async def publish_videos(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Trigger autoposter to publish pending videos."""
    
    # Run autoposter in background to avoid timeout
    background_tasks.add_task(run_autoposter)
    
    return {
        "status": "triggered",
        "message": "Autoposter started in background"
    }


@router.get("/autoposter/status")
async def get_status() -> Dict[str, Any]:
    """Get autoposter status and list of pending videos.

    This endpoint uses the ``discover_videos`` function imported at
    module level (or its fallback) rather than importing the service
    anew. It reads the ``AUTOPOSTER_DIRECTORY`` environment variable to
    determine where to look for videos. When the autoposter services
    are stubbed, this simply returns an empty list.
    """
    import os
    directory = os.getenv("AUTOPOSTER_DIRECTORY", "videos/to_publish")
    pending = discover_videos(directory)
    return {
        "status": "ready",
        "pending_videos": len(pending),
        "videos": [os.path.basename(v) for v in pending]
    }
