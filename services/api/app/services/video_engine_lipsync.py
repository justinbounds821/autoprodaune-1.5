# services/api/app/services/video_engine_lipsync.py
"""
Internal video engine with lip-sync capabilities.
SRP: Video generation with lip-sync, no business logic.
"""
import os
import uuid
import tempfile
import subprocess
import asyncio
import glob
import logging
from typing import Optional
import httpx

from .job_store import create_job, set_status
from .voice_elevenlabs import tts_elevenlabs

logger = logging.getLogger(__name__)

# Configuration from environment
FPS = os.getenv("VIDEO_ENGINE_FPS", "25")
CANVAS = os.getenv("VIDEO_ENGINE_CANVAS", "1280x720")
BACKEND = os.getenv("LIPSYNC_BACKEND", "sadtalker").lower()

async def _download_file(url: str, suffix: str) -> str:
    """
    Download a file from URL to temporary location.
    
    Args:
        url: URL to download
        suffix: File suffix (e.g., '.png', '.mp4')
        
    Returns:
        Path to downloaded file
        
    Raises:
        Exception: If download fails
    """
    tmp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.get(url)
            response.raise_for_status()
            tmp_file.write(response.content)
            tmp_file.flush()
        
        logger.info(f"Downloaded file from {url} to {tmp_file.name}")
        return tmp_file.name
        
    except Exception as e:
        tmp_file.close()
        os.remove(tmp_file.name)
        logger.error(f"Failed to download {url}: {e}")
        raise Exception(f"Download failed: {e}")
    finally:
        tmp_file.close()

def _mp3_to_wav(mp3_bytes: bytes) -> str:
    """
    Convert MP3 audio to WAV format for lip-sync processing.
    
    Args:
        mp3_bytes: MP3 audio data
        
    Returns:
        Path to WAV file
        
    Raises:
        Exception: If conversion fails
    """
    # Write MP3 to temporary file
    mp3_fd, mp3_path = tempfile.mkstemp(suffix=".mp3")
    try:
        with os.fdopen(mp3_fd, "wb") as f:
            f.write(mp3_bytes)
        
        # Convert to WAV
        wav_path = mp3_path.replace(".mp3", ".wav")
        result = subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", mp3_path,
            "-ac", "1",  # Mono
            "-ar", "16000",  # 16kHz sample rate
            wav_path
        ], capture_output=True, text=True, check=True)
        
        logger.info(f"Converted MP3 to WAV: {wav_path}")
        return wav_path
        
    except subprocess.CalledProcessError as e:
        logger.error(f"MP3 to WAV conversion failed: {e.stderr}")
        raise Exception(f"Audio conversion failed: {e.stderr}")
    finally:
        # Clean up MP3 file
        try:
            os.remove(mp3_path)
        except Exception:
            pass

async def _run_sadtalker(image_path: Optional[str], video_path: Optional[str], 
                        wav_path: str, out_path: str) -> None:
    """
    Run SadTalker lip-sync generation.
    
    Args:
        image_path: Path to source image (optional)
        video_path: Path to source video (optional)
        wav_path: Path to WAV audio file
        out_path: Output video path
        
    Raises:
        Exception: If SadTalker fails
    """
    logger.info("Starting SadTalker lip-sync generation")
    
    py = "python"
    base = "third_party/SadTalker"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    # Build SadTalker command
    cmd = [
        py, os.path.join(base, "inference.py"),
        "--driven_audio", wav_path,
        "--enhancer", "gfpgan",
        "--preprocess", "full",
        "--size", "512",
        "--fps", FPS,
        "--save_dir", os.path.dirname(out_path)
    ]
    
    # Add source (image or video)
    if image_path:
        cmd += ["--source_image", image_path]
    elif video_path:
        cmd += ["--source_image", video_path]
    else:
        raise RuntimeError("No avatar_image_url or avatar_video_url provided")
    
    try:
        # Run SadTalker
        result = subprocess.run(cmd, check=True, cwd=base, 
                              capture_output=True, text=True)
        
        # Find the generated video file
        output_dir = os.path.dirname(out_path)
        video_files = sorted(
            glob.glob(os.path.join(output_dir, "*.mp4")), 
            key=os.path.getmtime
        )
        
        if not video_files:
            raise RuntimeError("SadTalker produced no output video")
        
        # Normalize the output video
        input_video = video_files[-1]
        normalize_cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", input_video,
            "-vf", f"scale={CANVAS},fps={FPS}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", out_path
        ]
        
        subprocess.run(normalize_cmd, check=True)
        logger.info(f"SadTalker completed: {out_path}")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"SadTalker failed: {e.stderr}")
        raise Exception(f"SadTalker generation failed: {e.stderr}")

