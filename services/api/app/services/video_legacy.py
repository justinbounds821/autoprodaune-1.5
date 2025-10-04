# -*- coding: utf-8 -*-
"""
Legacy video pipeline helpers extracted from routes/video.py
Doar relocare  fără schimbare de logică. Ține funcțiile sub 40 linii la iterațiile următoare.
"""

import os, logging, tempfile
from typing import Dict, Any
from datetime import datetime, timezone

from . import video_utils as vu
from .video_constants import RES_MAP
from ..schemas.video import JobStatus
from ..services.supabase_client import get_supabase_service_instance

# PIL pentru background
from PIL import Image, ImageDraw, ImageFont

def _download_to_tmp(url: str, suffix: str = ".bin") -> str:
    import requests
    fd, path = tempfile.mkstemp(suffix=suffix, prefix="bg_")
    os.close(fd)
    with requests.get(url, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
    return path


def generate_video_job(job_id: str, video_data: Dict[str, Any]):
    """FuncÈ›ie helper pentru generarea unui video Ã®n background."""
    logging.info(f"Generare video {job_id} Ã®n curs...")
    
    # GÄƒseÈ™te job-ul Ã®n baza de date dupÄƒ client_job_id
    supabase_service = get_supabase_service_instance()
    jobs = supabase_service._table_select("video_jobs", "*", filters=[("eq", "client_job_id", job_id)])
    
    if not jobs:
        logging.error(f"Job-ul {job_id} nu a fost gÄƒsit Ã®n baza de date")
        return
    
    job_db_id = jobs[0]["id"]
    
    # MutÄƒ job-ul Ã®n status "processing" cÃ¢nd Ã®ncepe efectiv procesarea
    supabase_service._table_update_eq("video_jobs", "client_job_id", job_db_id, {
        "status": JobStatus.processing.value,
        "updated_at": now()
    })

    video = None
    try:
        from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip
        
        # FoloseÈ™te maparea de rezoluÈ›ie
        size = RES_MAP.get(video_data.get("resolution", "1080p"), (1920, 1080))

        templates_dir, output_dir = "templates", "generated_videos"
        os.makedirs(templates_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{job_id}.mp4")

        # Check for cancellation
        if is_cancelled_by_dbid(job_db_id):
            logging.info(f"Job {job_id} cancelled before processing")
            return

        get_supabase_service_instance()._table_update_eq("video_jobs", id_column, job_db_id, {
            "progress": 20, 
            "updated_at": datetime.now(timezone.utc).isoformat()
        })

        # Sanitizare template pentru securitate
        safe_name = os.path.basename(video_data.get("template") or "default_template.mp4")
        if not safe_name.endswith(".mp4"):
            raise ValueError("Template invalid")
        template_path = os.path.join(templates_dir, safe_name)

        if os.path.exists(template_path):
            # Load and resize template to requested resolution
            base = VideoFileClip(template_path)
            if base.size != list(size):
                base = base.resize(newsize=size)
            video = base
            
            # Check for cancellation
            if is_cancelled_by_dbid(job_db_id):
                logging.info(f"Job {job_id} cancelled during template processing")
                return
                
            get_supabase_service_instance()._table_update_eq("video_jobs", id_column, job_db_id, {
                "progress": 40, 
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
            
            if video_data.get("text"):
                text_clip = vu.make_text_clip(
                    video_data["text"], 
                    size=size, 
                    duration=video.duration, 
                    position="bottom"
                )
                video = CompositeVideoClip([video, text_clip])
        else:
            # Create simple video with background and text
            duration = video_data.get("duration_seconds", 30)
            background = ColorClip(size=size, color=(0, 100, 200), duration=duration)
            txt = video_data.get("text") or "AutoPro Daune - Video generat automat"
            text_clip = vu.make_text_clip(txt, size=size, duration=duration, position="center")
            video = CompositeVideoClip([background, text_clip])

        # Check for cancellation before heavy processing
        if is_cancelled_by_dbid(job_db_id):
            logging.info(f"Job {job_id} cancelled before video encoding")
            return

        get_supabase_service_instance()._table_update_eq("video_jobs", id_column, job_db_id, {
            "progress": 70, 
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Scrierea video cu parametri FFmpeg stabili
        video.write_videofile(
            output_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            temp_audiofile=f"{output_path}.aaccache", 
            remove_temp=True, 
            threads=2, 
            preset="medium"
        )
        
        file_size_mb = os.path.getsize(output_path) / (1024*1024)

        # Upload to storage and get public URL
        try:
            public_url = get_supabase_service_instance().upload_from_path("video-outputs", f"{job_id}.mp4", output_path)
        except Exception as upload_error:
            logging.warning(f"Upload failed for {job_id}, using local path: {upload_error}")
            public_url = output_path  # Fallback to local path

        get_supabase_service_instance()._table_update_eq("video_jobs", id_column, job_db_id, {
            "status": JobStatus.completed.value, 
            "progress": 100, 
            "file_size_mb": round(file_size_mb, 2),
            "output_url": public_url, 
            "completed_at": datetime.now(timezone.utc).isoformat(), 
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
        logging.info(f"Generare video {job_id} OK: {public_url}")

    except Exception as video_error:
        get_supabase_service_instance()._table_update_eq("video_jobs", id_column, job_db_id, {
            "status": JobStatus.failed.value, 
            "error_message": str(video_error), 
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
        logging.exception(f"Eroare la generarea video-ului {job_id}: {video_error}")
    finally:
        # ÃŽnchide resursele MoviePy
        if video:
            video.close()



def make_background(size, bg_type, bg_value):
    """Create background based on type and value."""
    import requests
    
    if bg_type == "color":
        # Solid color background
        if bg_value and bg_value.startswith("#"):
            # Convert hex to RGB
            hex_color = bg_value.lstrip("#")
            rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            rgb_color = (7, 59, 122)  # Default AutoPro blue
        return Image.new("RGB", size, rgb_color)
    
    elif bg_type == "gradient":
        # Linear gradient top to bottom
        img = Image.new("RGB", size, (0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Default gradient colors
        top_color = (7, 59, 122)    # AutoPro blue
        bottom_color = (0, 0, 50)   # Darker blue
        
        for y in range(size[1]):
            ratio = y / size[1]
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            draw.line([(0, y), (size[0], y)], fill=(r, g, b))
        
        return img
    
    elif bg_type == "image":
        # Image background
        if bg_value:
            try:
                if bg_value.startswith("http"):
                    # Download image
                    img_path = _download_to_tmp(bg_value, ".jpg")
                    bg_img = Image.open(img_path)
                    os.unlink(img_path)  # Clean up temp file
                else:
                    # Local file
                    bg_img = Image.open(bg_value)
                
                # Resize to cover (crop center)
                bg_img = bg_img.convert("RGB")
                bg_img.thumbnail((size[0] * 2, size[1] * 2), Image.Resampling.LANCZOS)
                
                # Center crop
                left = (bg_img.width - size[0]) // 2
                top = (bg_img.height - size[1]) // 2
                right = left + size[0]
                bottom = top + size[1]
                
                return bg_img.crop((left, top, right, bottom))
            except Exception as e:
                logging.warning(f"Failed to load background image: {e}")
        
        # Fallback to solid color
        return _make_background(size, "color", "#073B7A")
    
    elif bg_type == "video":
        # Video background (placeholder for now)
        logging.info("Video background not implemented yet, using gradient fallback")
        return _make_background(size, "gradient", None)
    
    else:
        # Default fallback
        return _make_background(size, "color", "#073B7A")

