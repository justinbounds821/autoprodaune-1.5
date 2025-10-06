"""
Tagging Service - Auto-generate content tags for videos
Single Responsibility: Extract keywords and sentiment from video content
Safe-by-default: Disabled unless ENABLE_TAGGING=true
"""
import os
import logging
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)


class TaggingService:
    """
    Auto-generate tags, keywords, and sentiment analysis for video content.
    Falls back to basic keyword extraction if ML unavailable.
    """
    
    def __init__(self):
        self.enabled = os.getenv("ENABLE_TAGGING", "false").lower() == "true"
        self.nlp_available = False
        self.nlp = None
        
        if not self.enabled:
            logger.info("⚠️ Tagging service disabled (ENABLE_TAGGING=false)")
            return
        
        # Try to load spaCy NLP model
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
            self.nlp_available = True
            logger.info("✅ Tagging service enabled with NLP")
        except (ImportError, OSError):
            logger.warning("⚠️ spaCy not available, using fallback tagging")
            self.enabled = True  # Still enable with fallback
    
    async def analyze_content(
        self, 
        text: str, 
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze text content and extract tags, keywords, sentiment.
        """
        if not self.enabled:
            return self._empty_analysis()
        
        try:
            if self.nlp_available and self.nlp:
                return await self._nlp_analysis(text, title)
            else:
                return await self._fallback_analysis(text, title)
        
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            return self._empty_analysis()
    
    async def _nlp_analysis(self, text: str, title: Optional[str]) -> Dict[str, Any]:
        """Advanced NLP-based analysis using spaCy"""
        combined_text = f"{title or ''} {text}"
        doc = self.nlp(combined_text[:1000000])  # Limit length for performance
        
        # Extract entities
        entities = [
            {"text": ent.text, "label": ent.label_}
            for ent in doc.ents
            if ent.label_ in ("ORG", "PRODUCT", "GPE", "EVENT", "WORK_OF_ART")
        ]
        
        # Extract key noun phrases
        noun_chunks = [chunk.text for chunk in doc.noun_chunks][:10]
        
        # Simple sentiment (positive/negative word counting)
        positive_words = ["good", "great", "excellent", "amazing", "perfect", "best"]
        negative_words = ["bad", "poor", "terrible", "worst", "awful", "horrible"]
        
        text_lower = text.lower()
        pos_count = sum(text_lower.count(w) for w in positive_words)
        neg_count = sum(text_lower.count(w) for w in negative_words)
        
        if pos_count > neg_count:
            sentiment = "positive"
            sentiment_score = min(1.0, pos_count / (pos_count + neg_count + 1))
        elif neg_count > pos_count:
            sentiment = "negative"
            sentiment_score = max(-1.0, -neg_count / (pos_count + neg_count + 1))
        else:
            sentiment = "neutral"
            sentiment_score = 0.0
        
        # Extract top keywords
        keywords = self._extract_keywords(text, doc)
        
        return {
            "tags": keywords[:10],
            "entities": entities[:5],
            "noun_phrases": noun_chunks[:5],
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "language": doc.lang_,
            "word_count": len(doc)
        }
    
    async def _fallback_analysis(self, text: str, title: Optional[str]) -> Dict[str, Any]:
        """Simple keyword-based fallback analysis"""
        combined_text = f"{title or ''} {text}"
        words = re.findall(r'\b[a-zA-Z]{4,}\b', combined_text.lower())
        
        # Count word frequencies
        word_freq = {}
        for word in words:
            if word not in self._get_stopwords():
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        tags = [word for word, _ in keywords]
        
        return {
            "tags": tags,
            "entities": [],
            "noun_phrases": [],
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "language": "en",
            "word_count": len(words)
        }
    
    def _extract_keywords(self, text: str, doc=None) -> List[str]:
        """Extract keywords from text"""
        if doc:
            # Use spaCy tokens
            keywords = [
                token.text.lower()
                for token in doc
                if not token.is_stop and not token.is_punct and len(token.text) > 3
            ]
        else:
            # Fallback regex
            keywords = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Remove stopwords and count frequency
        stopwords = self._get_stopwords()
        keyword_freq = {}
        for word in keywords:
            if word not in stopwords:
                keyword_freq[word] = keyword_freq.get(word, 0) + 1
        
        # Return sorted by frequency
        return [word for word, _ in sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)]
    
    def _get_stopwords(self) -> set:
        """Common English stopwords"""
        return {
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
            "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
            "or", "an", "will", "my", "one", "all", "would", "there", "their"
        }
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis when disabled"""
        return {
            "tags": [],
            "entities": [],
            "noun_phrases": [],
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "language": "unknown",
            "word_count": 0
        }
    
    def get_health(self) -> Dict[str, Any]:
        """Health check for tagging service"""
        return {
            "enabled": self.enabled,
            "nlp_available": self.nlp_available,
            "model": "en_core_web_sm" if self.nlp_available else "fallback"
        }


# Singleton instance
_instance = None

def get_tagging_service() -> TaggingService:
    """Get or create TaggingService singleton"""
    global _instance
    if _instance is None:
        _instance = TaggingService()
    return _instance
