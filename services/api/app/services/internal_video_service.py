"""
Internal Video Generation Service - Fără costuri externe
========================================================
Generare video profesională folosind doar tool-uri proprii.

Componente:
- ElevenLabs pentru voce (text-to-speech)
- OpenAI pentru generare script/îmbunătățire text
- FFmpeg pentru procesare video
- PIL pentru grafică
- MoviePy pentru compoziție video

Zero costuri pentru HeyGen, Pika sau alte servicii externe.
"""

import os
import asyncio
import logging
import tempfile
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
import io

# PIL pentru grafică
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# FFmpeg și MoviePy
try:
    from imageio_ffmpeg import get_ffmpeg_exe
    os.environ["IMAGEIO_FFMPEG_EXE"] = get_ffmpeg_exe()
except:
    pass

try:
    from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, TextClip, ColorClip, VideoFileClip
except:
    from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip, ColorClip, VideoFileClip

logger = logging.getLogger(__name__)


class InternalVideoService:
    """Serviciu intern pentru generare video - zero costuri externe."""
    
    def __init__(self):
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.output_dir = Path("generated_videos/internal")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Importă Supabase pentru date reale
        from .supabase_client import get_supabase_service_instance
        self.supabase = get_supabase_service_instance()
        
        # Voice IDs pentru ElevenLabs
        self.voice_ids = {
            "professional": os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),  # Rachel
            "empathetic": "EXAVITQu4vr4xnSDxMaL",  # Bella
            "confident": "pNInz6obpgDQGcFmaJgB",  # Adam
            "manole": os.getenv("ELEVENLABS_VOICE_ID", "manole_voice")
        }
    
    async def generate_video_from_lead(self, lead_id: str, video_type: str = "testimonial") -> Dict[str, Any]:
        """
        Generează video bazat pe un lead real din sistem.
        
        Args:
            lead_id: ID-ul lead-ului din baza de date
            video_type: Tipul video (testimonial, update, reminder)
            
        Returns:
            Dict cu rezultatul generării
        """
        try:
            # Obține datele lead-ului
            lead_data = self.supabase._table_select("leads", "*", f"id.eq.{lead_id}")
            if not lead_data:
                return {"success": False, "error": f"Lead {lead_id} not found"}
            
            lead = lead_data[0]
            
            # Generează script personalizat cu OpenAI
            script = await self._generate_script_from_lead(lead, video_type)
            
            # Determină stilul vocii bazat pe tipul de video
            voice_style = "empathetic" if video_type == "testimonial" else "professional"
            
            # Generează video
            return await self.generate_video(
                text=script,
                voice_style=voice_style,
                background_type="gradient",
                aspect_ratio="16:9",
                resolution="1080p"
            )
            
        except Exception as e:
            logger.error(f"[Lead Video] Failed for lead {lead_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_daily_summary_video(self) -> Dict[str, Any]:
        """
        Generează video cu sumarul zilnic - lead-uri noi, cazuri finalizate, statistici.
        """
        try:
            # Obține statistici zilnice
            from datetime import datetime, timedelta
            today = datetime.now().date()
            
            leads_today = self.supabase._table_select(
                "leads", 
                "*", 
                f"created_at.gte.{today.isoformat()}"
            )
            
            completed_today = self.supabase._table_select(
                "leads",
                "*",
                f"status.eq.completed,updated_at.gte.{today.isoformat()}"
            )
            
            revenues_today = self.supabase._table_select(
                "revenues",
                "*",
                f"timestamp.gte.{today.isoformat()}"
            )
            
            total_revenue = sum(float(r.get("amount", 0)) for r in revenues_today)
            
            # Generează script cu statistici
            script = f"""
            Bună ziua! Iată sumarul pentru ziua de {today.strftime('%d %B %Y')}:
            
            📊 Activitate:
            - {len(leads_today)} lead-uri noi
            - {len(completed_today)} cazuri finalizate
            - {total_revenue:.2f} RON venituri generate
            
            🎯 Performanță excelentă! Continuăm cu același ritm mâine.
            AutoPro Daune - Partenerul tău în recuperarea despăgubirilor.
            """
            
            return await self.generate_video(
                text=script,
                voice_style="confident",
                background_type="gradient",
                aspect_ratio="16:9",
                resolution="1080p"
            )
            
        except Exception as e:
            logger.error(f"[Daily Summary] Failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_script_from_lead(self, lead: Dict[str, Any], video_type: str) -> str:
        """Generează script personalizat cu OpenAI bazat pe datele lead-ului."""
        try:
            if not self.openai_api_key:
                # Fallback fără OpenAI - script template
                return self._generate_template_script(lead, video_type)
            
            import openai
            openai.api_key = self.openai_api_key
            
            # Prompt pentru OpenAI
            prompt = f"""
            Generează un script de 30-45 secunde pentru un video {video_type} despre următorul caz:
            
            Client: {lead.get('name', 'Client')}
            Tip daună: {lead.get('damage_type', 'accident auto')}
            Detalii: {lead.get('details', 'Accident rutier')}
            Status: {lead.get('status', 'în proces')}
            
            Script-ul trebuie să fie:
            - Professional și empatic
            - În limba română
            - Motivant și încurajator
            - Să menționeze AutoPro Daune ca partener de încredere
            
            Returnează DOAR textul scriptului, fără alte explicații.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Ești un copywriter expert în domeniul asigurărilor și recuperării despăgubirilor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            script = response.choices[0].message.content.strip()
            return script
            
        except Exception as e:
            logger.warning(f"OpenAI script generation failed: {e}. Using template.")
            return self._generate_template_script(lead, video_type)
    
    def _generate_template_script(self, lead: Dict[str, Any], video_type: str) -> str:
        """Generează script din template când OpenAI nu e disponibil."""
        name = lead.get('name', 'Client')
        damage_type = lead.get('damage_type', 'accident auto')
        
        if video_type == "testimonial":
            return f"""
            Bună ziua, sunt {name}. 
            Am avut un {damage_type} și am apelat la AutoPro Daune pentru recuperarea despăgubirilor.
            Echipa lor profesionistă m-a ajutat pas cu pas în întreg procesul.
            Recomand cu încredere AutoPro Daune tuturor celor care au nevoie de asistență în recuperarea despăgubirilor.
            """
        elif video_type == "update":
            return f"""
            Update pentru dosarul {name}:
            Cazul de {damage_type} este în curs de procesare.
            Echipa AutoPro Daune lucrează activ pentru obținerea celei mai bune despăgubiri.
            Vă vom ține la curent cu progresul.
            """
        else:  # reminder
            return f"""
            Reminder pentru {name}:
            Dosarul dvs. de {damage_type} necesită atenție.
            Vă rugăm să ne contactați pentru detalii suplimentare.
            AutoPro Daune - Suntem aici pentru dvs.
            """
    
    async def generate_video(
        self,
        text: str,
        voice_style: str = "professional",
        background_type: str = "gradient",
        logo_path: Optional[str] = None,
        aspect_ratio: str = "16:9",
        resolution: str = "1080p"
    ) -> Dict[str, Any]:
        """
        Generează video complet - voce + vizual.
        
        Args:
            text: Textul pentru voice-over
            voice_style: Stilul vocii (professional, empathetic, confident, manole)
            background_type: Tip background (gradient, solid, image)
            logo_path: Path la logo (opțional)
            aspect_ratio: 16:9, 9:16, 1:1
            resolution: 1080p, 720p, 4k
            
        Returns:
            Dict cu video_path, audio_path, duration, size_mb
        """
        try:
            video_id = f"internal_{int(datetime.now().timestamp())}"
            logger.info(f"[Internal Video] Starting generation: {video_id}")
            
            # 1. Generează audio cu ElevenLabs
            audio_result = await self._generate_audio(text, voice_style)
            if not audio_result["success"]:
                return {
                    "success": False,
                    "error": audio_result.get("error", "Audio generation failed")
                }
            
            audio_path = audio_result["audio_path"]
            audio_duration = audio_result["duration"]
            
            # 2. Generează vizual
            visual_result = await self._generate_visual(
                duration=audio_duration,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                background_type=background_type,
                logo_path=logo_path
            )
            
            if not visual_result["success"]:
                return {
                    "success": False,
                    "error": visual_result.get("error", "Visual generation failed")
                }
            
            # 3. Combină audio + video
            final_video_path = self.output_dir / f"{video_id}.mp4"
            combine_result = await self._combine_audio_video(
                visual_path=visual_result["video_path"],
                audio_path=audio_path,
                output_path=str(final_video_path)
            )
            
            if not combine_result["success"]:
                return {
                    "success": False,
                    "error": combine_result.get("error", "Combining failed")
                }
            
            # Calculează dimensiune
            file_size_mb = final_video_path.stat().st_size / (1024 * 1024)
            
            logger.info(f"[Internal Video] ✅ Generated: {final_video_path} ({file_size_mb:.2f}MB)")
            
            return {
                "success": True,
                "video_id": video_id,
                "video_path": str(final_video_path),
                "audio_path": audio_path,
                "duration_seconds": audio_duration,
                "file_size_mb": round(file_size_mb, 2),
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "provider": "Internal (ElevenLabs + FFmpeg)",
                "cost": 0.0  # Zero cost!
            }
            
        except Exception as e:
            logger.error(f"[Internal Video] Generation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_audio(self, text: str, voice_style: str) -> Dict[str, Any]:
        """Generează audio cu ElevenLabs."""
        try:
            if not self.elevenlabs_api_key:
                return {
                    "success": False,
                    "error": "ELEVENLABS_API_KEY not configured"
                }
            
            voice_id = self.voice_ids.get(voice_style, self.voice_ids["professional"])
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"ElevenLabs API error {response.status}: {error_text}"
                        }
                    
                    audio_content = await response.read()
            
            # Salvează audio
            audio_filename = f"audio_{int(datetime.now().timestamp())}.mp3"
            audio_path = str(self.output_dir / audio_filename)
            
            with open(audio_path, "wb") as f:
                f.write(audio_content)
            
            # Calculează durata (aproximativ - 150 cuvinte/minut)
            word_count = len(text.split())
            estimated_duration = (word_count / 150) * 60  # secunde
            
            # Verifică durata reală cu FFmpeg dacă e disponibil
            try:
                from moviepy.editor import AudioFileClip
                audio_clip = AudioFileClip(audio_path)
                actual_duration = audio_clip.duration
                audio_clip.close()
            except:
                actual_duration = estimated_duration
            
            logger.info(f"[ElevenLabs] Audio generated: {audio_path} ({actual_duration:.1f}s)")
            
            return {
                "success": True,
                "audio_path": audio_path,
                "duration": actual_duration,
                "word_count": word_count
            }
            
        except Exception as e:
            logger.error(f"[ElevenLabs] Audio generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_visual(
        self,
        duration: float,
        aspect_ratio: str,
        resolution: str,
        background_type: str,
        logo_path: Optional[str]
    ) -> Dict[str, Any]:
        """Generează partea vizuală a video-ului."""
        try:
            # Determină rezoluția
            res_map = {
                "720p": (1280, 720),
                "1080p": (1920, 1080),
                "4k": (3840, 2160)
            }
            width, height = res_map.get(resolution, (1920, 1080))
            
            # Ajustează pentru aspect ratio
            if aspect_ratio == "9:16":  # Vertical (TikTok, Stories)
                width, height = height * 9 // 16, height
            elif aspect_ratio == "1:1":  # Square (Instagram)
                width = height
            
            # Creează background
            if background_type == "gradient":
                image = self._create_gradient_background(width, height)
            elif background_type == "solid":
                image = self._create_solid_background(width, height, color="#1a1a2e")
            else:
                image = self._create_gradient_background(width, height)
            
            # Adaugă logo dacă există
            if logo_path and os.path.exists(logo_path):
                image = self._add_logo(image, logo_path)
            
            # Adaugă text decorativ (opțional)
            image = self._add_branding(image, "AutoPro Daune")
            
            # Salvează ca imagine temporară
            temp_image_path = str(self.output_dir / f"frame_{int(datetime.now().timestamp())}.png")
            image.save(temp_image_path, "PNG")
            
            # Creează video din imagine statică
            video_path = str(self.output_dir / f"visual_{int(datetime.now().timestamp())}.mp4")
            
            # Folosește MoviePy pentru a crea video
            clip = ImageClip(temp_image_path).with_duration(duration)
            clip.write_videofile(
                video_path,
                fps=24,
                codec='libx264',
                audio=False,
                preset='medium',
                logger=None  # Suppress MoviePy logs
            )
            clip.close()
            
            # Șterge imaginea temporară
            os.remove(temp_image_path)
            
            logger.info(f"[Visual] Generated: {video_path} ({width}x{height}, {duration:.1f}s)")
            
            return {
                "success": True,
                "video_path": video_path,
                "resolution": f"{width}x{height}",
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"[Visual] Generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_gradient_background(self, width: int, height: int) -> Image.Image:
        """Creează un background cu gradient elegant."""
        # Gradient de la albastru închis la violet
        image = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(image)
        
        # Gradient vertical
        for y in range(height):
            # Culori: #1a1a2e -> #16213e -> #0f3460
            r = int(26 + (15 - 26) * (y / height))
            g = int(26 + (33 - 26) * (y / height))
            b = int(46 + (96 - 46) * (y / height))
            draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))
        
        return image
    
    def _create_solid_background(self, width: int, height: int, color: str) -> Image.Image:
        """Creează un background solid."""
        # Convert hex to RGB
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        return Image.new("RGB", (width, height), rgb)
    
    def _add_logo(self, image: Image.Image, logo_path: str) -> Image.Image:
        """Adaugă logo în colțul imaginii."""
        try:
            logo = Image.open(logo_path)
            # Resize logo (max 15% din lățime)
            max_width = int(image.width * 0.15)
            ratio = max_width / logo.width
            new_height = int(logo.height * ratio)
            logo = logo.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Poziție: colț dreapta sus cu padding
            x = image.width - logo.width - 40
            y = 40
            
            # Paste cu transparență
            if logo.mode == 'RGBA':
                image.paste(logo, (x, y), logo)
            else:
                image.paste(logo, (x, y))
            
            return image
        except Exception as e:
            logger.warning(f"Failed to add logo: {e}")
            return image
    
    def _add_branding(self, image: Image.Image, text: str) -> Image.Image:
        """Adaugă text branding în partea de jos."""
        try:
            draw = ImageDraw.Draw(image)
            
            # Încearcă să folosească un font frumos
            try:
                font = ImageFont.truetype("arial.ttf", 48)
            except:
                font = ImageFont.load_default()
            
            # Calculează poziția textului (centrat jos)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (image.width - text_width) // 2
            y = image.height - text_height - 60
            
            # Adaugă umbră
            shadow_offset = 3
            draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=(0, 0, 0, 128))
            # Text principal
            draw.text((x, y), text, font=font, fill=(255, 255, 255))
            
            return image
        except Exception as e:
            logger.warning(f"Failed to add branding: {e}")
            return image
    
    async def _combine_audio_video(
        self,
        visual_path: str,
        audio_path: str,
        output_path: str
    ) -> Dict[str, Any]:
        """Combină audio și video într-un singur fișier."""
        try:
            # Folosește MoviePy pentru combinare
            video_clip = VideoFileClip(visual_path) if visual_path.endswith('.mp4') else ImageClip(visual_path)
            audio_clip = AudioFileClip(audio_path)
            
            # Setează audio pe video
            final_clip = video_clip.with_audio(audio_clip)
            
            # Scrie fișierul final
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=24,
                preset='medium',
                logger=None
            )
            
            # Cleanup
            video_clip.close()
            audio_clip.close()
            final_clip.close()
            
            # Șterge fișierele temporare
            if os.path.exists(visual_path):
                os.remove(visual_path)
            
            logger.info(f"[Combine] ✅ Video combined: {output_path}")
            
            return {
                "success": True,
                "output_path": output_path
            }
            
        except Exception as e:
            logger.error(f"[Combine] Failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
_internal_video_service = None

def get_internal_video_service() -> InternalVideoService:
    """Returnează instanța singleton."""
    global _internal_video_service
    if _internal_video_service is None:
        _internal_video_service = InternalVideoService()
    return _internal_video_service

