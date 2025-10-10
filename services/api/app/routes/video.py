"""
Video management routes for AutoPro Daune API.

This module provides endpoints for video queue management and processing.
"""

from fastapi import APIRouter, HTTPException, Query, Security, BackgroundTasks, File, UploadFile, Form
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, constr, field_validator
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging
import os
import io
import asyncio
import tempfile
import shutil
from enum import Enum
import numpy as np
import base64

# Setup logger
logger = logging.getLogger(__name__)

# Importuri pentru servicii și schemas
from ..services import video_utils as vu
from ..services import video_legacy as vleg
from ..services.video_constants import RES_MAP, DEFAULT_BG_COLOR
from ..schemas.video import ManoleGenerateRequest, VideoGenerateRequest, RetryRequest, JobStatus

# Top-level imports for PIL and MoviePy
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception as e:
    logging.exception("Pillow import failed: %s", e)
    raise

# Setează FFmpeg înainte de orice import MoviePy
try:
    from imageio_ffmpeg import get_ffmpeg_exe
    exe = get_ffmpeg_exe()  # descarcă binar portabil dacă nu există
    os.environ["IMAGEIO_FFMPEG_EXE"] = exe
    os.environ["FFMPEG_BINARY"] = exe   # MoviePy 1.x/2.x citește asta
    logging.info("FFmpeg resolved at: %s", exe)
except Exception as e:
    logging.warning("FFmpeg auto-resolve failed: %s", e)

# Apelează video_utils pentru backup
from ..services import video_utils as vu
vu.ensure_ffmpeg_exe()

# Abia după setarea variabilelor:
try:
    from moviepy import ImageClip, VideoFileClip, CompositeVideoClip, ColorClip, AudioFileClip
except Exception:  # fallback pt. 1.x
    try:
        from moviepy.editor import ImageClip, VideoFileClip, CompositeVideoClip, ColorClip, AudioFileClip
    except Exception as e:
        logging.exception("MoviePy import failed: %s", e)
        raise

from ..services.supabase_client import get_supabase_service_instance

# Runtime hardening helpers
def ensure_ffmpeg_exe():
    """Check if FFmpeg is available in PATH or FFMPEG_PATH env var."""
    ff = shutil.which("ffmpeg") or os.getenv("FFMPEG_PATH")
    if not ff:
        logging.warning("FFmpeg not found in PATH nor FFMPEG_PATH; encoding may fail.")
    return ff

def ensure_dir(*paths):
    """Safely create directories (Windows/Unix compatible)."""
    for p in paths: 
        os.makedirs(p, exist_ok=True)

def with_duration(clip, d): 
    """MoviePy API compatibility wrapper for duration."""
    return getattr(clip, "with_duration", clip.set_duration)(d)

def with_position(clip, p): 
    """MoviePy API compatibility wrapper for position."""
    return getattr(clip, "with_position", clip.set_position)(p)

def with_audio(clip, a): 
    """MoviePy API compatibility wrapper for audio."""
    return getattr(clip, "with_audio", clip.set_audio)(a)


# Robust PIL imports
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception as e:
    logging.exception("Pillow import failed: %s", e)
    raise

security = HTTPBearer()
router = APIRouter(
    prefix="/api/video",
    tags=["video"],
    responses={404: {"description": "Not found"}}
)

# DTO-uri mutate �n schemas/video.py
# Job status enum
class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"

# Helper for UTC timestamps
def now() -> str:
    """Get current UTC timestamp as ISO string."""
    return datetime.now(timezone.utc).isoformat()

