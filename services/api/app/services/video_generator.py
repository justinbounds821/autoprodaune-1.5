"""
Video generation service for AutoPro Daune.

This module generates promotional video clips using AI services (Pika or HeyGen).
Videos are generated based on prompt templates combining hooks and CTAs.
"""

import os
import json
import random
import requests
import time
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import utilitare și setează FFmpeg o singură dată
from . import video_utils as vu
os.environ.setdefault("IMAGEIO_FFMPEG_EXE", vu.ensure_ffmpeg_exe())

logger = logging.getLogger(__name__)


class VideoGenerator:
    """Generate promotional videos using AI services."""
    
    def __init__(self):
        self.provider = os.getenv("VEO_PROVIDER", "Pika")
        self.api_key = os.getenv("VEO_API_KEY")
        self.output_dir = os.getenv("AUTOPOSTER_DIRECTORY", "videos/to_publish")
        # WhatsApp contact/group link (ex: wa.me sau link de grup; setabil din .env)
        self.whatsapp_link = os.getenv("WHATSAPP_LINK", "https://wa.me/40700000000")
        self.whatsapp_number = os.getenv("WHATSAPP_DIRECT_NUMBER", "40700000000")
        
        # Prompt templates
        self.hooks = [
            "Știai că peste 40% dintre șoferi nu știu cum să completeze constatarea amiabilă?",
            "În caz de accident ușor, nu intra în panică: ai pașii clari aici.",
            "Poți rezolva daunele rapid și simplu, fără drumuri inutile.",
            "Nu lăsa birocrația să-ți strice ziua după un accident.",
            "Ai avut un accident? Iată ce trebuie să faci în următoarele 10 minute.",
            "3 greșeli care încetinesc despăgubirea — evită-le acum.",
            "De ce întârzie plata? Iată cum grăbești dosarul corect.",
            "Un truc simplu care te scutește de zile pierdute pe la ghișee."
        ]
        
        self.ctas = [
            "Recomandă un prieten și primești 200 lei! 💰",
            f"Scrie-ne pe WhatsApp pentru ajutor gratuit: {self.whatsapp_link}",
            f"Intră în grupul nostru WhatsApp pentru răspunsuri rapide: {self.whatsapp_link}",
            "Completează formularul — rezolvăm noi actele și urmărirea dosarului.",
            "Primești banii în 48 de ore — află cum pe WhatsApp!"
        ]
        
        self.hashtags = [
            "#AutoProDaune", "#AsigurareAuto", "#ConstatareAmiabila",
            "#DauneAuto", "#Despagubiri", "#AccidentAuto", "#Romania",
            "#AsistentaDaune", "#SfaturiAuto", "#WhatsApp", "#200Lei"
        ]
    
    def generate_prompt(self) -> Dict[str, str]:
        """Generate a video prompt combining hook, CTA and hashtags."""
        hook = random.choice(self.hooks)
        cta = random.choice(self.ctas)
        selected_hashtags = random.sample(self.hashtags, min(5, len(self.hashtags)))
        
        script = f"{hook}\n\n{cta}"
        
        return {
            "script": script,
            "caption": f"{script}\n\n{' '.join(selected_hashtags)}",
            "hashtags": selected_hashtags
        }
    
    def call_pika_api(self, prompt: str) -> str:
        """Call Pika API to generate video."""
        if not self.api_key:
            raise ValueError("PIKA_API_KEY not configured. Please set VEO_API_KEY in .env")
            
        # Pika API implementation
        url = "https://api.pika.art/v1/generate/video"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": prompt,
            "options": {
                "frameRate": 24,
                "duration": 10,
                "resolution": "1080x1920",  # 9:16 vertical
                "style": "cinematic"
            }
        }
        
        try:
            logger.info(f"[Pika] Submitting video generation request...")
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            # Pika returnează un job ID, trebuie să așteptăm finalizarea
            job_id = result.get("id")
            if not job_id:
                raise ValueError(f"Pika API did not return job ID: {result}")
            
            logger.info(f"[Pika] Job created: {job_id}, starting polling...")
            # Poll pentru status
            return self._poll_pika_status(job_id)
                
        except Exception as e:
            logger.error(f"[VideoGenerator] Pika API error: {e}")
            raise
    
    def call_heygen_api(self, prompt: str) -> str:
        """Call HeyGen API to generate video."""
        if not self.api_key:
            raise ValueError("HEYGEN_API_KEY not configured. Please set HEYGEN_API_KEY in .env")
            
        # HeyGen API implementation
        url = "https://api.heygen.com/v2/video/generate"
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": "Kristin_public_3_20240108",
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": prompt,
                    "voice_id": "en-US-JennyNeural",
                    "speed": 1.0
                },
                "background": {
                    "type": "color",
                    "value": "#FFFFFF"
                }
            }],
            "dimension": {
                "width": 1080,
                "height": 1920  # 9:16 pentru social media
            },
            "aspect_ratio": "9:16",
            "test": False
        }
        
        try:
            logger.info(f"[HeyGen] Submitting video generation request...")
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            # HeyGen returnează video_id, trebuie să verificăm statusul
            video_id = result.get("data", {}).get("video_id")
            if not video_id:
                raise ValueError(f"HeyGen API did not return video_id: {result}")
            
            logger.info(f"[HeyGen] Video created: {video_id}, starting polling...")
            # Poll pentru status
            return self._poll_heygen_status(video_id)
                
        except Exception as e:
            logger.error(f"[VideoGenerator] HeyGen API error: {e}")
            raise
    
    def _poll_pika_status(self, job_id: str, max_attempts: int = 60) -> str:
        """
        Poll Pika API for job completion.
        
        Args:
            job_id: Pika job ID
            max_attempts: Maximum polling attempts (default 60 = 5 minutes)
            
        Returns:
            Video URL when ready
        """
        url = f"https://api.pika.art/v1/video/{job_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"[Pika] Polling attempt {attempt + 1}/{max_attempts}...")
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                result = response.json()
                
                status = result.get("status")
                logger.info(f"[Pika] Status: {status}")
                
                if status == "succeeded":
                    video_url = result.get("video_url")
                    if video_url:
                        logger.info(f"[Pika] Video ready: {video_url}")
                        return video_url
                    else:
                        raise ValueError(f"Pika job succeeded but no video_url: {result}")
                        
                elif status == "failed":
                    error_msg = result.get("error", "Unknown error")
                    raise ValueError(f"Pika generation failed: {error_msg}")
                    
                elif status in ["pending", "processing"]:
                    # Continue polling
                    time.sleep(5)  # Wait 5 seconds before next poll
                    continue
                else:
                    logger.warning(f"[Pika] Unknown status: {status}")
                    time.sleep(5)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"[Pika] Polling error: {e}")
                if attempt == max_attempts - 1:
                    raise
                time.sleep(5)
        
        raise TimeoutError(f"Pika video generation timeout after {max_attempts * 5} seconds")
    
    def _poll_heygen_status(self, video_id: str, max_attempts: int = 120) -> str:
        """
        Poll HeyGen API for video completion.
        
        Args:
            video_id: HeyGen video ID
            max_attempts: Maximum polling attempts (default 120 = 10 minutes)
            
        Returns:
            Video URL when ready
        """
        url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
        headers = {"X-Api-Key": self.api_key}
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"[HeyGen] Polling attempt {attempt + 1}/{max_attempts}...")
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                result = response.json()
                
                status = result.get("data", {}).get("status")
                logger.info(f"[HeyGen] Status: {status}")
                
                if status == "completed":
                    video_url = result.get("data", {}).get("video_url")
                    if video_url:
                        logger.info(f"[HeyGen] Video ready: {video_url}")
                        return video_url
                    else:
                        raise ValueError(f"HeyGen completed but no video_url: {result}")
                        
                elif status == "failed":
                    error_msg = result.get("data", {}).get("error", "Unknown error")
                    raise ValueError(f"HeyGen generation failed: {error_msg}")
                    
                elif status in ["pending", "processing"]:
                    # Continue polling
                    time.sleep(5)  # Wait 5 seconds before next poll
                    continue
                else:
                    logger.warning(f"[HeyGen] Unknown status: {status}")
                    time.sleep(5)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"[HeyGen] Polling error: {e}")
                if attempt == max_attempts - 1:
                    raise
                time.sleep(5)
        
        raise TimeoutError(f"HeyGen video generation timeout after {max_attempts * 5} seconds")
    
    def download_video(self, url: str, filename: str) -> str:
        """Download video from URL and save to output directory."""
        os.makedirs(self.output_dir, exist_ok=True)
        filepath = os.path.join(self.output_dir, filename)
        
        if url.startswith("https://example.com"):
            # Pentru testare, creăm un fișier video mock
            self._create_mock_video(filepath)
        else:
            # Download real video
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        
        return filepath
    
    def _create_mock_video(self, filepath: str) -> None:
        """Create a mock video file for testing."""
        # Creăm un fișier MP4 minimal valid pentru testare
        mp4_header = bytes([
            0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70,  # ftyp box
            0x69, 0x73, 0x6F, 0x6D, 0x00, 0x00, 0x02, 0x00,
            0x69, 0x73, 0x6F, 0x6D, 0x69, 0x73, 0x6F, 0x32,
            0x6D, 0x70, 0x34, 0x31, 0x00, 0x00, 0x00, 0x08,
            0x66, 0x72, 0x65, 0x65                          # free box
        ])
        
        with open(filepath, 'wb') as f:
            f.write(mp4_header)
            # Adăugăm date random pentru a face fișierul mai mare
            f.write(os.urandom(1024 * 100))  # 100KB mock video
    
    def generate_video(self) -> Dict[str, Any]:
        """Generate a new promotional video."""
        # Generate prompt
        prompt_data = self.generate_prompt()
        
        # Call appropriate API
        try:
            if self.provider.lower() == "pika":
                video_url = self.call_pika_api(prompt_data["script"])
            else:
                video_url = self.call_heygen_api(prompt_data["script"])
        except Exception as e:
            # In production, implement proper error handling
            print(f"[VideoGenerator] API call failed: {e}")
            # Return a mock URL for testing
            video_url = "https://example.com/test-video.mp4"
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"promo_{timestamp}.mp4"
        json_filename = f"promo_{timestamp}.json"
        
        # Download video (mock for testing)
        if video_url.startswith("https://example.com"):
            # Create mock video file for testing
            video_path = os.path.join(self.output_dir, video_filename)
            with open(video_path, 'wb') as f:
                f.write(b"Mock video content")
        else:
            video_path = self.download_video(video_url, video_filename)
        
        # Save metadata
        metadata = {
            "created_at": datetime.now().isoformat(),
            "provider": self.provider,
            "script": prompt_data["script"],
            "caption": prompt_data["caption"],
            "hashtags": prompt_data["hashtags"],
            "video_url": video_url,
            "filename": video_filename
        }
        
        json_path = os.path.join(self.output_dir, json_filename)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return {
            "video_path": video_path,
            "metadata_path": json_path,
            "metadata": metadata
        }


