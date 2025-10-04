# services/api/app/services/voice_elevenlabs.py
"""
Text-to-Speech service using ElevenLabs API with local fallback.
SRP: TTS functionality only, no business logic.
"""
import os
import httpx
import tempfile
import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ElevenLabs API configuration
ELEVEN_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech"

async def tts_elevenlabs(text: str, voice: Optional[str] = None) -> bytes:
    """
    Generate speech using ElevenLabs API.
    
    Args:
        text: Text to convert to speech
        voice: Voice ID (optional, uses default if not provided)
        
    Returns:
        MP3 audio data as bytes
        
    Raises:
        Exception: If API call fails
    """
    api_key = os.getenv("ELEVENLABS_API_KEY", "")
    voice_id = voice or os.getenv("ELEVENLABS_VOICE_ID", "Rachel")
    
    if not api_key:
        logger.warning("ElevenLabs API key not configured, using fallback")
        return tts_fallback_local(text)
    
    headers = {
        "xi-api-key": api_key,
        "accept": "audio/mpeg",
        "content-type": "application/json"
    }
    
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{ELEVEN_TTS_URL}/{voice_id}",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            logger.info(f"Generated TTS for {len(text)} characters using ElevenLabs")
            return response.content  # MP3 data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"ElevenLabs API error: {e.response.status_code} - {e.response.text}")
        raise Exception(f"ElevenLabs API error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"ElevenLabs request failed: {e}")
        raise Exception(f"ElevenLabs request failed: {e}")

def tts_fallback_local(text: str) -> bytes:
    """
    Generate speech using local TTS (Windows SAPI or espeak).
    
    Args:
        text: Text to convert to speech
        
    Returns:
        MP3 audio data as bytes
        
    Raises:
        Exception: If local TTS fails
    """
    logger.info(f"Using local TTS fallback for {len(text)} characters")
    
    # Create temporary files
    wav_path = None
    mp3_path = None
    
    try:
        # Create temporary WAV file
        wav_fd, wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(wav_fd)
        
        # Create temporary MP3 file
        mp3_fd, mp3_path = tempfile.mkstemp(suffix=".mp3")
        os.close(mp3_fd)
        
        # Generate speech using local TTS
        if os.name == "nt":  # Windows
            # Use Windows SAPI
            escaped_text = text.replace('"', '""')  # Escape quotes for PowerShell
            ps_command = (
                f'$s=New-Object -ComObject SAPI.SpVoice; '
                f'$st=New-Object -ComObject SAPI.SpFileStream; '
                f'$st.Open("{wav_path}", 3); '
                f'$s.AudioOutputStream=$st; '
                f'$s.Speak("{escaped_text}"); '
                f'$st.Close();'
            )
            
            result = subprocess.run([
                "powershell", "-NoProfile", "-Command", ps_command
            ], capture_output=True, text=True, check=True)
            
        else:  # Linux/Mac
            # Use espeak
            result = subprocess.run([
                "espeak", text, "-w", wav_path
            ], capture_output=True, text=True, check=True)
        
        # Convert WAV to MP3 using FFmpeg
        ffmpeg_result = subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", wav_path, mp3_path
        ], capture_output=True, text=True, check=True)
        
        # Read MP3 data
        with open(mp3_path, "rb") as f:
            mp3_data = f.read()
        
        logger.info(f"Generated {len(mp3_data)} bytes of MP3 audio using local TTS")
        return mp3_data
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Local TTS failed: {e.stderr}")
        raise Exception(f"Local TTS failed: {e.stderr}")
    except Exception as e:
        logger.error(f"Local TTS error: {e}")
        raise Exception(f"Local TTS error: {e}")
    finally:
        # Clean up temporary files
        for path in [wav_path, mp3_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass

def get_available_voices() -> list[dict]:
    """
    Get list of available voices from ElevenLabs.
    
    Returns:
        List of voice dictionaries
    """
    api_key = os.getenv("ELEVENLABS_API_KEY", "")
    if not api_key:
        return [{"id": "local", "name": "Local TTS", "category": "fallback"}]
    
    try:
        headers = {"xi-api-key": api_key}
        response = httpx.get(
            "https://api.elevenlabs.io/v1/voices",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        voices_data = response.json()
        return voices_data.get("voices", [])
        
    except Exception as e:
        logger.error(f"Failed to get voices: {e}")
        return [{"id": "local", "name": "Local TTS", "category": "fallback"}]

def validate_voice_id(voice_id: str) -> bool:
    """
    Validate if a voice ID exists.
    
    Args:
        voice_id: Voice ID to validate
        
    Returns:
        True if voice exists, False otherwise
    """
    if voice_id == "local":
        return True
    
    voices = get_available_voices()
    return any(voice.get("voice_id") == voice_id for voice in voices)
