# services/api/app/services/job_store.py
"""
In-memory job store for video generation jobs with concurrency control and back-pressure.
SRP: Job management only, no business logic.
"""
import os
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# In-memory job storage (for production, consider Redis or database)
JOBS: Dict[str, Dict[str, Any]] = {}

# Concurrency control
_processing_semaphore = None
_processing_count = 0
_queue_length = 0

def _get_concurrency_limit() -> int:
    """Get maximum concurrent jobs from environment."""
    return int(os.getenv("VIDEO_ENGINE_MAX_CONCURRENCY", "2"))

def _get_queue_limit() -> int:
    """Get maximum queue length from environment."""
    return int(os.getenv("VIDEO_ENGINE_QUEUE_LIMIT", "20"))

def _get_cleanup_after_minutes() -> int:
    """Get cleanup interval in minutes."""
    return int(os.getenv("VIDEO_ENGINE_CLEANUP_AFTER_MIN", "120"))

def _init_concurrency_control() -> None:
    """Initialize concurrency control semaphore."""
    global _processing_semaphore
    if _processing_semaphore is None:
        max_concurrency = _get_concurrency_limit()
        _processing_semaphore = asyncio.Semaphore(max_concurrency)
        logger.info(f"✅ Initialized concurrency control: max {max_concurrency} concurrent jobs")

def get_processing_semaphore() -> asyncio.Semaphore:
    """Get or create processing semaphore."""
    if _processing_semaphore is None:
        _init_concurrency_control()
    return _processing_semaphore

def can_accept_job() -> bool:
    """
    Check if system can accept new jobs based on queue limits.

    Returns:
        True if job can be accepted, False if at capacity
    """
    global _queue_length
    queue_limit = _get_queue_limit()

    # Count queued and processing jobs
    queued_count = sum(1 for job in JOBS.values() if job.get("status") in ["queued", "processing"])
    return queued_count < queue_limit

def get_queue_stats() -> Dict[str, Any]:
    """Get current queue statistics."""
    global _processing_count, _queue_length

    status_counts = {}
    for job in JOBS.values():
        status = job.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "total_jobs": len(JOBS),
        "processing_count": _processing_count,
        "queue_length": _queue_length,
        "status_counts": status_counts,
        "concurrency_limit": _get_concurrency_limit(),
        "queue_limit": _get_queue_limit()
    }

def create_job(job_id: str, meta: Optional[Dict[str, Any]] = None) -> None:
    """
    Create a new job entry with concurrency checking.

    Args:
        job_id: Unique job identifier
        meta: Optional metadata dictionary

    Raises:
        ValueError: If queue is at capacity
    """
    global _queue_length

    # Check if we can accept the job
    if not can_accept_job():
        queue_limit = _get_queue_limit()
        raise ValueError(f"Queue at capacity ({queue_limit} jobs). Please try again later.")

    JOBS[job_id] = {
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "video_url": None,
        "error": None,
        "meta": meta or {},
    }

    _queue_length = sum(1 for job in JOBS.values() if job.get("status") in ["queued", "processing"])
    logger.info(f"Created job {job_id} (queue length: {_queue_length})")

def set_status(job_id: str, status: str, **kwargs) -> bool:
    """
    Update job status and additional fields with concurrency tracking.

    Args:
        job_id: Job identifier
        status: New status
        **kwargs: Additional fields to update

    Returns:
        True if job exists and was updated, False otherwise
    """
    global _processing_count, _queue_length

    if job_id not in JOBS:
        logger.warning(f"Job {job_id} not found")
        return False

    old_status = JOBS[job_id].get("status")

    JOBS[job_id].update({
        "status": status,
        "updated_at": datetime.utcnow().isoformat(),
        **kwargs
    })

    # Update processing count
    if old_status == "processing" and status != "processing":
        _processing_count = max(0, _processing_count - 1)
    elif old_status != "processing" and status == "processing":
        _processing_count += 1

    # Update queue length
    _queue_length = sum(1 for job in JOBS.values() if job.get("status") in ["queued", "processing"])

    logger.info(f"Updated job {job_id} status: {old_status} -> {status} (processing: {_processing_count}, queue: {_queue_length})")
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

def cleanup_old_jobs() -> int:
    """
    Clean up old completed/failed jobs based on cleanup interval.

    Returns:
        Number of jobs cleaned up
    """
    global _queue_length

    cleanup_minutes = _get_cleanup_after_minutes()
    cutoff_time = datetime.utcnow() - timedelta(minutes=cleanup_minutes)

    jobs_to_remove = []
    for job_id, job in JOBS.items():
        if job.get("status") in ["completed", "failed"]:
            created_at = job.get("created_at")
            if created_at:
                try:
                    job_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if job_time < cutoff_time:
                        jobs_to_remove.append(job_id)
                except ValueError:
                    # Invalid timestamp, remove job
                    jobs_to_remove.append(job_id)

    for job_id in jobs_to_remove:
        del JOBS[job_id]

    if jobs_to_remove:
        _queue_length = sum(1 for job in JOBS.values() if job.get("status") in ["queued", "processing"])
        logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs (older than {cleanup_minutes} minutes)")

    return len(jobs_to_remove)

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

def get_job_stats() -> Dict[str, Any]:
    """
    Get comprehensive job statistics.

    Returns:
        Dictionary with job statistics
    """
    total_jobs = len(JOBS)
    status_counts = {}

    for job in JOBS.values():
        status = job.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    # Calculate oldest and newest jobs
    valid_timestamps = [job.get("created_at") for job in JOBS.values() if job.get("created_at")]
    oldest_job = min(valid_timestamps, default=None) if valid_timestamps else None
    newest_job = max(valid_timestamps, default=None) if valid_timestamps else None

    return {
        "total_jobs": total_jobs,
        "status_counts": status_counts,
        "oldest_job": oldest_job,
        "newest_job": newest_job,
        "concurrency_stats": get_queue_stats()
    }
