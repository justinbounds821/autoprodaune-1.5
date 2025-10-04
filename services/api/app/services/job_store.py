# services/api/app/services/job_store.py
"""
Simple in-memory job store for video generation jobs.
SRP: Job management only, no business logic.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# In-memory job storage (for production, consider Redis or database)
JOBS: Dict[str, Dict[str, Any]] = {}

def create_job(job_id: str, meta: Optional[Dict[str, Any]] = None) -> None:
    """
    Create a new job entry.
    
    Args:
        job_id: Unique job identifier
        meta: Optional metadata dictionary
    """
    JOBS[job_id] = {
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "video_url": None,
        "error": None,
        "meta": meta or {},
    }
    logger.info(f"Created job {job_id}")

def set_status(job_id: str, status: str, **kwargs) -> bool:
    """
    Update job status and additional fields.
    
    Args:
        job_id: Job identifier
        status: New status
        **kwargs: Additional fields to update
        
    Returns:
        True if job exists and was updated, False otherwise
    """
    if job_id not in JOBS:
        logger.warning(f"Job {job_id} not found")
        return False
    
    JOBS[job_id].update({
        "status": status,
        "updated_at": datetime.utcnow().isoformat(),
        **kwargs
    })
    
    logger.info(f"Updated job {job_id} status to {status}")
    return True

def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Get job information.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job dictionary or None if not found
    """
    return JOBS.get(job_id)

def get_jobs_by_status(status: str) -> Dict[str, Dict[str, Any]]:
    """
    Get all jobs with specific status.
    
    Args:
        status: Status to filter by
        
    Returns:
        Dictionary of jobs with the specified status
    """
    return {job_id: job for job_id, job in JOBS.items() 
            if job.get("status") == status}

def delete_job(job_id: str) -> bool:
    """
    Delete a job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        True if job existed and was deleted, False otherwise
    """
    if job_id in JOBS:
        del JOBS[job_id]
        logger.info(f"Deleted job {job_id}")
        return True
    return False

def cleanup_old_jobs(max_age_hours: int = 24) -> int:
    """
    Clean up old completed/failed jobs.
    
    Args:
        max_age_hours: Maximum age in hours
        
    Returns:
        Number of jobs cleaned up
    """
    cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
    jobs_to_remove = []
    
    for job_id, job in JOBS.items():
        if job.get("status") in ["completed", "failed"]:
            created_at = job.get("created_at")
            if created_at:
                try:
                    job_time = datetime.fromisoformat(created_at.replace('Z', '+00:00')).timestamp()
                    if job_time < cutoff_time:
                        jobs_to_remove.append(job_id)
                except ValueError:
                    # Invalid timestamp, remove job
                    jobs_to_remove.append(job_id)
    
    for job_id in jobs_to_remove:
        del JOBS[job_id]
    
    logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs")
    return len(jobs_to_remove)

def get_job_stats() -> Dict[str, Any]:
    """
    Get job statistics.
    
    Returns:
        Dictionary with job statistics
    """
    total_jobs = len(JOBS)
    status_counts = {}
    
    for job in JOBS.values():
        status = job.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        "total_jobs": total_jobs,
        "status_counts": status_counts,
        "oldest_job": min((job.get("created_at") for job in JOBS.values() 
                          if job.get("created_at")), default=None),
        "newest_job": max((job.get("created_at") for job in JOBS.values() 
                          if job.get("created_at")), default=None)
    }
