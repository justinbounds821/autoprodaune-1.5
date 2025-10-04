"""
Wrapper compat pentru YouTube Poster (refactor modular).
Păstrează import-urile vechi funcționale.
"""
from .youtube.poster import YouTubePoster

youtube_poster = YouTubePoster()

def get_youtube_poster() -> YouTubePoster:
    return youtube_poster

__all__ = ["YouTubePoster", "youtube_poster", "get_youtube_poster"]