async def _run_wav2lip(image_path: Optional[str], video_path: Optional[str],
                      wav_path: str, out_path: str) -> None:
    """
    Run Wav2Lip lip-sync generation.
    
    Args:
        image_path: Path to source image (optional)
        video_path: Path to source video (optional)
        wav_path: Path to WAV audio file
        out_path: Output video path
        
    Raises:
        Exception: If Wav2Lip fails
    """
    logger.info("Starting Wav2Lip lip-sync generation")
    
    py = "python"
    base = "third_party/Wav2Lip"
    ckpt = os.path.join(base, "checkpoints", "Wav2Lip.pth")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    # Prepare source video
    src_path = video_path or image_path
    if src_path and src_path.endswith((".jpg", ".jpeg", ".png")):
        # Convert static image to video with subtle movement
        tmp_vid = out_path.replace(".mp4", "_src.mp4")
        img_to_vid_cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", src_path,
            "-t", "30",  # 30 seconds
            "-vf", f"scale={CANVAS},fps={FPS},zoompan=z='min(zoom+0.0005,1.05)':d=1:x='iw/2':y='ih/2'",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", tmp_vid
        ]
        
        try:
            subprocess.run(img_to_vid_cmd, check=True)
            src_path = tmp_vid
        except subprocess.CalledProcessError as e:
            logger.warning(f"Image to video conversion failed: {e.stderr}")
            # Continue with original image
    
    # Build Wav2Lip command
    cmd = [
        py, os.path.join(base, "inference.py"),
        "--checkpoint_path", ckpt,
        "--face", src_path,
        "--audio", wav_path,
        "--outfile", out_path
    ]
    
    try:
        # Run Wav2Lip
        result = subprocess.run(cmd, check=True, cwd=base,
                              capture_output=True, text=True)
        
        # Normalize output
        normalize_cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", out_path,
            "-vf", f"scale={CANVAS},fps={FPS}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", out_path
        ]
        
        subprocess.run(normalize_cmd, check=True)
        logger.info(f"Wav2Lip completed: {out_path}")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Wav2Lip failed: {e.stderr}")
        raise Exception(f"Wav2Lip generation failed: {e.stderr}")

async def enqueue_lipsync(script: str, voice_id: Optional[str], 
                         avatar_image_url: Optional[str], 
                         avatar_video_url: Optional[str]) -> str:
    """
    Enqueue a lip-sync video generation job.
    
    Args:
        script: Text script for the video
        voice_id: Voice ID for TTS
        avatar_image_url: URL to avatar image
        avatar_video_url: URL to avatar video
        
    Returns:
        Job ID for tracking
        
    Raises:
        Exception: If job creation fails
    """
    job_id = str(uuid.uuid4())
    out_path = os.path.join(os.getcwd(), f"video_{job_id}.mp4")
    
    # Create job entry
    create_job(job_id, meta={
        "backend": BACKEND,
        "voice": voice_id,
        "script_length": len(script),
        "output_path": out_path
    })
    
    # Start background processing
    async def worker():
        try:
            set_status(job_id, "processing", progress=10)

            # 1. Generate TTS audio
            logger.info(f"Generating TTS for job {job_id}")
            mp3_data = await tts_elevenlabs(script, voice_id)
            wav_path = _mp3_to_wav(mp3_data)
            
            # 2. Download avatar assets
            img_path = None
            vid_path = None
            
            if avatar_image_url:
                logger.info(f"Downloading avatar image for job {job_id}")
                img_path = await _download_file(avatar_image_url, ".png")
            
            if avatar_video_url:
                logger.info(f"Downloading avatar video for job {job_id}")
                vid_path = await _download_file(avatar_video_url, ".mp4")

            set_status(job_id, "processing", progress=50)

            # 3. Run lip-sync generation
            logger.info(f"Starting lip-sync generation for job {job_id} using {BACKEND}")
            if BACKEND == "sadtalker":
                await _run_sadtalker(img_path, vid_path, wav_path, out_path)
            else:
                await _run_wav2lip(img_path, vid_path, wav_path, out_path)
            
            # 4. Mark as completed
            video_url = f"/api/video/video/heygen/download/{job_id}"
            set_status(job_id, "completed", progress=100,
                      video_url=video_url,
                      completed_at=asyncio.get_event_loop().time())
            
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            set_status(job_id, "failed", error=str(e))
            
        finally:
            # Clean up temporary files
            for path in [wav_path, img_path, vid_path]:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception:
                        pass
    
    # Start the worker task
    asyncio.create_task(worker())
    return job_id
