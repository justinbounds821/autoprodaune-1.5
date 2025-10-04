# services/api/app/services/cost_tracker.py
"""
Cost tracking service for video generation costs.
SRP: Cost calculation and persistence only, no business logic.
"""
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class CostTracker:
    """Service for tracking video generation costs."""

    def __init__(self):
        """Initialize cost tracker."""
        # Cost rates (configurable via environment)
        self.tts_rate_per_second = float(os.getenv("TTS_COST_PER_SECOND", "0.0001"))  # ~$0.0001 per second
        self.processing_rate_per_second = float(os.getenv("PROCESSING_COST_PER_SECOND", "0.001"))  # ~$0.001 per second
        self.storage_rate_per_mb = float(os.getenv("STORAGE_COST_PER_MB", "0.01"))  # ~$0.01 per MB

        logger.info(f"✅ Cost tracker initialized: TTS=${self.tts_rate_per_second}/s, Processing=${self.processing_rate_per_second}/s, Storage=${self.storage_rate_per_mb}/MB")

    def calculate_costs(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate costs for a video generation job.

        Args:
            job_data: Job data with timing and file information

        Returns:
            Cost breakdown dictionary
        """
        costs = {
            "tts_seconds": 0.0,
            "processing_seconds": 0.0,
            "storage_mb": 0.0,
            "total_cents": 0,
            "breakdown": {}
        }

        # TTS cost (ElevenLabs or fallback)
        tts_seconds = job_data.get("tts_duration", 0)
        if tts_seconds > 0:
            tts_cost = tts_seconds * self.tts_rate_per_second
            costs["tts_seconds"] = tts_seconds
            costs["breakdown"]["tts"] = tts_cost

        # Processing cost (lip-sync + composition)
        processing_seconds = job_data.get("processing_duration", 0)
        if processing_seconds > 0:
            processing_cost = processing_seconds * self.processing_rate_per_second
            costs["processing_seconds"] = processing_seconds
            costs["breakdown"]["processing"] = processing_cost

        # Storage cost (estimated final file size)
        storage_mb = job_data.get("estimated_storage_mb", 5)  # Default 5MB estimate
        if storage_mb > 0:
            storage_cost = storage_mb * self.storage_rate_per_mb
            costs["storage_mb"] = storage_mb
            costs["breakdown"]["storage"] = storage_cost

        # Calculate total in cents
        total_cost = sum(costs["breakdown"].values())
        costs["total_cents"] = int(total_cost * 100)  # Convert to cents

        logger.info(f"Calculated costs for job: {costs}")
        return costs

    def save_costs(self, job_id: str, costs: Dict[str, Any]) -> bool:
        """
        Save cost data to Supabase.

        Args:
            job_id: Job identifier
            costs: Cost data dictionary

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            from .job_repo_supabase import get_job_repo

            repo = get_job_repo()
            success = repo.save_cost(job_id, costs)

            if success:
                logger.info(f"✅ Saved costs for job {job_id}")
            else:
                logger.warning(f"Failed to save costs for job {job_id}")

            return success

        except Exception as e:
            logger.error(f"Error saving costs for job {job_id}: {e}")
            return False

    def get_cost_summary(self, job_ids: list = None) -> Dict[str, Any]:
        """
        Get cost summary for jobs.

        Args:
            job_ids: Optional list of job IDs to summarize

        Returns:
            Cost summary dictionary
        """
        try:
            from .job_repo_supabase import get_job_repo

            repo = get_job_repo()

            # This would typically query Supabase for cost data
            # For now, return placeholder
            summary = {
                "total_jobs": 0,
                "total_cost_cents": 0,
                "average_cost_cents": 0,
                "cost_by_type": {
                    "tts": 0,
                    "processing": 0,
                    "storage": 0
                }
            }

            logger.info(f"Cost summary requested for {len(job_ids) if job_ids else 'all'} jobs")
            return summary

        except Exception as e:
            logger.error(f"Error getting cost summary: {e}")
            return {
                "total_jobs": 0,
                "total_cost_cents": 0,
                "average_cost_cents": 0,
                "cost_by_type": {}
            }

    def get_cost_rates(self) -> Dict[str, float]:
        """Get current cost rates."""
        return {
            "tts_rate_per_second": self.tts_rate_per_second,
            "processing_rate_per_second": self.processing_rate_per_second,
            "storage_rate_per_mb": self.storage_rate_per_mb
        }

# Global instance
_cost_tracker = None

def get_cost_tracker() -> CostTracker:
    """Get or create global cost tracker instance."""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker