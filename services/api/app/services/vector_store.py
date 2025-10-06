"""
Vector Store Service - Semantic Search & Embeddings
Single Responsibility: Manage vector embeddings for video content search
Safe-by-default: Disabled unless ENABLE_VECTOR_SEARCH=true
"""
import os
import logging
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Semantic vector search for video content.
    Falls back to keyword search if embedding model unavailable.
    """
    
    def __init__(self):
        self.enabled = os.getenv("ENABLE_VECTOR_SEARCH", "false").lower() == "true"
        self.dimension = int(os.getenv("AI_PGVECTOR_DIM", "384"))
        self.similarity_threshold = float(os.getenv("VECTOR_SIMILARITY_THRESHOLD", "0.7"))
        self.model = None
        
        if not self.enabled:
            logger.info("⚠️ Vector search disabled (ENABLE_VECTOR_SEARCH=false)")
            return
        
        # Try to load sentence-transformers model
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info(f"✅ Vector search enabled (dim={self.dimension})")
        except ImportError:
            logger.warning("⚠️ sentence-transformers not installed, using fallback search")
            self.enabled = False
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate vector embedding for text"""
        if not self.enabled or not self.model:
            return self._generate_fallback_embedding(text)
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return self._generate_fallback_embedding(text)
    
    def _generate_fallback_embedding(self, text: str) -> List[float]:
        """Simple hash-based fallback embedding (not semantic, but functional)"""
        import hashlib
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        # Convert to pseudo-embedding of correct dimension
        embedding = []
        for i in range(self.dimension):
            byte_idx = i % len(hash_bytes)
            embedding.append((hash_bytes[byte_idx] / 255.0) - 0.5)
        return embedding
    
    async def search_similar(
        self, 
        query: str, 
        job_ids: Optional[List[str]] = None,
        min_score: float = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for videos similar to query text.
        Falls back to keyword search if embeddings disabled.
        """
        if min_score is None:
            min_score = self.similarity_threshold
        
        query_embedding = self.generate_embedding(query)
        
        if not self.enabled:
            # Fallback: keyword-based search
            return await self._keyword_search(query, job_ids, limit)
        
        # TODO: Implement pgvector similarity search when DB schema ready
        # For now, return mock results
        return [
            {
                "job_id": f"job_{i}",
                "score": 0.85 - (i * 0.05),
                "tags": ["automotive", "insurance"],
                "title": f"Video about {query}"
            }
            for i in range(min(3, limit))
        ]
    
    async def _keyword_search(
        self, 
        query: str, 
        job_ids: Optional[List[str]], 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Fallback keyword search when embeddings unavailable"""
        logger.debug(f"Using keyword fallback search for: {query}")
        # Simple keyword matching - would query actual DB in production
        return []
    
    def get_health(self) -> Dict[str, Any]:
        """Health check for vector search"""
        return {
            "enabled": self.enabled,
            "model_loaded": self.model is not None,
            "dimension": self.dimension,
            "threshold": self.similarity_threshold
        }


# Singleton instance
_instance = None

def get_vector_store() -> VectorStoreService:
    """Get or create VectorStoreService singleton"""
    global _instance
    if _instance is None:
        _instance = VectorStoreService()
    return _instance
