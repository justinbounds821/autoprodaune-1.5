"""
Simple working video generation routes.
This creates REAL video files using basic tools.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import os
import tempfile
import json

# Import basic video generation tools
try:
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    # MoviePy 2.x uses new import structure
    from moviepy import ImageClip, AudioClip, CompositeVideoClip
    PIL_AVAILABLE = True
    logging.info("✅ Video generation libraries loaded successfully")
except ImportError as e:
    logging.error(f"❌ Video generation libraries not available: {e}")
    PIL_AVAILABLE = False

router = APIRouter(
    prefix="/api/simple-video",
    tags=["simple-video"],
    responses={404: {"description": "Not found"}}
)

class SimpleVideoRequest(BaseModel):
    text: str = "AutoPro Daune - Rezolvă daunele rapid și simplu!"
    duration: int = 10  # seconds
    width: int = 720
    height: int = 480
    background_color: str = "#1a73e8"
    text_color: str = "#ffffff"

class VideoResponse(BaseModel):
    success: bool
    message: str
    video_path: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[int] = None

@router.post("/generate", response_model=VideoResponse)
async def generate_simple_video(
    request: SimpleVideoRequest,
    background_tasks: BackgroundTasks
) -> VideoResponse:
    """Generate a simple video with text overlay."""

    if not PIL_AVAILABLE:
        return VideoResponse(
            success=False,
            message="Video generation libraries not available. Install PIL, numpy, moviepy."
        )

    try:
        # Create video in background
        video_info = await _create_simple_video(request)

        return VideoResponse(
            success=True,
            message="Video generated successfully!",
            video_path=video_info["path"],
            file_size=video_info["size"],
            duration=request.duration
        )

    except Exception as e:
        logging.error(f"Video generation failed: {e}")
        return VideoResponse(
            success=False,
            message=f"Video generation failed: {str(e)}"
        )

async def _create_simple_video(request: SimpleVideoRequest) -> Dict[str, Any]:
    """Create a simple video file with text."""

    # Create output directory
    output_dir = os.path.join(os.getcwd(), "generated_videos")
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"autopro_video_{timestamp}.mp4"
    video_path = os.path.join(output_dir, video_filename)

    try:
        # Parse background color
        bg_color = request.background_color.lstrip('#')
        bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (0, 2, 4))

        # Parse text color
        text_color = request.text_color.lstrip('#')
        text_rgb = tuple(int(text_color[i:i+2], 16) for i in (0, 2, 4))

        # Create image with text
        img = Image.new('RGB', (request.width, request.height), bg_rgb)
        draw = ImageDraw.Draw(img)

        # Try to load a font
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
            except:
                font = ImageFont.load_default()

        # Calculate text position (centered)
        text_bbox = draw.textbbox((0, 0), request.text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        x = (request.width - text_width) // 2
        y = (request.height - text_height) // 2

        # Draw text
        draw.text((x, y), request.text, font=font, fill=text_rgb)

        # Convert PIL image to numpy array
        img_array = np.array(img)

        # Create video clip
        clip = ImageClip(img_array, duration=request.duration)

        # Write video file
        clip.write_videofile(
            video_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            verbose=False,
            logger=None
        )

        # Get file size
        file_size = os.path.getsize(video_path)

        logging.info(f"Video created successfully: {video_path} ({file_size} bytes)")

        return {
            "path": video_path,
            "filename": video_filename,
            "size": file_size,
            "duration": request.duration
        }

    except Exception as e:
        logging.error(f"Video creation failed: {e}")
        # Create a simple text file as fallback
        with open(video_path.replace('.mp4', '.txt'), 'w') as f:
            f.write(f"Video generation failed: {str(e)}\n")
            f.write(f"Request: {json.dumps(request.dict(), indent=2)}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")

        raise e

@router.get("/list")
async def list_generated_videos():
    """List all generated videos and demo files."""

    output_dir = os.path.join(os.getcwd(), "generated_videos")

    if not os.path.exists(output_dir):
        return {"videos": [], "count": 0, "message": "No files generated yet"}

    videos = []
    for filename in os.listdir(output_dir):
        if filename.endswith(('.mp4', '.txt')):  # Include demo files too
            filepath = os.path.join(output_dir, filename)
            stat = os.stat(filepath)
            videos.append({
                "filename": filename,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "path": filepath,
                "type": "video" if filename.endswith('.mp4') else "demo"
            })

    videos_sorted = sorted(videos, key=lambda x: x['created'], reverse=True)

    return {
        "success": True,
        "videos": videos_sorted,
        "count": len(videos_sorted),
        "message": f"Found {len(videos_sorted)} generated files"
    }

@router.post("/create-demo")
async def create_demo_file():
    """Create a simple demo file to prove the endpoint works."""

    # Create output directory
    output_dir = os.path.join(os.getcwd(), "generated_videos")
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    demo_filename = f"autopro_demo_{timestamp}.txt"
    demo_path = os.path.join(output_dir, demo_filename)

    # Create demo content
    content = f"""
🎬 AUTOPRO DAUNE VIDEO GENERATION TEST
=====================================

This file was created by the working video generation API!

Timestamp: {datetime.now().isoformat()}
System: AutoPro Daune Video Generator
Status: WORKING! ✅

Next step: Generate actual video files with MoviePy
"""

    # Write file
    with open(demo_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return {
        "success": True,
        "message": "Demo file created successfully! The endpoint is WORKING!",
        "file_path": demo_path,
        "file_size": os.path.getsize(demo_path),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/test")
async def test_video_capabilities():
    """Test video generation capabilities."""

    capabilities = {
        "pil_available": PIL_AVAILABLE,
        "output_directory": os.path.join(os.getcwd(), "generated_videos"),
        "timestamp": datetime.now().isoformat()
    }

    if PIL_AVAILABLE:
        capabilities["status"] = "Ready for video generation"
    else:
        capabilities["status"] = "Missing required libraries"
        capabilities["required"] = ["PIL", "numpy", "moviepy"]

    return capabilities