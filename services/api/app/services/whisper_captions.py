# services/api/app/services/whisper_captions.py
"""
Whisper-based auto-captions service.
SRP: Generate captions from audio using Whisper (local CPU/GPU).
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import shutil
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class WhisperCaptions:
    """
    Generates captions using OpenAI Whisper (local installation).
    Falls back gracefully if Whisper is not available.
    """

    def __init__(self) -> None:
        """Initialize Whisper captions service from environment."""
        self.enabled = os.getenv("AI_ENABLE_WHISPER", "false").lower() == "true"
        self.bin = os.getenv("WHISPER_BIN", "whisper")
        self.model = os.getenv("WHISPER_MODEL", "base")
        self.lang = os.getenv("AI_CAPTIONS_LANG", "ro")

        if self.enabled:
            logger.info(
                f"Whisper captions enabled: bin={self.bin}, model={self.model}, lang={self.lang}"
            )

    def generate(self, audio_path: str, out_dir: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Generate captions from audio file.

        Args:
            audio_path: Path to audio file (WAV/MP3)
            out_dir: Output directory for caption files

        Returns:
            Dict with keys: srt_path, ass_path, text (concatenated)
            Returns None if disabled or if generation fails
        """
        if not self.enabled:
            logger.debug("Whisper captions disabled")
            return None

        if not shutil.which(self.bin):
            logger.warning(f"Whisper binary not found: {self.bin}")
            return None

        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return None

        try:
            os.makedirs(out_dir, exist_ok=True)
            srt_out = os.path.join(out_dir, "auto.srt")

            # Build Whisper command
            cmd = [
                self.bin,
                audio_path,
                "--model",
                self.model,
                "--language",
                self.lang,
                "--task",
                "transcribe",
                "--output_format",
                "srt",
                "--output_dir",
                out_dir,
            ]

            logger.info(f"Running Whisper: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300
            )

            if result.returncode != 0:
                logger.error(f"Whisper failed: {result.stderr}")
                return None

            # Find produced SRT file
            # Whisper may name the file after the audio file basename
            produced = None
            for name in os.listdir(out_dir):
                if name.endswith(".srt"):
                    produced = os.path.join(out_dir, name)
                    break

            if not produced:
                logger.warning("Whisper did not produce SRT file")
                return None

            # Normalize to auto.srt
            if produced != srt_out:
                if os.path.exists(srt_out):
                    os.remove(srt_out)
                os.replace(produced, srt_out)

            logger.info(f"Whisper captions generated: {srt_out}")

            # Extract text content
            text_content = None
            try:
                with open(srt_out, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    # Extract only subtitle text (skip timestamps and numbers)
                    text_lines = [
                        line.strip()
                        for line in lines
                        if line.strip()
                        and not line.strip().isdigit()
                        and "-->" not in line
                    ]
                    text_content = " ".join(text_lines)
            except Exception as e:
                logger.warning(f"Failed to extract text from SRT: {e}")

            return {
                "srt_path": srt_out,
                "ass_path": None,  # ASS format not generated
                "text": text_content,
            }

        except subprocess.TimeoutExpired:
            logger.error("Whisper generation timed out")
            return None
        except Exception as e:
            logger.error(f"Whisper generation failed: {e}", exc_info=True)
            return None
