"""
Shared models for social media operations - Breaking circular imports.

This module contains shared classes and enums that are used across
the social media system to avoid circular import issues.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class PostStatus(Enum):
    """Statusurile unei postări."""
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ContentTemplate(Enum):
    """Template-urile de conținut disponibile."""
    EDUCATIONAL = "educational"
    TESTIMONIAL = "testimonial"
    PROMOTIONAL = "promotional"
    MANOLE_EXPERT = "manole_expert"


class ContentType(Enum):
    """Tipurile de conținut suportate."""
    VIDEO = "video"
    IMAGE = "image"
    CAROUSEL = "carousel"
    TEXT = "text"


@dataclass
class PostMetadata:
    """Metadatele unei postări."""
    title: str
    description: str
    tags: List[str] = None
    category: str = "auto"
    target_audience: str = "general"
    content_type: ContentType = ContentType.VIDEO

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class PostResult:
    """Rezultatul unei operații de postare."""
    success: bool
    platform: str
    post_id: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Interface for platform-specific posters
class SocialPosterInterface:
    """Interface pentru platformele de social media."""

    def upload_video(self, video_path: str, metadata: PostMetadata, **kwargs) -> PostResult:
        raise NotImplementedError

    def upload_image(self, image_path: str, metadata: PostMetadata, **kwargs) -> PostResult:
        raise NotImplementedError

    def schedule_post(self, content_path: str, metadata: PostMetadata,
                     scheduled_time: datetime, **kwargs) -> PostResult:
        raise NotImplementedError