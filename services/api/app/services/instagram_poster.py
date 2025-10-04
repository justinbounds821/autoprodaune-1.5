"""
Wrapper compat pentru vechiul nume `instagram_poster`.
Păstrează API-ul existent (get_instagram_poster / instagram_poster).
"""
from .instagram.poster import InstagramPoster
from .instagram.exceptions import InstagramPosterError

instagram_poster = InstagramPoster()

def get_instagram_poster() -> InstagramPoster:
    return instagram_poster

__all__ = ["InstagramPoster", "InstagramPosterError", "instagram_poster", "get_instagram_poster"]
