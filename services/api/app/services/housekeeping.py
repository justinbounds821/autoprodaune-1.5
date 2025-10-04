# services/api/app/services/housekeeping.py
"""
Housekeeping service for cleaning up old jobs and artifacts.
SRP: Cleanup operations only, no business logic.
"""
import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class HousekeepingService:
    """Service for periodic cleanup of old jobs and artifacts."""

    def __init__(self):
        """Initialize housekeeping service."""
        self.ttl_completed_days = int(os.getenv("HOUSEKEEPING_TTL_COMPLETED_DAYS", "30"))
        self.ttl_failed_days = int(os.getenv("HOUSEKEEPING_TTL_FAILED_DAYS", "7"))
        self.cleanup_interval_minutes = int(os.getenv("HOUSEKEEPING_INTERVAL_MIN", "30"))
        self.enabled = True

        logger.info(f"✅ Housekeeping service initialized: completed={self.ttl_completed_days}d, failed={self.ttl_failed_days}d, interval={self.cleanup_interval_minutes}m")

    async def run_cleanup_cycle(self) -> Dict[str, Any]:
        """
        Run a complete cleanup cycle.

        Returns:
            Dictionary with cleanup results
        """
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "database_cleanup": {"deleted_jobs": 0, "errors": []},
            "local_cleanup": {"deleted_files": 0, "errors": []},
            "r2_cleanup": {"deleted_objects": 0, "errors": []}
        }

        try:
            # Database cleanup
            results["database_cleanup"] = await self._cleanup_database()

            # Local file cleanup
            results["local_cleanup"] = await self._cleanup_local_files()

            # R2 object cleanup (if enabled)
            storage_type = os.getenv("VIDEO_ENGINE_STORAGE", "local")
            if storage_type == "r2":
                results["r2_cleanup"] = await self._cleanup_r2_objects()

            logger.info(f"✅ Cleanup cycle completed: {results}")

        except Exception as e:
            logger.error(f"Housekeeping cycle failed: {e}")
            results["error"] = str(e)

        return results

    async def _cleanup_database(self) -> Dict[str, Any]:
        """Clean up old database records."""
        result = {"deleted_jobs": 0, "errors": []}

        try:
            from .job_repo_supabase import get_job_repo

            repo = get_job_repo()

            if not repo.enabled:
                result["errors"].append("Supabase not available")
                return result

            # Get jobs older than TTL
            cutoff_completed = datetime.utcnow() - timedelta(days=self.ttl_completed_days)
            cutoff_failed = datetime.utcnow() - timedelta(days=self.ttl_failed_days)

            # This would typically use raw SQL queries to efficiently delete old records
            # For now, we'll use the existing cleanup function
            deleted_count = 0

            try:
                # Use the existing cleanup function from job_store if available
                from .job_store import cleanup_old_jobs
                deleted_count = cleanup_old_jobs()
                result["deleted_jobs"] = deleted_count

            except ImportError:
                logger.warning("Job store cleanup not available, skipping database cleanup")
                result["errors"].append("Job store cleanup not available")

            logger.info(f"Database cleanup: deleted {deleted_count} old jobs")

        except Exception as e:
            error_msg = f"Database cleanup error: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)

        return result

    async def _cleanup_local_files(self) -> Dict[str, Any]:
        """Clean up old local files."""
        result = {"deleted_files": 0, "errors": []}

        try:
            videos_dir = os.path.join(os.getcwd(), "generated_videos")

            if not os.path.exists(videos_dir):
                result["errors"].append("Videos directory not found")
                return result

            deleted_count = 0
            cutoff_time = datetime.utcnow() - timedelta(days=self.ttl_completed_days)

            # Walk through video files
            for root, dirs, files in os.walk(videos_dir):
                for file in files:
                    if file.endswith('.mp4'):
                        file_path = os.path.join(root, file)

                        # Check file age
                        try:
                            file_stat = os.stat(file_path)
                            file_age = datetime.fromtimestamp(file_stat.st_mtime)

                            if file_age < cutoff_time:
                                os.remove(file_path)
                                deleted_count += 1
                                logger.debug(f"Deleted old local file: {file_path}")

                        except OSError as e:
                            result["errors"].append(f"Failed to delete {file_path}: {e}")

            result["deleted_files"] = deleted_count
            logger.info(f"Local cleanup: deleted {deleted_count} old video files")

        except Exception as e:
            error_msg = f"Local cleanup error: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)

        return result

    async def _cleanup_r2_objects(self) -> Dict[str, Any]:
        """Clean up old R2 objects."""
        result = {"deleted_objects": 0, "errors": []}

        try:
            from .cdn_manager import get_cdn_manager

            cdn_manager = get_cdn_manager()

            if not cdn_manager.r2_client:
                result["errors"].append("R2 client not available")
                return result

            # For R2 cleanup, we would typically:
            # 1. Find objects older than TTL
            # 2. Delete them from R2

            # This is a simplified version - in production you might want
            # to implement more sophisticated lifecycle management
            logger.info("R2 cleanup: checking for old objects...")

            # For now, just log that cleanup would happen
            # Real implementation would query R2 for old objects and delete them

        except Exception as e:
            error_msg = f"R2 cleanup error: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)

        return result

    def mark_job_expired(self, job_id: str) -> bool:
        """
        Mark a job as expired in the database.

        Args:
            job_id: Job identifier

        Returns:
            True if marked successfully, False otherwise
        """
        try:
            from .job_repo_supabase import get_job_repo

            repo = get_job_repo()

            if repo.enabled:
                # Update job status to expired
                success = repo.update_job_status(job_id, "expired")
                if success:
                    logger.info(f"Marked job {job_id} as expired")
                    return True

            return False

        except Exception as e:
            logger.error(f"Failed to mark job {job_id} as expired: {e}")
            return False

    async def start_periodic_cleanup(self) -> None:
        """Start periodic cleanup task."""
        if not self.enabled:
            logger.info("Housekeeping periodic cleanup disabled")
            return

        logger.info(f"Starting periodic cleanup every {self.cleanup_interval_minutes} minutes")

        while True:
            try:
                await asyncio.sleep(self.cleanup_interval_minutes * 60)

                logger.info("Running scheduled housekeeping cleanup")
                results = await self.run_cleanup_cycle()

                # Log summary
                total_deleted = (
                    results["database_cleanup"]["deleted_jobs"] +
                    results["local_cleanup"]["deleted_files"] +
                    results["r2_cleanup"]["deleted_objects"]
                )

                if total_deleted > 0:
                    logger.info(f"Housekeeping: cleaned up {total_deleted} items")

            except asyncio.CancelledError:
                logger.info("Housekeeping periodic cleanup cancelled")
                break
            except Exception as e:
                logger.error(f"Housekeeping periodic cleanup error: {e}")
                await asyncio.sleep(60)  # Wait before retrying

# Global instance
_housekeeping_service = None

def get_housekeeping_service() -> HousekeepingService:
    """Get or create global housekeeping service instance."""
    global _housekeeping_service
    if _housekeeping_service is None:
        _housekeeping_service = HousekeepingService()
    return _housekeeping_service