class ManoleVideoGenerator:
    """Generator pentru videoclipuri Manole cu compoziție imagine + audio."""
    
    def __init__(self, supabase_service, config: dict = None):
        self.supabase = supabase_service
        self.config = config or {}
        
        # Import servicii
        from .audio_tts import TTSService
        from .video_queue import VideoQueueSupabase
        
        self.tts_service = TTSService()
        self.queue_service = VideoQueueSupabase()
    
    def generate(self, job_id: str, payload: dict) -> str:
        """
        Orchestrează generarea videoclipului Manole.
        
        Args:
            job_id: ID-ul job-ului
            payload: Datele pentru generare
            
        Returns:
            URL-ul videoclipului generat
        """
        try:
            # Adaugă job_id în payload pentru a fi folosit în alte metode
            payload["job_id"] = job_id
            
            # Update status la processing
            self.queue_service.update_status(job_id, "processing", progress=10)
            
            # 1. Procesează imaginea și background (20%)
            frame_img = self._process_image_composition(payload)
            self.queue_service.update_status(job_id, "processing", progress=20)
            
            # 2. Generează audio (40%)
            audio_path = self._handle_audio_synthesis(payload)
            self.queue_service.update_status(job_id, "processing", progress=40)
            
            # 3. Compune videoclipul (70%)
            video_path = self._compose_video(frame_img, audio_path, payload)
            self.queue_service.update_status(job_id, "processing", progress=70)
            
            # 4. Upload și cleanup (100%)
            output_url = self._upload_and_cleanup(video_path, audio_path, job_id)
            self.queue_service.update_status(
                job_id, 
                "completed", 
                progress=100,
                output_url=output_url,
                completed_at=datetime.now().isoformat()
            )
            
            logger.info(f"Manole video {job_id} completed successfully: {output_url}")
            return output_url
            
        except Exception as e:
            logger.exception(f"Manole video generation failed for {job_id}: {e}")
            self.queue_service.update_status(
                job_id, 
                "failed", 
                error_message=str(e)
            )
            raise
    
    def _process_image_composition(self, payload: dict):
        """Procesează compoziția imaginii (person + background)."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import numpy as np
            
            # Setează dimensiunile
            resolution_map = {"1080p": (1920, 1080), "720p": (1280, 720), "480p": (854, 480)}
            size = resolution_map.get(payload.get("resolution", "1080p"), (1920, 1080))
            
            # Creează background
            bg_type = payload.get("bg_type", "color")
            bg_value = payload.get("bg_value", "#073B7A")
            
            if bg_type == "color":
                # Background color simplu
                bg_img = Image.new("RGB", size, bg_value)
            else:
                # Placeholder pentru alte tipuri
                bg_img = Image.new("RGB", size, "#073B7A")
            
            # Adaugă person (placeholder pentru acum)
            person_img = Image.new("RGBA", (400, 400), (255, 255, 255, 128))
            
            # Compune imaginile
            bg_img.paste(person_img, (760, 340), person_img)
            
            return bg_img
            
        except Exception as e:
            logger.error(f"Image composition failed: {e}")
            # Fallback la background simplu
            return Image.new("RGB", (1920, 1080), "#073B7A")
    
    def _handle_audio_synthesis(self, payload: dict) -> Optional[str]:
        """Generează audio folosind TTS."""
        tts_text = payload.get("tts_text") or payload.get("topic") or " "
        voice_mode = payload.get("voice_mode", "romanian_tts")
        
        return self.tts_service.synthesize(tts_text, voice_mode)
    
    def _compose_video(self, frame_img, audio_path: Optional[str], payload: dict) -> str:
        """Compune videoclipul final."""
        try:
            from moviepy import ImageClip, AudioFileClip, CompositeVideoClip
            import numpy as np
            
            # Setează durata
            duration = payload.get("duration_seconds", 45)
            
            # Creează clip-ul video din imagine
            video_clip = ImageClip(np.array(frame_img))
            video_clip = video_clip.with_duration(duration)
            
            # Adaugă audio dacă există (cu context manager)
            if audio_path and os.path.exists(audio_path):
                try:
                    from moviepy import AudioFileClip
                except Exception:
                    from moviepy.editor import AudioFileClip
                try:
                    with AudioFileClip(audio_path) as audio_clip:
                        if audio_clip.duration > duration:
                            audio_clip = audio_clip.subclip(0, duration)
                        elif audio_clip.duration < duration:
                            loops = int(duration / max(0.1, audio_clip.duration)) + 1
                            audio_clip = audio_clip.loop(loops).subclip(0, duration)
                        video_clip = video_clip.with_audio(audio_clip)
                except Exception as audio_e:
                    logger.warning(f"Failed to add audio: {audio_e}")
            
            # Generează path pentru output
            output_path = f"generated_videos/{payload.get('job_id', 'temp')}.mp4"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Exportă video-ul
            video_clip.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                audio_codec="aac" if audio_path else None,
                threads=2,
                preset="medium",
                verbose=False,
                logger=None
            )
            
            video_clip.close()
            
            logger.info(f"Video composed successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Video composition failed: {e}")
            raise
    
    def _upload_and_cleanup(self, video_path: str, audio_path: Optional[str], job_id: str) -> str:
        """Upload videoclipul și șterge fișierele temporare."""
        try:
            # Upload la Supabase Storage
            output_url = self.supabase.upload_from_path(
                "video-outputs", 
                f"{job_id}.mp4", 
                video_path
            )
            
            # Cleanup fișiere temporare
            try:
                if os.path.exists(video_path):
                    os.remove(video_path)
                if audio_path and os.path.exists(audio_path):
                    os.remove(audio_path)
            except Exception as cleanup_e:
                logger.warning(f"Cleanup failed: {cleanup_e}")
            
            return output_url
            
        except Exception as e:
            logger.error(f"Upload failed for {job_id}: {e}")
            raise
    
    # ============================================
    # MANOLE VIDEO GENERATOR METHODS
    # ============================================
    
    def animate_manole_photo(self, photo_path: str, duration: int = 30) -> Any:
        """
        Animate Manole's photo with Ken Burns effect (zoom + pan).
        
        Args:
            photo_path: Path to Manole's photo
            duration: Video duration in seconds
            
        Returns:
            VideoClip with animated photo
        """
        try:
            from moviepy.editor import ImageClip
            from PIL import Image
            import numpy as np
            
            logger.info(f"[ManoleVideo] Animating photo: {photo_path}")
            
            # Load and convert image
            img = Image.open(photo_path)
            
            # Resize to 9:16 aspect ratio (1080x1920 for TikTok/Instagram)
            target_width, target_height = 1080, 1920
            img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            img_array = np.array(img_resized)
            
            # Create ImageClip
            clip = ImageClip(img_array).with_duration(duration)
            
            # Ken Burns effect: slow zoom in
            def resize_func(t):
                # Zoom from 100% to 115% over the duration
                zoom = 1.0 + 0.15 * (t / duration)
                return zoom
            
            clip = clip.resized(resize_func)
            
            # Slow pan down effect
            def position_func(t):
                # Pan from top to slightly down
                y_offset = int(50 - t * 2)  # Subtle downward movement
                return ('center', y_offset)
            
            clip = clip.with_position(position_func)
            
            # Set FPS
            clip = clip.with_fps(24)
            
            logger.info(f"[ManoleVideo] Photo animated successfully ({duration}s)")
            return clip
            
        except Exception as e:
            logger.error(f"[ManoleVideo] Photo animation failed: {e}")
            raise
    
    def overlay_accident_footage(
        self, 
        main_clip: Any, 
        footage_path: str, 
        mode: str = "sequence",
        start_time: float = 10.0,
        footage_duration: float = 5.0
    ) -> Any:
        """
        Overlay accident footage in main video.
        
        Args:
            main_clip: Main video clip (Manole talking)
            footage_path: Path to accident photo/video
            mode: Display mode - 'sequence', 'pip', or 'split'
            start_time: When to show footage (seconds)
            footage_duration: How long to show footage (seconds)
            
        Returns:
            Composite video with accident footage
        """
        try:
            from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
            from PIL import Image
            import numpy as np
            
            logger.info(f"[ManoleVideo] Adding accident footage: {footage_path} (mode: {mode})")
            
            # Determine if footage is image or video
            is_image = footage_path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
            
            if is_image:
                # Load image
                img = Image.open(footage_path)
                img_resized = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                accident_clip = ImageClip(np.array(img_resized)).with_duration(footage_duration)
            else:
                # Load video
                accident_clip = VideoFileClip(footage_path)
                if accident_clip.duration > footage_duration:
                    accident_clip = accident_clip.subclip(0, footage_duration)
            
            # Apply display mode
            if mode == "pip":
                # Picture-in-picture (bottom-right corner)
                accident_clip = accident_clip.resized(width=400)  # Smaller size
                accident_clip = accident_clip.with_position(("right", "bottom"))
                accident_clip = accident_clip.with_start(start_time)
                
                final = CompositeVideoClip([main_clip, accident_clip])
                
            elif mode == "split":
                # Split screen (Manole left, accident right)
                main_resized = main_clip.resized(width=540)
                accident_resized = accident_clip.resized(width=540)
                
                main_resized = main_resized.with_position(("left", "center"))
                accident_resized = accident_resized.with_position(("right", "center"))
                
                final = CompositeVideoClip([main_resized, accident_resized], size=(1080, 1920))
                
            else:  # sequence (default)
                # Sequential: Manole → Accident → Manole continues
                part1 = main_clip.subclip(0, start_time)
                part3 = main_clip.subclip(start_time, main_clip.duration)
                
                final = concatenate_videoclips([part1, accident_clip, part3])
            
            logger.info(f"[ManoleVideo] Accident footage added successfully")
            return final
            
        except Exception as e:
            logger.error(f"[ManoleVideo] Accident footage overlay failed: {e}")
            raise
    
    def add_whatsapp_cta_overlay(self, video_clip: Any) -> Any:
        """
        Add WhatsApp CTA overlay to video (last 5 seconds).
        
        Args:
            video_clip: Video to add CTA to
            
        Returns:
            Video with CTA overlay
        """
        try:
            from moviepy.editor import TextClip, CompositeVideoClip, ImageClip
            import qrcode
            from io import BytesIO
            import numpy as np
            from PIL import Image
            
            logger.info(f"[ManoleVideo] Adding WhatsApp CTA overlay")
            
            duration = video_clip.duration
            cta_start = max(0, duration - 5)  # Last 5 seconds
            
            # Generate QR code for WhatsApp link
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(self.whatsapp_link)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert QR to numpy array
            qr_buffer = BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            qr_pil = Image.open(qr_buffer)
            qr_array = np.array(qr_pil.convert('RGB'))
            
            # Create QR clip (bottom-right, 100x100)
            qr_clip = ImageClip(qr_array).resized(width=150)
            qr_clip = qr_clip.with_position((video_clip.w - 170, video_clip.h - 170))
            qr_clip = qr_clip.with_duration(5).with_start(cta_start)
            
            # Create text CTA
            cta_text = f"📱 Contactează-mă pe WhatsApp\n{self.whatsapp_number}"
            
            txt_clip = TextClip(
                cta_text,
                fontsize=35,
                color='white',
                font='Arial-Bold',
                bg_color='rgba(0,0,0,0.7)',
                size=(video_clip.w - 200, None),
                method='caption',
                align='center'
            )
            txt_clip = txt_clip.with_position(('center', video_clip.h - 150))
            txt_clip = txt_clip.with_duration(5).with_start(cta_start)
            
            # Composite everything
            final = CompositeVideoClip([video_clip, txt_clip, qr_clip])
            
            logger.info(f"[ManoleVideo] WhatsApp CTA added successfully")
            return final
            
        except Exception as e:
            logger.error(f"[ManoleVideo] CTA overlay failed: {e}")
            # Return original video if CTA fails
            logger.warning("Returning video without CTA overlay")
            return video_clip

# CLI interface for testing
if __name__ == "__main__":
    generator = VideoGenerator()
    result = generator.generate_video()
    print(f"Video generated: {result['video_path']}")
    print(f"Metadata saved: {result['metadata_path']}")
