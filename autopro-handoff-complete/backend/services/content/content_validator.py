from __future__ import annotations
from typing import List, Dict, Any
from .models import ContentItem

# reguli simple, extensibile ușor
_PLATFORM_RULES: Dict[str, Dict[str, int]] = {
    "instagram": {"max_length": 2200, "max_hashtags": 30},
    "facebook":  {"max_length": 63206, "max_hashtags": 50},
    "twitter":   {"max_length": 280,  "max_hashtags": 10},
    "linkedin":  {"max_length": 3000, "max_hashtags": 20},
    "tiktok":    {"max_length": 2200, "max_hashtags": 30},
    "youtube":   {"max_length": 5000, "max_hashtags": 15},
}

class ContentValidator:
    def validate_content(self, item: ContentItem) -> List[str]:
        errors: List[str] = []
        text = (item.title or "") + " " + (item.description or "")
        for p in item.target_platforms or []:
            rules = _PLATFORM_RULES.get(p.lower())
            if not rules:
                continue
            if len(text) > rules["max_length"]:
                errors.append(f"Text prea lung pt {p}: {len(text)}/{rules['max_length']}")
            if len(item.hashtags) > rules["max_hashtags"]:
                errors.append(f"Prea multe hashtags pt {p}: {len(item.hashtags)}/{rules['max_hashtags']}")
        for a in item.assets:
            if not a.file_path:
                errors.append(f"Asset fără path: {a.id}")
        return errors
