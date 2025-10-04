"""
Autoposter service for AutoPro Daune (API version).

This module provides functions to discover ready‑to‑publish videos in a
configured directory, select a platform based on configurable ratios,
upload using per‑platform adapters and fall back to Publer in case of
persistent failures【564548360441287†L1616-L1655】.  It is intended to be invoked by an API
endpoint (see ``routes/autoposter.py``) or scheduled via cron/n8n.
"""

import os
import random
import time
import json
from typing import List, Tuple

from .tiktok import upload_video as upload_tiktok
from .ig import upload_video as upload_instagram
from .youtube import upload_video as upload_youtube
from .fallback_publer import upload_video as upload_publer


def discover_videos(directory: str) -> List[str]:
    """Return a sorted list of video file paths ready for publishing.

    The autoposter expects videos to be stored in the configured folder.
    Each file must have a corresponding JSON metadata file (same
    basename, `.json` extension) with at least a ``caption`` field.
    """
    videos: List[str] = []
    try:
        for entry in os.scandir(directory):
            if entry.is_file() and entry.name.lower().endswith(".mp4"):
                meta = os.path.splitext(entry.path)[0] + ".json"
                if os.path.exists(meta):
                    videos.append(entry.path)
    except FileNotFoundError:
        return []
    return sorted(videos)


def pick_platform() -> str:
    """Randomly choose a platform based on ``AUTOPOSTER_RATIO`` env variable.

    The ratio environment variable must be a comma‑separated list of
    ``platform:weight`` entries.  Defaults to ``tiktok:0.4,instagram:0.4,youtube:0.2``.
    """
    ratio_env = os.getenv("AUTOPOSTER_RATIO")
    if ratio_env:
        parts = [p.strip() for p in ratio_env.split(",") if p.strip()]
        ratios = {}
        for part in parts:
            try:
                platform, weight = part.split(":")
                ratios[platform.lower()] = float(weight)
            except ValueError:
                continue
    else:
        ratios = {"tiktok": 0.4, "instagram": 0.4, "youtube": 0.2}
    total = sum(ratios.values()) or 1.0
    cumulative: List[Tuple[str, float]] = []
    csum = 0.0
    for platform, weight in ratios.items():
        csum += weight / total
        cumulative.append((platform, csum))
    r = random.random()
    for platform, threshold in cumulative:
        if r <= threshold:
            return platform
    return "youtube"


def publish_video(path: str) -> None:
    """Publish a single video to the chosen platform with retries and fallback.

    :param path: Path to the MP4 file.  Requires a JSON file with the
      same basename containing a ``caption`` field.
    """
    base, _ = os.path.splitext(path)
    meta_path = base + ".json"
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        caption = meta.get("caption", "")
    except Exception as exc:
        print(f"[Autoposter] Skipping {path}: failed to read metadata -> {exc}")
        return
    platform = pick_platform()
    upload_fn = {
        "tiktok": upload_tiktok,
        "instagram": upload_instagram,
        "youtube": upload_youtube,
    }.get(platform, upload_tiktok)
    max_attempts = 3
    delay = 10
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"[Autoposter] Uploading {path} to {platform} (attempt {attempt}/{max_attempts})")
            upload_fn(path, caption)
            # Move files to published directory on success
            published_dir = os.path.join(os.path.dirname(path), "published")
            os.makedirs(published_dir, exist_ok=True)
            os.rename(path, os.path.join(published_dir, os.path.basename(path)))
            os.rename(meta_path, os.path.join(published_dir, os.path.basename(meta_path)))
            print(f"[Autoposter] Successfully uploaded {path} to {platform}")
            return
        except Exception as exc:
            print(f"[Autoposter] Error uploading {path} to {platform}: {exc}")
            time.sleep(delay)
            delay *= 2
    # Fallback to Publer
    try:
        print(f"[Autoposter] Falling back to Publer for {path}")
        upload_publer(path, caption)
        published_dir = os.path.join(os.path.dirname(path), "published")
        os.makedirs(published_dir, exist_ok=True)
        os.rename(path, os.path.join(published_dir, os.path.basename(path)))
        os.rename(meta_path, os.path.join(published_dir, os.path.basename(meta_path)))
    except Exception as exc:
        print(f"[Autoposter] Failed fallback upload via Publer: {exc}")


def run_autoposter() -> dict[str, int]:
    """Discover videos and publish each in turn.

    :returns: A dictionary with counts of processed and published videos.
    """
    directory = os.getenv("AUTOPOSTER_DIRECTORY", "./videos/to_publish")
    videos = discover_videos(directory)
    published = 0
    for video in videos:
        publish_video(video)
        published += 1
    return {"processed": len(videos), "published": published}