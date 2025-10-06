"""
Cost Tracker Service - Track per-job costs and budgets
Single Responsibility: Calculate and track processing costs
Safe-by-default: Disabled unless ENABLE_COST_TRACKER=true
Extends existing cost_calculator.py with enhanced tracking
"""
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


class CostTrackerService:
    """
    Track detailed costs per job including:
    - TTS costs (per second of audio)
    - Processing costs (per second of video)
    - Storage costs (per MB)
    - AI feature costs (embeddings, captions, etc.)
    """
    
    def __init__(self):
        self.enabled = os.getenv("ENABLE_COST_TRACKER", "false").lower() == "true"
        
        # Cost rates (per unit)
        self.tts_cost_per_second = Decimal(os.getenv("TTS_COST_PER_SECOND", "0.01"))  # $0.01/sec
        self.processing_cost_per_second = Decimal(os.getenv("PROCESSING_COST_PER_SECOND", "0.001"))  # $0.001/sec
        self.storage_cost_per_mb = Decimal(os.getenv("STORAGE_COST_PER_MB", "0.0001"))  # $0.0001/MB
        self.ai_embedding_cost = Decimal(os.getenv("AI_EMBEDDING_COST", "0.0001"))  # $0.0001 per embedding
        self.ai_caption_cost = Decimal(os.getenv("AI_CAPTION_COST", "0.05"))  # $0.05 per minute
        
        if not self.enabled:
            logger.info("⚠️ Cost tracking disabled (ENABLE_COST_TRACKER=false)")
            return
        
        logger.info(
            f"✅ Cost tracking enabled "
            f"(TTS=${float(self.tts_cost_per_second)}/s, "
            f"Processing=${float(self.processing_cost_per_second)}/s)"
        )
    
    async def calculate_job_cost(
        self,
        job_id: str,
        tts_seconds: float = 0,
        processing_seconds: float = 0,
        storage_mb: float = 0,
        ai_features_used: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate total cost for a job.
        Returns breakdown and total in cents.
        """
        if not self.enabled:
            return {"amount_cents": 0, "breakdown": {}, "enabled": False}
        
        breakdown = {}
        total = Decimal("0")
        
        # TTS costs
        if tts_seconds > 0:
            tts_cost = self.tts_cost_per_second * Decimal(str(tts_seconds))
            breakdown["tts"] = {
                "seconds": tts_seconds,
                "rate_per_second": float(self.tts_cost_per_second),
                "cost_dollars": float(tts_cost)
            }
            total += tts_cost
        
        # Processing costs
        if processing_seconds > 0:
            proc_cost = self.processing_cost_per_second * Decimal(str(processing_seconds))
            breakdown["processing"] = {
                "seconds": processing_seconds,
                "rate_per_second": float(self.processing_cost_per_second),
                "cost_dollars": float(proc_cost)
            }
            total += proc_cost
        
        # Storage costs
        if storage_mb > 0:
            storage_cost = self.storage_cost_per_mb * Decimal(str(storage_mb))
            breakdown["storage"] = {
                "megabytes": storage_mb,
                "rate_per_mb": float(self.storage_cost_per_mb),
                "cost_dollars": float(storage_cost)
            }
            total += storage_cost
        
        # AI feature costs
        if ai_features_used:
            ai_cost = Decimal("0")
            ai_breakdown = {}
            
            if ai_features_used.get("embeddings"):
                embedding_cost = self.ai_embedding_cost
                ai_breakdown["embeddings"] = float(embedding_cost)
                ai_cost += embedding_cost
            
            if ai_features_used.get("captions_minutes"):
                minutes = Decimal(str(ai_features_used["captions_minutes"]))
                caption_cost = self.ai_caption_cost * minutes
                ai_breakdown["captions"] = {
                    "minutes": float(minutes),
                    "cost_dollars": float(caption_cost)
                }
                ai_cost += caption_cost
            
            if ai_breakdown:
                breakdown["ai_features"] = ai_breakdown
                breakdown["ai_total"] = float(ai_cost)
                total += ai_cost
        
        # Convert to cents
        total_cents = int(total * 100)
        
        result = {
            "job_id": job_id,
            "amount_cents": total_cents,
            "amount_dollars": float(total),
            "breakdown": breakdown,
            "calculated_at": datetime.utcnow().isoformat()
        }
        
        # Store cost in database
        await self._store_cost(job_id, result)
        
        return result
    
    async def _store_cost(self, job_id: str, cost_data: Dict[str, Any]):
        """Store cost data in database"""
        try:
            from .supabase_client import get_supabase
            
            supabase = get_supabase()
            
            # Store in costs table
            supabase.table("video_costs").upsert({
                "job_id": job_id,
                "amount_cents": cost_data["amount_cents"],
                "breakdown": cost_data["breakdown"],
                "calculated_at": cost_data["calculated_at"]
            }).execute()
            
            logger.debug(f"Stored cost for job {job_id}: ${cost_data['amount_dollars']:.4f}")
        
        except Exception as e:
            logger.error(f"Failed to store cost for job {job_id}: {e}")
    
    async def get_job_cost(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored cost for a job"""
        if not self.enabled:
            return None
        
        try:
            from .supabase_client import get_supabase
            
            supabase = get_supabase()
            response = supabase.table("video_costs").select("*").eq("job_id", job_id).execute()
            
            if response.data:
                return response.data[0]
            return None
        
        except Exception as e:
            logger.error(f"Failed to retrieve cost for job {job_id}: {e}")
            return None
    
    async def get_total_costs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get total costs for a date range"""
        if not self.enabled:
            return {"total_cents": 0, "total_dollars": 0, "job_count": 0}
        
        try:
            from .supabase_client import get_supabase
            
            supabase = get_supabase()
            query = supabase.table("video_costs").select("amount_cents, calculated_at")
            
            if start_date:
                query = query.gte("calculated_at", start_date.isoformat())
            if end_date:
                query = query.lte("calculated_at", end_date.isoformat())
            
            response = query.execute()
            
            costs = response.data or []
            total_cents = sum(c["amount_cents"] for c in costs)
            
            return {
                "total_cents": total_cents,
                "total_dollars": total_cents / 100,
                "job_count": len(costs),
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        
        except Exception as e:
            logger.error(f"Failed to get total costs: {e}")
            return {"total_cents": 0, "total_dollars": 0, "job_count": 0, "error": str(e)}
    
    def get_health(self) -> Dict[str, Any]:
        """Health check for cost tracker"""
        return {
            "enabled": self.enabled,
            "rates": {
                "tts_per_second": float(self.tts_cost_per_second),
                "processing_per_second": float(self.processing_cost_per_second),
                "storage_per_mb": float(self.storage_cost_per_mb),
                "ai_embedding": float(self.ai_embedding_cost),
                "ai_caption_per_minute": float(self.ai_caption_cost)
            }
        }


# Singleton instance
_instance = None

def get_cost_tracker() -> CostTrackerService:
    """Get or create CostTrackerService singleton"""
    global _instance
    if _instance is None:
        _instance = CostTrackerService()
    return _instance