def make_text_clip(txt: str, size: tuple, duration: int, position: str = "center"):
    """Create text clip using Pillow to avoid ImageMagick dependency."""
    try:
        from moviepy.editor import ImageClip
        
        W, H = size
        # Create transparent canvas
        img = Image.new("RGBA", (int(W*0.9), H), (0, 0, 0, 0))
        
        # Try to use system font, fallback to default
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 60)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            except:
                try:
                    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 60)
                except:
                    font = ImageFont.load_default()
        
        # Calculate text size and position
        d = ImageDraw.Draw(img)
        text_bbox = d.multiline_textbbox((0, 0), txt, font=font, align="center")
        tw, th = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        y = (H - th) // 2
        
        # Draw text
        d.multiline_text(
            ((W*0.9 - tw) // 2, y), 
            txt, 
            font=font, 
            fill=(255, 255, 255, 255), 
            align="center"
        )
        
        # Crop to text area with padding
        crop = img.crop((0, max(0, y-40), int(W*0.9), min(H, y+th+40)))
        
        # Use compatibility wrappers
        clip = ImageClip(np.array(crop), is_mask=False)
        return vu.with_position(vu.with_duration(clip, duration), position)
        
    except Exception as e:
        logging.error(f"Error creating text clip with Pillow: {e}")
        # Return transparent clip to avoid ImageMagick dependency
        logging.warning(f"Text rendering failed, returning transparent clip for: {txt}")
        from moviepy.editor import ImageClip
        arr = np.zeros((1, 1, 4), dtype=np.uint8)  # 1x1 transparent RGBA
        clip = ImageClip(arr, is_mask=False)
        return vu.with_position(vu.with_duration(clip, duration), position)

@router.get("/queue")
async def get_video_queue(
    status: Optional[JobStatus] = Query(None, description="queued|processing|completed|failed|cancelled"),
    limit: int = Query(50, ge=1, le=200, description="Numărul maxim de job-uri")
) -> Dict[str, Any]:
    """
    Obține coada de procesare video din Supabase.
    
    Args:
        status: Status-ul job-urilor (opțional)
        limit: Numărul maxim de job-uri (1-200)
        
    Returns:
        Dicționar cu coada de video
    """
    try:
        # Import serviciu
        from ..services.video_queue import VideoQueueSupabase
        
        # Folosește serviciul nou
        queue_service = VideoQueueSupabase()
        jobs = queue_service.get_jobs(status.value if status else None)
        
        # Aplică limit
        if limit < len(jobs):
            jobs = jobs[:limit]
        
        return {
            "items": jobs,
            "total": len(jobs),
            "status": status.value if status else None,
            "limit": limit
        }
        
    except Exception as e:
        logging.error(f"Eroare la obținerea cozii video: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la coada video: {str(e)}")

@router.post("/retry", status_code=202)
async def retry_video_job(
    payload: RetryRequest,
    background_tasks: BackgroundTasks,
    _auth: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    Reîncearcă procesarea unui job video.
    
    Args:
        payload: Request payload with job_id
        _auth: Authentication credentials
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        # Import serviciu
        from ..services.video_queue import VideoQueueSupabase
        
        # Folosește serviciul nou pentru retry
        queue_service = VideoQueueSupabase()
        queue_service.retry_job(payload.job_id)
        
        return {
            "success": True,
            "message": f"Retry pentru job-ul {payload.job_id} inițiat",
            "job_id": payload.job_id,
            "timestamp": now()
        }
        
    except Exception as e:
        logging.error(f"Eroare la retry job-ului {payload.job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la retry: {str(e)}")

@router.post("/generate", status_code=202)
async def generate_video(
    video_data: VideoGenerateRequest,
    background_tasks: BackgroundTasks,
    _auth: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    Generează un video nou.
    
    Args:
        video_data: Datele pentru generarea video-ului
        _auth: Authentication credentials
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        # Creează job ID și job-ul în baza de date
        job_id = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Creează job-ul în baza de date cu status "queued"
        job_result = get_supabase_service_instance().video_queue_enqueue({
            "client_job_id": job_id,
            "filename": f"{job_id}.mp4",
            "status": JobStatus.queued.value,
            "progress": 0,
            "duration_seconds": video_data.duration_seconds,
            "resolution": video_data.resolution,
            "file_size_mb": None,
            "output_url": None,
            "error_message": None,
            "created_at": now(),
            "updated_at": now()
        })
        
        # Pornește task-ul în background
        background_tasks.add_task(vleg.generate_video_job, job_id, video_data.dict())
        
        return {
            "success": True,
            "message": "Generare video inițiată",
            "job_id": job_id,
            "timestamp": now()
        }
        
    except Exception as e:
        logging.error(f"Eroare la generarea video-ului: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la generarea video-ului: {str(e)}")

@router.post("/internal-generate", status_code=200)
async def generate_internal_video(
    text: str = Form(..., description="Textul pentru voice-over"),
    voice_style: str = Form("professional", description="Stilul vocii: professional, empathetic, confident, manole"),
    background_type: str = Form("gradient", description="Tip background: gradient, solid"),
    aspect_ratio: str = Form("16:9", description="Aspect ratio: 16:9, 9:16, 1:1"),
    resolution: str = Form("1080p", description="Rezoluție: 720p, 1080p, 4k")
) -> Dict[str, Any]:
    """
    🎬 Generează video INTERN prin ORCHESTRATOR - ZERO COSTURI!
    
    Folosește:
    - VideoOrchestrator pentru logică centralizată
    - ElevenLabs pentru voce
    - FFmpeg + MoviePy pentru procesare
    - PIL pentru grafică
    
    Nu necesită HeyGen, Pika sau alte servicii plătite.
    """
    try:
        from ..services.video_orchestrator import get_video_orchestrator, VideoType
        
        orchestrator = get_video_orchestrator()
        result = await orchestrator.generate_video(
            video_type=VideoType.GENERIC,
            context={
                "text": text,
                "voice_style": voice_style,
                "background_type": background_type,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution
            }
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Video generation failed: {result.get('error', 'Unknown error')}"
            )
        
        # Convertește video la base64 pentru preview (opțional)
        video_path = result["video_path"]
        try:
            with open(video_path, "rb") as f:
                video_content = f.read()
                video_base64 = base64.b64encode(video_content).decode()
                # Limitează dimensiunea pentru răspuns HTTP
                preview_base64 = video_base64[:100000] if len(video_base64) > 100000 else video_base64
        except Exception as e:
            logger.warning(f"Failed to encode video to base64: {e}")
            preview_base64 = None
        
        return {
            "success": True,
            "message": "✅ Video generat cu succes prin Orchestrator (ZERO COST)!",
            "video_id": result["video_id"],
            "video_path": result["video_path"],
            "video_url": result.get("video_url"),
            "preview_base64": preview_base64,
            "duration_seconds": result["duration_seconds"],
            "file_size_mb": result["file_size_mb"],
            "provider": result["provider"],
            "cost": 0.0,
            "video_type": result["video_type"]
        }
        
    except Exception as e:
        logger.error(f"[Internal Video] Generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate internal video: {str(e)}"
        )

@router.post("/generate-from-lead/{lead_id}", status_code=200)
async def generate_video_from_lead(
    lead_id: str,
    video_type: str = Form("testimonial", description="Tip video: testimonial, update, reminder")
) -> Dict[str, Any]:
    """
    🎬 Generează video AUTOMAT din lead REAL prin ORCHESTRATOR!
    
    Citește datele lead-ului din baza de date și generează:
    - Script personalizat cu AI
    - Voice-over cu ElevenLabs
    - Video complet cu FFmpeg
    
    ZERO COSTURI EXTERNE!
    """
    try:
        from ..services.video_orchestrator import get_video_orchestrator, VideoType
        
        # Map video_type la VideoType enum
        type_map = {
            "testimonial": VideoType.LEAD_TESTIMONIAL,
            "update": VideoType.LEAD_UPDATE,
            "reminder": VideoType.LEAD_REMINDER
        }
        
        vtype = type_map.get(video_type, VideoType.LEAD_UPDATE)
        
        orchestrator = get_video_orchestrator()
        result = await orchestrator.generate_video(
            video_type=vtype,
            context={"lead_id": lead_id}
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=404 if "not found" in result.get("error", "").lower() else 500,
                detail=result.get("error", "Unknown error")
            )
        
        return {
            "success": True,
            "message": f"✅ Video generat din lead {lead_id} prin Orchestrator!",
            "video_id": result["video_id"],
            "video_path": result["video_path"],
            "video_url": result.get("video_url"),
            "duration_seconds": result["duration_seconds"],
            "file_size_mb": result["file_size_mb"],
            "provider": result["provider"],
            "cost": 0.0,
            "script": result.get("script")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Lead Video] Failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate video from lead: {str(e)}"
        )

@router.post("/generate-daily-summary", status_code=200)
async def generate_daily_summary_video() -> Dict[str, Any]:
    """
    🎬 Generează video SUMAR ZILNIC prin ORCHESTRATOR!
    
    Citește automat:
    - Lead-uri noi astăzi
    - Cazuri finalizate
    - Venituri generate
    - Statistici de performanță
    
    Generează video profesional cu toate statisticile.
    ZERO COSTURI EXTERNE!
    """
    try:
        from ..services.video_orchestrator import get_video_orchestrator, VideoType
        
        orchestrator = get_video_orchestrator()
        result = await orchestrator.generate_video(
            video_type=VideoType.REPORT_DAILY,
            context={"period": "daily"}
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Unknown error")
            )
        
        return {
            "success": True,
            "message": "✅ Video sumar zilnic generat prin Orchestrator!",
            "video_id": result["video_id"],
            "video_path": result["video_path"],
            "video_url": result.get("video_url"),
            "duration_seconds": result["duration_seconds"],
            "file_size_mb": result["file_size_mb"],
            "provider": result["provider"],
            "cost": 0.0,
            "script": result.get("script")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Daily Summary] Failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate daily summary: {str(e)}"
        )

@router.post("/lipsync-generate", status_code=202)
async def generate_lipsync_video(
    script: str = Form(..., description="Text pentru voce"),
    avatar_image: Optional[UploadFile] = File(None, description="Poza avatar (PNG/JPG)"),
    voice_id: Optional[str] = Form(None, description="ID voce ElevenLabs")
) -> Dict[str, Any]:
    """
    🎬 Generează video cu LIP-SYNC REAL!
    
    Folosește:
    - SadTalker/Wav2Lip pentru lip-sync
    - ElevenLabs pentru voce
    - Poza ta devine avatar animat vorbitor
    
    TOTUL FUNCȚIONAL!
    """
    try:
        from ..services.video_engine_lipsync import enqueue_lipsync
        import tempfile
        
        # Salvează imaginea uploaded
        avatar_image_path = None
        if avatar_image:
            # Salvează temporar
            temp_dir = Path("uploaded_avatars")
            temp_dir.mkdir(exist_ok=True)
            avatar_image_path = temp_dir / f"avatar_{int(datetime.now().timestamp())}_{avatar_image.filename}"
            
            with open(avatar_image_path, "wb") as f:
                content = await avatar_image.read()
                f.write(content)
            
            logger.info(f"Avatar image saved: {avatar_image_path}")
        
        # Generează job ID și pornește procesare
        job_id = await enqueue_lipsync(
            script=script,
            voice_id=voice_id,
            avatar_image_url=str(avatar_image_path) if avatar_image_path else None,
            avatar_video_url=None
        )
        
        return {
            "success": True,
            "message": "🎬 Video cu lip-sync în procesare!",
            "job_id": job_id,
            "status": "processing",
            "check_status_url": f"/api/video/job-status/{job_id}",
            "estimated_time": "2-5 minute",
            "provider": "Internal (SadTalker/Wav2Lip + ElevenLabs)",
            "cost": 0.0
        }
        
    except Exception as e:
        logger.error(f"[Lipsync Video] Failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate lipsync video: {str(e)}"
        )

@router.get("/job-status/{job_id}")
async def get_job_status(job_id: str) -> Dict[str, Any]:
    """
    Verifică statusul unui job de video.
    """
    try:
        from ..services.job_store import get_job
        
        job = get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "success": True,
            "job_id": job_id,
            "status": job.get("status", "unknown"),
            "progress": job.get("progress", 0),
            "video_url": job.get("video_url"),
            "error": job.get("error"),
            "metadata": job.get("meta", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Job Status] Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/manole-generate", status_code=202)
async def generate_manole_video(
    manole_data: ManoleGenerateRequest,
    background_tasks: BackgroundTasks,
    _auth: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    Generează un video personalizat cu Manole ca prezentator.
    
    Args:
        manole_data: Datele pentru generarea video-ului Manole
        background_tasks: Background tasks pentru procesare
        _auth: Authentication credentials
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        # Import servicii
        from ..services.video_queue import VideoQueueSupabase
        from ..services.video_generator import ManoleVideoGenerator
        
        # Pregătește payload
        payload = manole_data.dict()
        payload["type"] = "manole"
        
        # Enqueue job
        queue_service = VideoQueueSupabase()
        job_id = queue_service.enqueue(payload)
        
        # Pornește background task
        from ..services.supabase_client import get_supabase_service_instance
        generator = ManoleVideoGenerator(get_supabase_service_instance(), {})
        background_tasks.add_task(generator.generate, job_id, payload)
        
        return {
            "success": True,
            "message": "Generare video Manole inițiată",
            "job_id": job_id,
            "timestamp": now()
        }
        
    except Exception as e:
        logging.error(f"Eroare la generarea video-ului Manole: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la generarea video-ului Manole: {str(e)}")

@router.get("/stats")
async def get_video_stats() -> Dict[str, Any]:
    """
    Obține statistici despre procesarea video-urilor.
    
    Returns:
        Dicționar cu statisticile
    """
    try:
        return get_supabase_service_instance().video_stats()
    except Exception as e:
        logging.error(f"Eroare la obținerea statisticilor video: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la statisticile video: {str(e)}")

@router.delete("/queue/{job_id}", status_code=202)
async def cancel_video_job(
    job_id: str,
    _auth: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    Anulează un job video.
    
    Args:
        job_id: ID-ul job-ului
        _auth: Authentication credentials
        
    Returns:
        Dicționar cu rezultatul operației
    """
    try:
        # Marchează job-ul ca fiind anulat în baza de date
        result = get_supabase_service_instance()._table_update_eq(
            "video_jobs", 
            "client_job_id", 
            job_id, 
            {
                "status": JobStatus.cancelled.value,
                "updated_at": now()
            }
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Job-ul nu a fost găsit")
            
        return {
            "success": True,
            "message": f"Job-ul {job_id} a fost anulat",
            "job_id": job_id,
            "timestamp": now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Eroare la anularea job-ului {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la anularea job-ului: {str(e)}")

# Funcții helper pentru background tasks
def _retry_video_job(job_id: str):
    """Funcție helper pentru retry-ul unui job video în background."""
    logging.info(f"Retry job video {job_id} în curs...")
    # TODO: citește job, resetează status/progres și requeue
    import time
    time.sleep(1)
    logging.info(f"Retry job video {job_id} completat (stub)")

def is_cancelled_by_client_id(client_job_id: str) -> bool:
    """Check if job is cancelled by client_job_id."""
    try:
        result = get_supabase_service_instance()._table_select("video_jobs", "status", filters=[("eq", "client_job_id", client_job_id)])
        if result:
            return result[0].get("status") in {"cancelled", "cancelling"}
        return False
    except:
        return False

def is_cancelled_by_dbid(job_db_id: str) -> bool:
    """Check if job is cancelled by database ID."""
    try:
        result = get_supabase_service_instance()._table_select("video_jobs", "status", filters=[("eq", "id", job_db_id)])
        if result:
            return result[0].get("status") in {"cancelled", "cancelling"}
        return False
    except:
        return False


# Funcția _manole_video_job a fost mutata în ManoleVideoGenerator din services/video_generator.py


# ============================================
# MANOLE VIDEO GENERATOR ENDPOINT
# ============================================

@router.post("/video/manole/generate")
async def generate_manole_video(
    prompt: str = Form(..., description="Script prompt for the video"),
    manole_photo: UploadFile = File(..., description="Manole's photo to animate"),
    accident_footage: Optional[list[UploadFile]] = File(None, description="Accident photos/videos (optional)"),
    display_mode: str = Form("sequence", description="Display mode: sequence, pip, or split"),
    voice_emotion: str = Form("professional", description="Voice emotion: professional, empathetic, or urgent"),
):
    """
    Generate video with Manole talking + accident footage.
    
    This endpoint creates a professional video by:
    1. Animating Manole's photo with Ken Burns effect
    2. Generating voice using ElevenLabs (or Edge-TTS fallback)
    3. Overlaying accident footage if provided
    4. Adding WhatsApp CTA overlay
    
    Returns video URL and metadata.
    """
    try:
        from ..services.video_generator import VideoGenerator
        from ..services.audio_tts import ManoleVoiceCloner
        from moviepy.editor import AudioFileClip
        import uuid
        
        logger.info(f"[ManoleVideoEndpoint] Starting generation (mode: {display_mode}, emotion: {voice_emotion})")
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Save uploaded Manole photo
        photo_path = os.path.join(tempfile.gettempdir(), f"manole_photo_{job_id}.jpg")
        with open(photo_path, 'wb') as f:
            content = await manole_photo.read()
            f.write(content)
        
        logger.info(f"[ManoleVideoEndpoint] Photo saved: {photo_path}")
        
        # Initialize generators
        video_gen = VideoGenerator()
        voice_cloner = ManoleVoiceCloner()
        
        # Generate script (use prompt directly or enhance it)
        script = prompt if len(prompt) > 20 else video_gen.generate_prompt()["script"]
        
        logger.info(f"[ManoleVideoEndpoint] Script: {script[:100]}...")
        
        # Generate Manole's voice
        audio_path = await voice_cloner.generate_manole_voice(
            text=script,
            emotion=voice_emotion
        )
        
        logger.info(f"[ManoleVideoEndpoint] Voice generated: {audio_path}")
        
        # Calculate video duration from audio
        audio_clip = AudioFileClip(audio_path)
        video_duration = int(audio_clip.duration) + 2  # Add 2 seconds padding
        audio_clip.close()
        
        # Animate Manole's photo
        photo_clip = video_gen.animate_manole_photo(photo_path, duration=video_duration)
        
        # Add audio to video
        audio_clip = AudioFileClip(audio_path)
        video_with_audio = photo_clip.with_audio(audio_clip)
        
        logger.info(f"[ManoleVideoEndpoint] Photo animated with audio ({video_duration}s)")
        
        # Overlay accident footage if provided
        if accident_footage and len(accident_footage) > 0:
            for idx, footage in enumerate(accident_footage):
                footage_path = os.path.join(tempfile.gettempdir(), f"accident_{job_id}_{idx}{os.path.splitext(footage.filename)[1]}")
                with open(footage_path, 'wb') as f:
                    content = await footage.read()
                    f.write(content)
                
                logger.info(f"[ManoleVideoEndpoint] Adding accident footage: {footage_path}")
                
                # Overlay footage (starts at 10 seconds by default)
                start_time = min(10.0, video_duration / 2)
                video_with_audio = video_gen.overlay_accident_footage(
                    main_clip=video_with_audio,
                    footage_path=footage_path,
                    mode=display_mode,
                    start_time=start_time,
                    footage_duration=5.0
                )
                
                # Cleanup footage file
                try:
                    os.remove(footage_path)
                except:
                    pass
        
        # Add WhatsApp CTA overlay
        final_video = video_gen.add_whatsapp_cta_overlay(video_with_audio)
        
        logger.info(f"[ManoleVideoEndpoint] Final video composed, rendering...")
        
        # Save final video
        output_path = os.path.join(tempfile.gettempdir(), f"manole_video_{job_id}.mp4")
        final_video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=2,
            preset="medium",
            verbose=False,
            logger=None
        )
        
        # Close clips
        final_video.close()
        if hasattr(video_with_audio, 'close'):
            video_with_audio.close()
        if hasattr(photo_clip, 'close'):
            photo_clip.close()
        
        logger.info(f"[ManoleVideoEndpoint] Video rendered: {output_path}")
        
        # Get file size
        file_size = os.path.getsize(output_path)
        
        # Cleanup temporary files
        try:
            os.remove(photo_path)
            voice_cloner.cleanup(audio_path)
        except:
            pass
        
        # Return success with video path (or upload to storage and return URL)
        return {
            "success": True,
            "job_id": job_id,
            "video_path": output_path,  # In production, upload to S3/Supabase and return URL
            "duration": video_duration,
            "file_size": file_size,
            "script": script,
            "mode": display_mode,
            "emotion": voice_emotion,
            "message": "Video generat cu succes! 🎬"
        }
        
    except Exception as e:
        logger.error(f"[ManoleVideoEndpoint] Generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Video generation failed: {str(e)}"
        )


@router.delete("/video/batch")
async def batch_delete_videos(video_ids: list[str]) -> Dict[str, Any]:
    """
    Delete multiple videos in batch.
    
    Args:
        video_ids: List of video IDs to delete
        
    Returns:
        Success status and count of deleted videos
    """
    try:
        from ..services.supabase_client import get_supabase_service_instance
        
        logger.info(f"[VideoBatchDelete] Deleting {len(video_ids)} videos")
        
        supabase = get_supabase_service_instance()
        deleted_count = 0
        errors = []
        
        for video_id in video_ids:
            try:
                # Get video record to delete from storage
                videos = supabase._table_select(
                    "video_jobs",
                    "*",
                    filters=[("eq", "job_id", video_id)]
                )
                
                if videos and len(videos) > 0:
                    video = videos[0]
                    output_url = video.get("output_url")
                    
                    # Delete from storage if exists
                    if output_url:
                        try:
                            # Extract bucket and path from URL
                            if "supabase" in output_url:
                                # Delete from Supabase storage
                                storage_path = output_url.split("/storage/v1/object/public/")[1] if "/storage/v1/object/public/" in output_url else None
                                if storage_path:
                                    bucket_name = storage_path.split("/")[0]
                                    file_path = "/".join(storage_path.split("/")[1:])
                                    supabase.supabase.storage.from_(bucket_name).remove([file_path])
                        except Exception as storage_error:
                            logger.warning(f"[VideoBatchDelete] Storage deletion failed for {video_id}: {storage_error}")
                    
                    # Delete from database
                    supabase._table_delete(
                        "video_jobs",
                        filters=[("eq", "job_id", video_id)]
                    )
                    deleted_count += 1
                    logger.info(f"[VideoBatchDelete] Deleted video: {video_id}")
                else:
                    errors.append({"video_id": video_id, "error": "Not found"})
                    
            except Exception as e:
                logger.error(f"[VideoBatchDelete] Failed to delete {video_id}: {e}")
                errors.append({"video_id": video_id, "error": str(e)})
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "total_requested": len(video_ids),
            "errors": errors if errors else None,
            "message": f"Successfully deleted {deleted_count}/{len(video_ids)} videos"
        }
        
    except Exception as e:
        logger.error(f"[VideoBatchDelete] Batch delete failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch delete failed: {str(e)}"
        )


@router.delete("/video/{video_id}")
async def delete_video(video_id: str) -> Dict[str, Any]:
    """
    Delete a video from database and storage.
    
    Args:
        video_id: Video ID or job ID
        
    Returns:
        Deletion result
    """
    try:
        from ..services.supabase_client import get_supabase_service_instance
        
        logger.info(f"[VideoDelete] Deleting video: {video_id}")
        
        supabase = get_supabase_service_instance()
        
        # Get video record from database
        videos = supabase._table_select(
            "video_jobs",
            "*",
            filters=[("eq", "job_id", video_id)]
        )
        
        if not videos or len(videos) == 0:
            raise HTTPException(status_code=404, detail=f"Video {video_id} not found")
        
        video = videos[0]
        
        # Delete from storage if URL exists
        video_url = video.get("output_url")
        if video_url:
            try:
                # Extract file path from URL
                # URL format: https://....supabase.co/storage/v1/object/public/video-outputs/{filename}.mp4
                if "/video-outputs/" in video_url:
                    filename = video_url.split("/video-outputs/")[1]
                    supabase.client.storage.from_("video-outputs").remove([filename])
                    logger.info(f"[VideoDelete] Deleted from storage: {filename}")
            except Exception as storage_error:
                logger.warning(f"[VideoDelete] Storage deletion failed: {storage_error}")
        
        # Delete from database
        supabase._table_delete("video_jobs", filters=[("eq", "job_id", video_id)])
        
        logger.info(f"[VideoDelete] Video {video_id} deleted successfully")
        
        return {
            "success": True,
            "video_id": video_id,
            "message": "Video deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VideoDelete] Deletion failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete video: {str(e)}"
        )


@router.get("/video/{video_id}/download")
async def download_video(video_id: str):
    """
    Download a video file.
    
    Args:
        video_id: Video ID or job ID
        
    Returns:
        Video file for download
    """
    try:
        from ..services.supabase_client import get_supabase_service_instance
        from fastapi.responses import StreamingResponse, RedirectResponse
        import requests
        
        logger.info(f"[VideoDownload] Downloading video: {video_id}")
        
        supabase = get_supabase_service_instance()
        
        # Get video record
        videos = supabase._table_select(
            "video_jobs",
            "*",
            filters=[("eq", "job_id", video_id)]
        )
        
        if not videos or len(videos) == 0:
            raise HTTPException(status_code=404, detail=f"Video {video_id} not found")
        
        video = videos[0]
        video_url = video.get("output_url")
        
        if not video_url:
            raise HTTPException(status_code=404, detail="Video file not available")
        
        # Redirect to Supabase public URL (simplest approach)
        logger.info(f"[VideoDownload] Redirecting to: {video_url}")
        return RedirectResponse(url=video_url)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VideoDownload] Download failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download video: {str(e)}"
        )


@router.post("/video/{video_id}/thumbnail")
async def generate_video_thumbnail(video_id: str):
    """
    Generate thumbnail from video's first frame.
    
    Args:
        video_id: Video ID
        
    Returns:
        Thumbnail URL or base64 encoded image
    """
    try:
        from ..services.supabase_client import get_supabase_service_instance
        import base64
        
        logger.info(f"[VideoThumbnail] Generating thumbnail for: {video_id}")
        
        supabase = get_supabase_service_instance()
        
        # Get video record
        videos = supabase._table_select(
            "video_jobs",
            "*",
            filters=[("eq", "job_id", video_id)]
        )
        
        if not videos or len(videos) == 0:
            raise HTTPException(status_code=404, detail=f"Video {video_id} not found")
        
        video = videos[0]
        video_url = video.get("output_url")
        
        if not video_url:
            raise HTTPException(status_code=404, detail="Video file not available")
        
        # Generate thumbnail from first frame
        try:
            # Download video temporarily
            import requests
            response = requests.get(video_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video:
                for chunk in response.iter_content(chunk_size=8192):
                    tmp_video.write(chunk)
                tmp_video_path = tmp_video.name
            
            # Extract first frame
            try:
                from moviepy import VideoFileClip
                
                clip = VideoFileClip(tmp_video_path)
                # Get frame at 1 second (skip intro glitches)
                frame_time = min(1.0, clip.duration / 2)
                frame = clip.get_frame(frame_time)
                clip.close()
                
                # Convert numpy array to PIL Image
                img = Image.fromarray(frame)
                
                # Resize to thumbnail size (320x180 for 16:9)
                img.thumbnail((320, 180), Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                # Update video record with thumbnail
                supabase._table_update(
                    "video_jobs",
                    {"thumbnail_base64": img_base64},
                    filters=[("eq", "job_id", video_id)]
                )
                
                logger.info(f"[VideoThumbnail] Thumbnail generated successfully for {video_id}")
                
                return {
                    "success": True,
                    "video_id": video_id,
                    "thumbnail_base64": img_base64,
                    "message": "Thumbnail generated successfully"
                }
                
            finally:
                # Cleanup temp file
                if os.path.exists(tmp_video_path):
                    os.unlink(tmp_video_path)
                    
        except Exception as frame_error:
            logger.error(f"[VideoThumbnail] Frame extraction failed: {frame_error}")
            # Return a placeholder or error
            return {
                "success": False,
                "video_id": video_id,
                "error": str(frame_error),
                "message": "Thumbnail generation failed"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VideoThumbnail] Thumbnail generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate thumbnail: {str(e)}"
        )


# HeyGen Video Generation Endpoint
@router.post("/video/heygen/generate")
async def generate_heygen_video(
    script: str = Form(..., description="Textul pentru video (max 1000 caractere)"),
    avatar_id: Optional[str] = Form(None, description="ID-ul avatarului HeyGen"),
    voice_id: Optional[str] = Form(None, description="ID-ul vocii"),
    style: str = Form("realistic", description="Stilul video: realistic, animated, cartoon, documentary, presentation"),
    quality: str = Form("high", description="Calitatea video: low, medium, high, ultra"),
    language: str = Form("ro", description="Limba pentru voice-over"),
    background_tasks: BackgroundTasks = None
):
    """
    Generează un video profesional folosind HeyGen API cu avatar vorbitor.
    
    - **script**: Textul care va fi rostit de avatar (max 1000 caractere)
    - **avatar_id**: ID avatar HeyGen (opțional, folosește default dacă lipsește)
    - **voice_id**: ID voce HeyGen (opțional)
    - **style**: Stilul video (realistic, animated, cartoon, documentary, presentation)
    - **quality**: Calitatea (low, medium, high, ultra)
    - **language**: Limba (ro, en, etc.)
    
    Returns:
        Dict cu status, video_id și URL-ul video-ului când e gata
    """
    try:
        from ..services.heygen_service import (
            get_heygen_service,
            HeyGenVideoRequest,
            HeyGenVideoStyle,
            HeyGenVideoQuality
        )
        from fastapi import HTTPException
        import os
        import httpx
        
        # FAZA 2.6: HeyGen 400/401 clar dacă lipsește cheia, 401 clar dacă e invalidă
        api_key = os.getenv("HEYGEN_API_KEY")
        if not api_key:
            raise HTTPException(400, detail="HEYGEN_API_KEY not configured")
        
        # Validare text
        if len(script) > 1000:
            raise HTTPException(
                status_code=400,
                detail="Script-ul nu poate depăși 1000 caractere"
            )
        
        # Creează request pentru HeyGen
        heygen_request = HeyGenVideoRequest(
            script=script,
            avatar_id=avatar_id,
            voice_id=voice_id,
            style=HeyGenVideoStyle(style),
            quality=HeyGenVideoQuality(quality),
            language=language,
            subtitles=True,  # Întotdeauna cu subtitrări
            background_music=False
        )
        
        # Call HeyGen service cu httpx direct pentru 401 handling
        async with httpx.AsyncClient(timeout=60) as client:
            payload = {
                "script": script,
                "style": style,
                "quality": quality,
                "language": language,
                "avatar_id": avatar_id,
                "voice_id": voice_id
            }
            
            r = await client.post(
                "https://api.heygen.com/v1/video/generate",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
            )
            if r.status_code == 401:
                raise HTTPException(401, detail="HeyGen 401 Unauthorized – invalid API key")
            if r.status_code >= 400:
                raise HTTPException(r.status_code, detail=f"HeyGen error: {r.text[:180]}")
            
            result_data = r.json()
        
        # Estimează cost (simplificat)
        estimated_cost = 0.50  # Cost estimat pentru video
        
        logger.info(f"[HeyGen] Video generation started: {result_data.get('video_id')}")
        
        return {
            "success": True,
            "message": "Video HeyGen se generează...",
            "video_id": result_data.get("video_id"),
            "status": result_data.get("status", "processing"),
            "estimated_completion": None,  # HeyGen nu returnează asta direct
            "estimated_cost": estimated_cost,
            "provider": "HeyGen",
            "style": style,
            "quality": quality,
            "check_status_url": f"/api/video/heygen/status/{result_data.get('video_id')}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[HeyGen] Video generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate HeyGen video: {str(e)}"
        )


@router.get("/video/heygen/status/{video_id}")
async def get_heygen_video_status(video_id: str):
    """
    Verifică statusul unui video HeyGen în curs de generare.
    
    - **video_id**: ID-ul video-ului returnat de /generate
    
    Returns:
        Status actual și URL video când e gata
    """
    try:
        from ..services.heygen_service import get_heygen_service
        
        service = get_heygen_service()
        result = await service.get_video_status(video_id)
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to check status: {result.error_message}"
            )
        
        response = {
            "success": True,
            "video_id": video_id,
            "status": result.status,
            "video_url": result.video_url,
            "thumbnail_url": result.thumbnail_url,
            "duration": result.duration
        }
        
        # Dacă video e gata, descarcă-l local
        if result.status == "completed" and result.video_url:
            output_path = f"generated_videos/heygen/heygen_video_{video_id}.mp4"
            download_success = await service.download_video(result.video_url, output_path)
            if download_success:
                response["local_path"] = output_path
                logger.info(f"[HeyGen] Video downloaded: {output_path}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[HeyGen] Status check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check video status: {str(e)}"
        )


@router.get("/video/heygen/avatars")
async def list_heygen_avatars():
    """
    Listează avatarele disponibile în HeyGen.
    
    Returns:
        Listă de avatare cu ID-uri și preview-uri
    """
    try:
        from ..services.heygen_service import get_heygen_service
        
        service = get_heygen_service()
        avatars = await service.list_avatars()
        
        return {
            "success": True,
            "avatars": avatars
        }
        
    except Exception as e:
        logger.error(f"[HeyGen] Failed to list avatars: {e}")
        # Return mock data dacă API-ul eșuează
        return {
            "success": True,
            "avatars": [
                {"id": "default", "name": "Professional Woman", "preview": ""},
                {"id": "business_man", "name": "Business Man", "preview": ""},
                {"id": "friendly_woman", "name": "Friendly Advisor", "preview": ""}
            ]
        }


