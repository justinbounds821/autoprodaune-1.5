"""
Housekeeping Service - Auto-cleanup of old files and data
Single Responsibility: Delete expired jobs, clean storage, maintain DB
Safe-by-default: Always enabled with configurable TTLs
"""
import os
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)


class HousekeepingService:
    """
    Automated cleanup of old data and files.
    Runs periodically to maintain system health.
    """
    
    def __init__(self):
        self.ttl_completed_days = int(os.getenv("TTL_COMPLETED_DAYS", "30"))
        self.ttl_failed_days = int(os.getenv("TTL_FAILED_DAYS", "7"))
        self.cleanup_interval_minutes = int(os.getenv("CLEANUP_INTERVAL_MINUTES", "60"))
        self.enabled = True  # Always enabled
        self.is_running = False
        
        logger.info(
            f"✅ Housekeeping enabled "
            f"(completed={self.ttl_completed_days}d, failed={self.ttl_failed_days}d, "
            f"interval={self.cleanup_interval_minutes}m)"
        )
    
    async def run_cleanup(self) -> Dict[str, Any]:
        """
        Run complete cleanup cycle.
        Returns statistics about cleanup operations.
        """
        if self.is_running:
            return {"status": "already_running"}
        
        self.is_running = True
        start_time = datetime.utcnow()
        
        try:
            stats = {
                "started_at": start_time.isoformat(),
                "jobs_deleted": 0,
                "files_deleted": 0,
                "storage_freed_mb": 0,
                "errors": []
            }
            
            # 1. Delete expired completed jobs
            completed_deleted = await self._delete_expired_jobs("completed", self.ttl_completed_days)
            stats["jobs_deleted"] += completed_deleted
            
            # 2. Delete expired failed jobs
            failed_deleted = await self._delete_expired_jobs("failed", self.ttl_failed_days)
            stats["jobs_deleted"] += failed_deleted
            
            # 3. Clean orphaned files
            files_cleaned = await self._clean_orphaned_files()
            stats["files_deleted"] = files_cleaned["count"]
            stats["storage_freed_mb"] = files_cleaned["size_mb"]
            
            # 4. Clean temp files
            temp_cleaned = await self._clean_temp_files()
            stats["temp_files_deleted"] = temp_cleaned
            
            # 5. Vacuum database (if applicable)
            # stats["db_vacuum"] = await self._vacuum_database()
            
            stats["completed_at"] = datetime.utcnow().isoformat()
            stats["duration_seconds"] = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(
                f"Housekeeping complete: "
                f"{stats['jobs_deleted']} jobs, "
                f"{stats['files_deleted']} files, "
                f"{stats['storage_freed_mb']:.2f} MB freed"
            )
            
            return stats
        
        except Exception as e:
            logger.error(f"Housekeeping error: {e}")
            return {"status": "error", "error": str(e)}
        
        finally:
            self.is_running = False
    
    async def _delete_expired_jobs(self, status: str, ttl_days: int) -> int:
        """Delete jobs older than TTL"""
        try:
            from .supabase_client import get_supabase
            
            supabase = get_supabase()
            cutoff_date = datetime.utcnow() - timedelta(days=ttl_days)
            
            # Query jobs to delete
            response = supabase.table("video_jobs").select("id, output_url").match({
                "status": status
            }).lt("created_at", cutoff_date.isoformat()).execute()
            
            jobs_to_delete = response.data or []
            
            # Delete files first
            for job in jobs_to_delete:
                if job.get("output_url"):
                    await self._delete_file(job["output_url"])
            
            # Delete database records
            if jobs_to_delete:
                job_ids = [job["id"] for job in jobs_to_delete]
                supabase.table("video_jobs").delete().in_("id", job_ids).execute()
            
            logger.info(f"Deleted {len(jobs_to_delete)} {status} jobs older than {ttl_days} days")
            return len(jobs_to_delete)
        
        except Exception as e:
            logger.error(f"Failed to delete expired {status} jobs: {e}")
            return 0
    
    async def _clean_orphaned_files(self) -> Dict[str, Any]:
        """Clean files without corresponding database records"""
        try:
            output_dir = Path("services/api/generated_videos")
            if not output_dir.exists():
                return {"count": 0, "size_mb": 0}
            
            total_size = 0
            files_deleted = 0
            
            # Find all video files
            for video_file in output_dir.rglob("*.mp4"):
                # Check if job exists in DB
                job_id = video_file.stem
                
                try:
                    from .supabase_client import get_supabase
                    supabase = get_supabase()
                    
                    response = supabase.table("video_jobs").select("id").eq("id", job_id).execute()
                    
                    if not response.data:
                        # Orphaned file - delete it
                        file_size = video_file.stat().st_size
                        video_file.unlink()
                        total_size += file_size
                        files_deleted += 1
                        logger.debug(f"Deleted orphaned file: {video_file}")
                
                except Exception as e:
                    logger.warning(f"Error checking file {video_file}: {e}")
            
            return {
                "count": files_deleted,
                "size_mb": total_size / (1024 * 1024)
            }
        
        except Exception as e:
            logger.error(f"Orphaned files cleanup failed: {e}")
            return {"count": 0, "size_mb": 0}
    
    async def _clean_temp_files(self) -> int:
        """Clean temporary files older than 24 hours"""
        try:
            temp_dir = Path("/tmp")
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            files_deleted = 0
            
            # Find autopro temp files
            for temp_file in temp_dir.glob("autopro_*.tmp"):
                try:
                    file_time = datetime.fromtimestamp(temp_file.stat().st_mtime)
                    if file_time < cutoff_time:
                        temp_file.unlink()
                        files_deleted += 1
                except Exception as e:
                    logger.warning(f"Could not delete temp file {temp_file}: {e}")
            
            return files_deleted
        
        except Exception as e:
            logger.error(f"Temp files cleanup failed: {e}")
            return 0
    
    async def _delete_file(self, file_path: str):
        """Delete a single file safely"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.debug(f"Deleted file: {file_path}")
        except Exception as e:
            logger.warning(f"Could not delete file {file_path}: {e}")
    
    async def start_periodic_cleanup(self):
        """Start periodic cleanup task"""
        logger.info(f"Starting periodic cleanup (every {self.cleanup_interval_minutes} minutes)")
        
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval_minutes * 60)
                await self.run_cleanup()
            except asyncio.CancelledError:
                logger.info("Periodic cleanup stopped")
                break
            except Exception as e:
                logger.error(f"Periodic cleanup error: {e}")
    
    def get_health(self) -> Dict[str, Any]:
        """Health check for housekeeping service"""
        return {
            "enabled": self.enabled,
            "is_running": self.is_running,
            "ttl_completed_days": self.ttl_completed_days,
            "ttl_failed_days": self.ttl_failed_days,
            "cleanup_interval_minutes": self.cleanup_interval_minutes
        }


# Singleton instance
_instance = None

def get_housekeeping_service() -> HousekeepingService:
    """Get or create HousekeepingService singleton"""
    global _instance
    if _instance is None:
        _instance = HousekeepingService()
    return _instance
