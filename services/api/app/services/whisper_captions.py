"""
Whisper Captions Service - Auto-generate video captions
Single Responsibility: Generate SRT/ASS caption files from video audio
Safe-by-default: Disabled unless ENABLE_WHISPER_CAPTIONS=true
"""
import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import subprocess

logger = logging.getLogger(__name__)


class WhisperCaptionsService:
    """
    Auto-generate captions using Whisper AI.
    Falls back to silent mode if Whisper unavailable.
    """
    
    def __init__(self):
        self.enabled = os.getenv("ENABLE_WHISPER_CAPTIONS", "false").lower() == "true"
        self.model_size = os.getenv("WHISPER_MODEL", "base")  # tiny, base, small, medium, large
        self.device = os.getenv("WHISPER_DEVICE", "cpu")  # cpu or cuda
        self.language = os.getenv("AI_CAPTIONS_LANG", "ro")
        self.model = None
        
        if not self.enabled:
            logger.info("⚠️ Whisper captions disabled (ENABLE_WHISPER_CAPTIONS=false)")
            return
        
        # Try to load Whisper model
        try:
            import whisper
            self.model = whisper.load_model(self.model_size, device=self.device)
            logger.info(f"✅ Whisper captions enabled (model={self.model_size}, lang={self.language})")
        except ImportError:
            logger.warning("⚠️ openai-whisper not installed, captions disabled")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.enabled = False
    
    async def generate_captions(
        self, 
        video_path: str, 
        output_format: str = "srt"
    ) -> Optional[Dict[str, Any]]:
        """
        Generate captions for video file.
        Returns dict with caption file paths and metadata.
        """
        if not self.enabled or not self.model:
            logger.debug(f"Captions disabled for {video_path}")
            return None
        
        try:
            # Transcribe audio
            result = self.model.transcribe(
                video_path, 
                language=self.language,
                task="transcribe"
            )
            
            # Generate output files
            base_path = Path(video_path).with_suffix("")
            srt_path = f"{base_path}.srt"
            ass_path = f"{base_path}.ass"
            
            # Write SRT
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(self._to_srt(result["segments"]))
            
            # Write ASS (advanced subtitle format)
            with open(ass_path, "w", encoding="utf-8") as f:
                f.write(self._to_ass(result["segments"]))
            
            return {
                "srt_path": srt_path,
                "ass_path": ass_path,
                "language": result.get("language", self.language),
                "segments": len(result["segments"]),
                "text": result.get("text", "")
            }
        
        except Exception as e:
            logger.error(f"Caption generation failed for {video_path}: {e}")
            return None
    
    def _to_srt(self, segments: list) -> str:
        """Convert Whisper segments to SRT format"""
        srt_lines = []
        for i, seg in enumerate(segments, 1):
            start = self._format_timestamp(seg["start"])
            end = self._format_timestamp(seg["end"])
            text = seg["text"].strip()
            srt_lines.append(f"{i}\n{start} --> {end}\n{text}\n")
        return "\n".join(srt_lines)
    
    def _to_ass(self, segments: list) -> str:
        """Convert Whisper segments to ASS format"""
        header = """[Script Info]
Title: AutoPro Captions
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        for seg in segments:
            start = self._format_ass_timestamp(seg["start"])
            end = self._format_ass_timestamp(seg["end"])
            text = seg["text"].strip().replace("\n", "\\N")
            events.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")
        
        return header + "\n".join(events)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds as SRT timestamp (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _format_ass_timestamp(self, seconds: float) -> str:
        """Format seconds as ASS timestamp (H:MM:SS.cc)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:05.2f}"
    
    def get_health(self) -> Dict[str, Any]:
        """Health check for caption service"""
        return {
            "enabled": self.enabled,
            "model": self.model_size if self.enabled else None,
            "device": self.device if self.enabled else None,
            "language": self.language
        }


# Singleton instance
_instance = None

def get_whisper_service() -> WhisperCaptionsService:
    """Get or create WhisperCaptionsService singleton"""
    global _instance
    if _instance is None:
        _instance = WhisperCaptionsService()
    return _instance
