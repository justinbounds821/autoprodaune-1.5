"""
Wrapper compat pentru Content Manager (refactor modular).
"""

from .content import (
    ContentManager, ContentStatus, ContentCategory, ContentValidationError
)
from .social_models import PostMetadata, ContentType

# instanță globală (compat cu vechiul cod)
content_manager = ContentManager()

def get_content_manager() -> ContentManager:
    return content_manager

__all__ = [
    "ContentManager",
    "ContentStatus",
    "ContentCategory",
    "ContentValidationError",
    "PostMetadata",
    "ContentType",
    "content_manager",
    "get_content_manager",
]
