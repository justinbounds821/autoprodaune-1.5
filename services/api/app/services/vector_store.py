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
        
        if not self.enabled or not query_embedding:
            # Fallback: keyword-based search
            return await self._keyword_search(query, job_ids, limit)
        
        # Use pgvector for similarity search
        try:
            from ..services.supabase_client import get_supabase
            supabase = get_supabase()
            
            # Query using vector similarity (if pgvector extension enabled)
            # Note: This requires pgvector extension and vector column in video_insights
            response = supabase.table("video_insights").select(
                "job_id, tags, vector_embedding"
            ).not_.is_("vector_embedding", "null").execute()
            
            if not response.data:
                return []
            
            # Calculate cosine similarity in Python (would be done in SQL with pgvector in production)
            import numpy as np
            
            results = []
            for row in response.data:
                if not row.get("vector_embedding"):
                    continue
                
                # Calculate similarity
                embedding = np.array(row["vector_embedding"])
                query_emb = np.array(query_embedding)
                
                # Cosine similarity
                similarity = np.dot(embedding, query_emb) / (np.linalg.norm(embedding) * np.linalg.norm(query_emb))
                
                if similarity >= min_score:
                    results.append({
                        "job_id": row["job_id"],
                        "score": float(similarity),
                        "tags": row.get("tags", [])
                    })
            
            # Sort by score and limit
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return await self._keyword_search(query, job_ids, limit)
    
    async def _keyword_search(
        self, 
        query: str, 
        job_ids: Optional[List[str]], 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Fallback keyword search when embeddings unavailable"""
        logger.debug(f"Using keyword fallback search for: {query}")
        
        try:
            from ..services.supabase_client import get_supabase
            supabase = get_supabase()
            
            # Search in tags and job metadata
            response = supabase.table("video_insights").select(
                "job_id, tags"
            ).execute()
            
            if not response.data:
                return []
            
            # Simple keyword matching
            query_words = set(query.lower().split())
            results = []
            
            for row in response.data:
                tags = row.get("tags", [])
                tag_words = set(" ".join(tags).lower().split())
                
                # Calculate overlap score
                overlap = len(query_words & tag_words)
                if overlap > 0:
                    score = overlap / len(query_words)
                    results.append({
                        "job_id": row["job_id"],
                        "score": score,
                        "tags": tags
                    })
            
            # Sort by score and limit
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
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
