# services/api/app/services/vector_store.py
"""
Vector store service for semantic video search.
SRP: Manage vector embeddings for videos.
"""
from __future__ import annotations

import os
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector store for semantic search.
    Stub implementation - can be extended with actual embedding models.
    """

    def __init__(self) -> None:
        """Initialize vector store from environment."""
        self.enabled = os.getenv("AI_ENABLE_VECTOR_SEARCH", "false").lower() == "true"
        self.dim = int(os.getenv("AI_VECTOR_DIM", "384"))
        
        if self.enabled:
            logger.info(f"VectorStore enabled with dimension {self.dim}")
        else:
            logger.debug("VectorStore disabled")

    def _embed(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector (stub: returns zeros)
        """
        # Stub implementation - returns zero vector
        # In production, use sentence-transformers or similar
        return [0.0] * self.dim

    def upsert(self, job_id: str, captions_text: str) -> None:
        """
        Upsert vector embedding for a job.
        
        Args:
            job_id: Video job ID
            captions_text: Text content for embedding
        """
        if not self.enabled:
            return
            
        try:
            from .supabase_client import get_supabase_service_instance
            
            emb = self._embed(captions_text)
            emb_str = "[" + ",".join(str(x) for x in emb) + "]"
            
            svc = get_supabase_service_instance()
            # Use raw SQL to update vector embedding
            svc.sb.rpc(
                "exec_sql",
                {
                    "query": f"""
                        UPDATE video_insights 
                        SET vector_embedding = '{emb_str}'::vector 
                        WHERE job_id = '{job_id}'
                    """
                }
            )
            
            logger.info(f"Upserted vector embedding for job {job_id}")
            
        except Exception as e:
            logger.warning(f"Failed to upsert vector embedding: {e}")


def get_supabase_service_instance():
    """Get or create Supabase service singleton."""
    from .supabase_client import SupabaseService
    return SupabaseService()
