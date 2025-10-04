from __future__ import annotations
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
import os

THUMB_MAX = 512  # px

def _thumb_name(path: str) -> str:
    root, ext = os.path.splitext(path)
    return f"{root}__thumb{ext or '.jpg'}"

def process_image(path: str) -> Dict[str, Any]:
    """Returnează metadata + thumbnail pentru un fișier imagine."""
    out: Dict[str, Any] = {"source_path": path, "ok": False}
    if not os.path.isfile(path):
        out["error"] = "not_found"
        return out

    try:
        with Image.open(path) as im:
            im.load()
            w, h = im.size
            out.update({"width": w, "height": h, "format": im.format})

            # thumbnail proporțional
            im_copy = im.copy()
            im_copy.thumbnail((THUMB_MAX, THUMB_MAX))
            thumb_path = _thumb_name(path)
            # pentru formate cu alpha -> salvează PNG
            save_path = thumb_path if im_copy.mode in ("RGB", "L") else os.path.splitext(thumb_path)[0] + ".png"
            im_copy.save(save_path)
            out.update({"thumbnail_path": save_path, "ok": True})
            return out
    except Exception as e:
        out["error"] = f"PIL_error: {e}"
        return out

class AssetProcessor:
    def __init__(self, thumbnails_dir: str):
        self.thumbnails_dir = Path(thumbnails_dir)
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)

    def process_asset(self, asset_path: str) -> Dict[str, Any]:
        p = Path(asset_path)
        if not p.exists():
            raise FileNotFoundError(f"Asset inexistent: {asset_path}")

        mime, _ = mimetypes.guess_type(p.name)
        mime = mime or "application/octet-stream"
        size = p.stat().st_size

        meta: Dict[str, Any] = {}
        dims = None
        duration = None
        thumb: Optional[str] = None

        # imagini → extrage dimensiuni + thumbnail
        if mime.startswith("image/"):
            try:
                with Image.open(p) as img:
                    dims = {"width": img.width, "height": img.height}
                    thumb_path = self.thumbnails_dir / f"{p.stem}_thumb{p.suffix}"
                    img.thumbnail((300, 300))
                    img.save(thumb_path)
                    thumb = str(thumb_path)
            except Exception:
                pass
        # video → nu folosim ffmpeg aici; lăsăm thumbnail/durată None pentru stabilitate
        return {
            "file_size": size,
            "mime_type": mime,
            "metadata": {"dimensions": dims, "duration": duration},
            "thumbnail_path": thumb,
        }