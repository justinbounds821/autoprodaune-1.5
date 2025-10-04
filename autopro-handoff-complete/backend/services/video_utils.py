# services/api/app/services/video_utils.py
from __future__ import annotations
from pathlib import Path
from typing import Tuple, Union
import os, re, tempfile

# ---------- paths / fs ----------
def ensure_dir(p: Union[str, Path]) -> Path:
    p = Path(p)
    p.mkdir(parents=True, exist_ok=True)
    return p

def safe_temp_path(suffix: str = "", prefix: str = "apd_", dir: Union[str, Path] | None = None) -> Path:
    """Windows-safe temp file path (no locked handle)."""
    dir = Path(dir) if dir else Path(tempfile.gettempdir())
    ensure_dir(dir)
    fd, name = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=str(dir))
    os.close(fd)  # important pe Windows
    return Path(name)

# ---------- ffmpeg ----------
def ensure_ffmpeg_exe() -> str:
    """Returnează calea către ffmpeg sau 'ffmpeg' dacă nu poate rezolva."""
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        return get_ffmpeg_exe()
    except Exception:
        return os.environ.get("FFMPEG_PATH", "ffmpeg")

# ---------- color / utils ----------
_HEX_RE = re.compile(r"^#?(?P<R>[0-9a-fA-F]{2})(?P<G>[0-9a-fA-F]{2})(?P<B>[0-9a-fA-F]{2})$")
def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    m = _HEX_RE.match(hex_color.strip())
    if not m:
        raise ValueError(f"Invalid HEX color: {hex_color}")
    return tuple(int(m[c], 16) for c in ("R", "G", "B"))

# ---------- moviepy helpers (scurte) ----------
def with_audio(clip, audio_path: Union[str, Path]):
    """Atașează audio în mod sigur (închide fișierul la timp)."""
    from moviepy.editor import AudioFileClip
    audio_path = str(audio_path)
    with AudioFileClip(audio_path) as aclip:
        return clip.set_audio(aclip)

def with_duration(clip, seconds: float):
    return clip.set_duration(float(seconds))

def with_position(clip, position: Union[str, tuple]):
    return clip.set_position(position)

def make_text_clip(
    text: str,
    size: tuple[int, int],
    duration: float,
    position: Union[str, tuple] = "center",
    fontsize: int = 60,
):
    """
    Creează un clip cu text folosind PIL (fără ImageMagick).
    Întoarce mereu un ImageClip cu durata & poziția setate.
    """
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    try:
        from moviepy.editor import ImageClip  # compat 1.x/2.x
    except Exception:
        from moviepy import ImageClip

    W, H = size
    canvas = Image.new("RGBA", (int(W * 0.9), H), (0, 0, 0, 0))

    # font fallback
    font = None
    for path in (
        "DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ):
        try:
            font = ImageFont.truetype(path, fontsize)
            break
        except Exception:
            continue
    if not font:
        font = ImageFont.load_default()

    d = ImageDraw.Draw(canvas)
    bbox = d.multiline_textbbox((0, 0), text, font=font, align="center")
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    y = max(0, (H - th) // 2)

    d.multiline_text(
        ((canvas.width - tw) // 2, y),
        text,
        font=font,
        fill=(255, 255, 255, 255),
        align="center",
    )

    top = max(0, y - 40)
    bottom = min(H, y + th + 40)
    crop = canvas.crop((0, top, canvas.width, bottom))

    clip = ImageClip(np.array(crop))
    return with_position(with_duration(clip, duration), position)

__all__ = [
    "ensure_dir", "safe_temp_path", "ensure_ffmpeg_exe",
    "hex_to_rgb", "with_audio", "with_duration", "with_position",
    "make_text_clip",
]
