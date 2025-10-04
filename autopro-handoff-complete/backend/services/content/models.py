from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional, List

# Importă metadata/type din social_poster (sibling în services)
from ..social_poster import PostMetadata, ContentType

class ContentStatus(Enum):
    DRAFT = "draft"
    READY = "ready"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"

class ContentCategory(Enum):
    AUTOMOTIVE = "automotive"
    INSURANCE = "insurance"
    EDUCATION = "education"
    PROMOTIONAL = "promotional"
    INFORMATIONAL = "informational"
    ENTERTAINMENT = "entertainment"

@dataclass
class ContentAsset:
    id: str
    file_path: str
    file_type: str
    mime_type: str
    file_size: int
    thumbnail_path: Optional[str] = None
    duration: Optional[float] = None
    dimensions: Optional[Dict[str, int]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class ContentItem:
    id: str
    title: str
    description: str
    category: ContentCategory
    content_type: ContentType
    assets: List[ContentAsset]
    metadata: PostMetadata
    status: ContentStatus
    tags: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    target_platforms: List[str] = field(default_factory=list)
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    notes: Optional[str] = None

class ContentValidationError(Exception):
    pass
