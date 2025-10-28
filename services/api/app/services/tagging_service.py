# services/api/app/services/tagging_service.py
"""
Video tagging service.
SRP: Extract semantic tags from video content.
"""
from __future__ import annotations

import logging
from typing import List

logger = logging.getLogger(__name__)


class TaggingService:
    """
    Simple tagging service for video content.
    Stub implementation - can be extended with NLP/classification models.
    """

    def __init__(self) -> None:
        """Initialize tagging service."""
        logger.debug("TaggingService initialized")

    def extract_tags(self, text: str) -> List[str]:
        """
        Extract tags from text content.
        
        Args:
            text: Input text (script, captions, etc.)
            
        Returns:
            List of extracted tags
        """
        if not text:
            return []
        
        # Stub implementation - simple keyword matching
        text_lower = text.lower()
        tags = []
        
        # Domain-specific keywords
        keywords = {
            "asigurari": ["asigurare", "asigurări", "poliță", "polițe"],
            "daune": ["daună", "daune", "avarie", "avarii", "accident"],
            "auto": ["auto", "mașină", "vehicul", "automobil"],
            "despagubire": ["despăgubire", "despăgubiri", "compensație"],
            "rca": ["rca", "răspundere civilă"],
            "casco": ["casco", "kasko"],
        }
        
        for tag, kw_list in keywords.items():
            if any(kw in text_lower for kw in kw_list):
                tags.append(tag)
        
        logger.debug(f"Extracted {len(tags)} tags: {tags}")
        return tags
