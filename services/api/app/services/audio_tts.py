"""
AutoPro Daune - Text-to-Speech Service
Gestionare TTS cu fallback graceful pentru Manole Video Generator
"""

import os
import asyncio
import logging
from typing import Optional
from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)

class TTSService:
    """Serviciu TTS cu suport pentru Edge-TTS și fallback graceful."""
    
    def __init__(self, voice_defaults: Optional[dict] = None):
        self.voice_defaults = voice_defaults or {
            "romanian_tts": "ro-RO-AlinaNeural",
            "clone": "ro-RO-EmilNeural"
        }
    
    def _safe_tempfile(self, suffix: str) -> str:
        """Creează temp file sigur pentru Windows."""
        with NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            return tmp.name
    
    async def _edge_tts_to_file_async(self, text: str, out_path: str, voice: str = "ro-RO-AlinaNeural"):
        """Async helper pentru Edge-TTS."""
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text=text, voice=voice)
            chunks = []
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    chunks.append(chunk["data"])
            
            with open(out_path, "wb") as f:
                for chunk_data in chunks:
                    f.write(chunk_data)
                    
            logger.info(f"TTS audio generated: {out_path}")
            return True
            
        except Exception as e:
            logger.warning(f"Edge-TTS failed: {e}")
            return False
    
    def synthesize(self, text: str, mode: str = "romanian_tts") -> Optional[str]:
        """
        Sintetizează text în audio.
        
        Args:
            text: Textul de sintetizat
            mode: Modul de voce ("romanian_tts", "clone")
            
        Returns:
            Path către fișierul audio sau None la fallback
        """
        try:
            # Generează path temporar
            audio_path = self._safe_tempfile(".mp3")
            
            # Selectează vocea
            voice = self.voice_defaults.get(mode, "ro-RO-AlinaNeural")
            
            # Rulează TTS async
            success = asyncio.run(self._edge_tts_to_file_async(text, audio_path, voice))
            
            if success and os.path.exists(audio_path):
                return audio_path
            else:
                # Cleanup la eșec
                try:
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                except Exception:
                    pass
                return None
                
        except Exception as e:
            logger.warning(f"TTS synthesis failed, continuing without audio: {e}")
            return None
    
    def cleanup_audio_file(self, audio_path: str):
        """Șterge fișierul audio temporar."""
        try:
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
                logger.debug(f"Cleaned up audio file: {audio_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup audio file {audio_path}: {e}")


class ManoleVoiceCloner:
    """
    Manole Voice Cloning Service.
    Uses ElevenLabs for professional voice cloning, with Edge-TTS fallback.
    """
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "manole_voice")
        self.use_elevenlabs = bool(self.api_key)
        
        logger.info(f"[ManoleVoice] Initialized (ElevenLabs: {self.use_elevenlabs})")
    
    async def generate_manole_voice(
        self, 
        text: str, 
        emotion: str = "professional",
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate audio with Manole's cloned voice.
        
        Args:
            text: Script text to synthesize
            emotion: Voice emotion (professional, empathetic, urgent)
            output_path: Optional custom output path
            
        Returns:
            Path to generated audio file
        """
        if not output_path:
            with NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                output_path = tmp.name
        
        try:
            if self.use_elevenlabs:
                logger.info(f"[ManoleVoice] Using ElevenLabs (emotion: {emotion})")
                return await self._generate_with_elevenlabs(text, output_path, emotion)
            else:
                logger.info(f"[ManoleVoice] Using Edge-TTS fallback")
                return await self._generate_with_edge_tts(text, output_path)
                
        except Exception as e:
            logger.error(f"[ManoleVoice] Generation failed: {e}")
            # Try fallback
            logger.info("[ManoleVoice] Attempting Edge-TTS fallback")
            return await self._generate_with_edge_tts(text, output_path)
    
    async def _generate_with_elevenlabs(
        self, 
        text: str, 
        output_path: str,
        emotion: str = "professional"
    ) -> str:
        """Generate audio using ElevenLabs API."""
        try:
            # Import ElevenLabs SDK
            from elevenlabs import VoiceSettings, generate, save
            
            # Voice settings based on emotion
            stability_map = {
                "professional": 0.71,
                "empathetic": 0.50,
                "urgent": 0.30
            }
            
            similarity_boost_map = {
                "professional": 0.75,
                "empathetic": 0.85,
                "urgent": 0.65
            }
            
            # Generate audio
            audio = generate(
                text=text,
                voice=self.voice_id,
                api_key=self.api_key,
                model="eleven_multilingual_v2",  # Supports Romanian
                voice_settings=VoiceSettings(
                    stability=stability_map.get(emotion, 0.71),
                    similarity_boost=similarity_boost_map.get(emotion, 0.75),
                    style=0.0,
                    use_speaker_boost=True
                )
            )
            
            # Save audio to file
            save(audio, output_path)
            
            logger.info(f"[ManoleVoice] ElevenLabs audio saved: {output_path}")
            return output_path
            
        except ImportError:
            logger.warning("[ManoleVoice] elevenlabs package not installed. Install with: pip install elevenlabs")
            raise
        except Exception as e:
            logger.error(f"[ManoleVoice] ElevenLabs generation failed: {e}")
            raise
    
    async def _generate_with_edge_tts(self, text: str, output_path: str) -> str:
        """Fallback to Edge-TTS Romanian voice."""
        try:
            import edge_tts
            
            # Use Romanian male voice (Emil) for Manole
            voice = "ro-RO-EmilNeural"
            
            communicate = edge_tts.Communicate(text=text, voice=voice)
            await communicate.save(output_path)
            
            logger.info(f"[ManoleVoice] Edge-TTS audio saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"[ManoleVoice] Edge-TTS fallback failed: {e}")
            raise
    
    def cleanup(self, audio_path: str):
        """Clean up temporary audio file."""
        try:
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
                logger.debug(f"[ManoleVoice] Cleaned up: {audio_path}")
        except Exception as e:
            logger.warning(f"[ManoleVoice] Cleanup failed: {e}")
