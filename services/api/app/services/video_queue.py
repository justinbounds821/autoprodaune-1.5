"""
Video Queue System - Sistem de cozi pentru generarea de videoclipuri AI
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

# Configurează logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoJobStatus(Enum):
    """Statusurile unui job de generare video"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class VideoProvider(Enum):
    """Providerii de generare video"""
    PIKA = "pika"
    HEYGEN = "heygen"
    AUTO = "auto"  # Alege automat cel mai bun provider

@dataclass
class VideoJob:
    """Reprezentarea unui job de generare video"""
    id: str
    user_id: Optional[str]
    provider: VideoProvider
    request_data: Dict[str, Any]
    status: VideoJobStatus = VideoJobStatus.PENDING
    priority: int = 0  # 0 = normal, 1 = high, 2 = urgent
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    estimated_completion: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class QueueStats:
    """Statistici pentru coada de video"""
    total_jobs: int
    pending_jobs: int
    processing_jobs: int
    completed_jobs: int
    failed_jobs: int
    average_processing_time: float
    success_rate: float

class VideoQueue:
    """Coada pentru gestionarea job-urilor de generare video"""
    
    def __init__(self, max_concurrent_jobs: int = 3):
        self.max_concurrent_jobs = max_concurrent_jobs
        self.jobs: Dict[str, VideoJob] = {}
        self.processing_jobs: Dict[str, VideoJob] = {}
        self.job_callbacks: Dict[str, List[Callable]] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_jobs)
        self._lock = asyncio.Lock()
        self._shutdown = False
        
        # Statistici
        self.stats = {
            "total_processed": 0,
            "total_successful": 0,
            "total_failed": 0,
            "total_processing_time": 0.0
        }
    
    async def add_job(
        self,
        user_id: Optional[str],
        provider: VideoProvider,
        request_data: Dict[str, Any],
        priority: int = 0,
        max_retries: int = 3
    ) -> str:
        """
        Adaugă un job nou în coadă
        
        Args:
            user_id: ID-ul utilizatorului
            provider: Providerul de video
            request_data: Datele pentru generarea video
            priority: Prioritatea job-ului
            max_retries: Numărul maxim de încercări
            
        Returns:
            ID-ul job-ului creat
        """
        job_id = str(uuid.uuid4())
        
        job = VideoJob(
            id=job_id,
            user_id=user_id,
            provider=provider,
            request_data=request_data,
            priority=priority,
            max_retries=max_retries
        )
        
        async with self._lock:
            self.jobs[job_id] = job
            logger.info(f"Job {job_id} adăugat în coadă cu prioritatea {priority}")
        
        # Pornește procesarea dacă nu sunt job-uri în execuție
        await self._start_processing()
        
        return job_id
    
    async def get_job(self, job_id: str) -> Optional[VideoJob]:
        """
        Returnează un job după ID
        
        Args:
            job_id: ID-ul job-ului
            
        Returns:
            VideoJob sau None dacă nu există
        """
        async with self._lock:
            return self.jobs.get(job_id)
    
    async def get_user_jobs(self, user_id: str, limit: int = 50) -> List[VideoJob]:
        """
        Returnează job-urile unui utilizator
        
        Args:
            user_id: ID-ul utilizatorului
            limit: Numărul maxim de job-uri de returnat
            
        Returns:
            Lista de job-uri
        """
        async with self._lock:
            user_jobs = [
                job for job in self.jobs.values()
                if job.user_id == user_id
            ]
            
            # Sortează după data creării (cele mai recente primul)
            user_jobs.sort(key=lambda x: x.created_at, reverse=True)
            
            return user_jobs[:limit]
    
    async def cancel_job(self, job_id: str) -> bool:
        """
        Anulează un job
        
        Args:
            job_id: ID-ul job-ului
            
        Returns:
            True dacă job-ul a fost anulat
        """
        async with self._lock:
            job = self.jobs.get(job_id)
            if job and job.status in [VideoJobStatus.PENDING, VideoJobStatus.RETRYING]:
                job.status = VideoJobStatus.CANCELLED
                job.completed_at = datetime.now()
                logger.info(f"Job {job_id} anulat")
                return True
            return False
    
    async def retry_job(self, job_id: str) -> bool:
        """
        Reîncearcă un job eșuat
        
        Args:
            job_id: ID-ul job-ului
            
        Returns:
            True dacă job-ul a fost repornit
        """
        async with self._lock:
            job = self.jobs.get(job_id)
            if job and job.status == VideoJobStatus.FAILED and job.retry_count < job.max_retries:
                job.status = VideoJobStatus.RETRYING
                job.retry_count += 1
                job.error_message = None
                logger.info(f"Job {job_id} repornit (încercarea {job.retry_count})")
                
                # Pornește procesarea
                await self._start_processing()
                return True
            return False
    
    async def get_queue_stats(self) -> QueueStats:
        """
        Returnează statisticile cozii
        
        Returns:
            QueueStats cu statisticile actuale
        """
        async with self._lock:
            total_jobs = len(self.jobs)
            pending_jobs = sum(1 for job in self.jobs.values() if job.status == VideoJobStatus.PENDING)
            processing_jobs = len(self.processing_jobs)
            completed_jobs = sum(1 for job in self.jobs.values() if job.status == VideoJobStatus.COMPLETED)
            failed_jobs = sum(1 for job in self.jobs.values() if job.status == VideoJobStatus.FAILED)
            
            # Calculează timpul mediu de procesare
            completed_jobs_with_time = [
                job for job in self.jobs.values()
                if job.status == VideoJobStatus.COMPLETED and job.started_at and job.completed_at
            ]
            
            if completed_jobs_with_time:
                total_time = sum(
                    (job.completed_at - job.started_at).total_seconds()
                    for job in completed_jobs_with_time
                )
                average_processing_time = total_time / len(completed_jobs_with_time)
            else:
                average_processing_time = 0.0
            
            # Calculează rata de succes
            total_processed = completed_jobs + failed_jobs
            success_rate = (completed_jobs / total_processed * 100) if total_processed > 0 else 0.0
            
            return QueueStats(
                total_jobs=total_jobs,
                pending_jobs=pending_jobs,
                processing_jobs=processing_jobs,
                completed_jobs=completed_jobs,
                failed_jobs=failed_jobs,
                average_processing_time=average_processing_time,
                success_rate=success_rate
            )
    
    async def _start_processing(self):
        """Pornește procesarea job-urilor dacă este posibil"""
        if self._shutdown:
            return
        
        async with self._lock:
            # Verifică dacă mai sunt sloturi disponibile
            if len(self.processing_jobs) >= self.max_concurrent_jobs:
                return
            
            # Găsește următorul job de procesat
            next_job = self._get_next_job()
            if not next_job:
                return
            
            # Marchează job-ul ca fiind în procesare
            next_job.status = VideoJobStatus.PROCESSING
            next_job.started_at = datetime.now()
            self.processing_jobs[next_job.id] = next_job
            
            logger.info(f"Pornit procesarea job-ului {next_job.id}")
            
            # Pornește procesarea în background
            asyncio.create_task(self._process_job(next_job))
    
    def _get_next_job(self) -> Optional[VideoJob]:
        """
        Returnează următorul job de procesat
        
        Returns:
            VideoJob sau None
        """
        # Sortează job-urile după prioritate și data creării
        pending_jobs = [
            job for job in self.jobs.values()
            if job.status in [VideoJobStatus.PENDING, VideoJobStatus.RETRYING]
        ]
        
        if not pending_jobs:
            return None
        
        # Sortează după prioritate (descrescător) și data creării (crescător)
        pending_jobs.sort(key=lambda x: (-x.priority, x.created_at))
        
        return pending_jobs[0]
    
    async def _process_job(self, job: VideoJob):
        """
        Procesează un job de generare video
        
        Args:
            job: Job-ul de procesat
        """
        try:
            logger.info(f"Procesez job-ul {job.id} cu provider-ul {job.provider.value}")
            
            # Importă serviciul corespunzător
            if job.provider == VideoProvider.PIKA:
                from app.services.pika_service import get_pika_service, PikaVideoRequest, VideoStyle, VideoAspectRatio
                
                service = get_pika_service()
                
                # Convertește datele request-ului
                request = PikaVideoRequest(
                    prompt=job.request_data.get("prompt", ""),
                    style=VideoStyle(job.request_data.get("style", "cinematic")),
                    aspect_ratio=VideoAspectRatio(job.request_data.get("aspect_ratio", "16:9")),
                    duration=job.request_data.get("duration", 5),
                    seed=job.request_data.get("seed"),
                    negative_prompt=job.request_data.get("negative_prompt"),
                    guidance_scale=job.request_data.get("guidance_scale", 7.5),
                    num_inference_steps=job.request_data.get("num_inference_steps", 20)
                )
                
                result = await service.generate_video(request)
                
            elif job.provider == VideoProvider.HEYGEN:
                from app.services.heygen_service import get_heygen_service, HeyGenVideoRequest, HeyGenVideoStyle, HeyGenVideoQuality
                
                service = get_heygen_service()
                
                # Convertește datele request-ului
                request = HeyGenVideoRequest(
                    script=job.request_data.get("script", ""),
                    voice_id=job.request_data.get("voice_id"),
                    avatar_id=job.request_data.get("avatar_id"),
                    style=HeyGenVideoStyle(job.request_data.get("style", "realistic")),
                    quality=HeyGenVideoQuality(job.request_data.get("quality", "high")),
                    background_music=job.request_data.get("background_music", False),
                    subtitles=job.request_data.get("subtitles", True),
                    language=job.request_data.get("language", "en"),
                    speed=job.request_data.get("speed", 1.0)
                )
                
                result = await service.generate_video(request)
                
            else:
                raise ValueError(f"Provider necunoscut: {job.provider}")
            
            # Actualizează statusul job-ului
            async with self._lock:
                if result.success:
                    job.status = VideoJobStatus.COMPLETED
                    job.result_data = {
                        "video_id": result.video_id,
                        "video_url": result.video_url,
                        "thumbnail_url": result.thumbnail_url,
                        "status": result.status,
                        "created_at": result.created_at.isoformat() if result.created_at else None,
                        "estimated_completion": result.estimated_completion.isoformat() if result.estimated_completion else None
                    }
                    self.stats["total_successful"] += 1
                    logger.info(f"Job {job.id} completat cu succes")
                else:
                    job.status = VideoJobStatus.FAILED
                    job.error_message = result.error_message
                    self.stats["total_failed"] += 1
                    logger.error(f"Job {job.id} eșuat: {result.error_message}")
                
                job.completed_at = datetime.now()
                
                # Calculează timpul de procesare
                if job.started_at:
                    processing_time = (job.completed_at - job.started_at).total_seconds()
                    self.stats["total_processing_time"] += processing_time
                
                self.stats["total_processed"] += 1
                
                # Elimină job-ul din lista de procesare
                if job.id in self.processing_jobs:
                    del self.processing_jobs[job.id]
            
            # Apelează callback-urile
            await self._notify_callbacks(job)
            
            # Pornește următorul job
            await self._start_processing()
            
        except Exception as e:
            logger.error(f"Eroare la procesarea job-ului {job.id}: {str(e)}")
            
            async with self._lock:
                job.status = VideoJobStatus.FAILED
                job.error_message = str(e)
                job.completed_at = datetime.now()
                
                if job.id in self.processing_jobs:
                    del self.processing_jobs[job.id]
                
                self.stats["total_failed"] += 1
            
            # Apelează callback-urile
            await self._notify_callbacks(job)
            
            # Pornește următorul job
            await self._start_processing()
    
    async def _notify_callbacks(self, job: VideoJob):
        """
        Apelează callback-urile pentru un job
        
        Args:
            job: Job-ul pentru care să apeleze callback-urile
        """
        callbacks = self.job_callbacks.get(job.id, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(job)
                else:
                    callback(job)
            except Exception as e:
                logger.error(f"Eroare la apelarea callback-ului pentru job {job.id}: {str(e)}")
    
    def add_job_callback(self, job_id: str, callback: Callable):
        """
        Adaugă un callback pentru un job
        
        Args:
            job_id: ID-ul job-ului
            callback: Funcția callback
        """
        if job_id not in self.job_callbacks:
            self.job_callbacks[job_id] = []
        self.job_callbacks[job_id].append(callback)
    
    async def cleanup_old_jobs(self, days: int = 7):
        """
        Curăță job-urile vechi
        
        Args:
            days: Numărul de zile după care să șteargă job-urile
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        async with self._lock:
            jobs_to_remove = [
                job_id for job_id, job in self.jobs.items()
                if job.completed_at and job.completed_at < cutoff_date
            ]
            
            for job_id in jobs_to_remove:
                del self.jobs[job_id]
                if job_id in self.job_callbacks:
                    del self.job_callbacks[job_id]
            
            logger.info(f"Șters {len(jobs_to_remove)} job-uri vechi")
    
    async def shutdown(self):
        """Oprește coada și așteaptă ca toate job-urile să se termine"""
        logger.info("Oprește coada de video...")
        self._shutdown = True
        
        # Așteaptă ca toate job-urile să se termine
        while self.processing_jobs:
            await asyncio.sleep(1)
        
        self.executor.shutdown(wait=True)
        logger.info("Coada de video oprită")

# Singleton instance
_video_queue = None

class VideoQueueSupabase:
    """Wrapper pentru integrarea VideoQueue cu Supabase."""
    
    def enqueue(self, payload: dict) -> str:
        """Enqueue job în Supabase și returnează job_id."""
        try:
            from .supabase_client import supabase_service
            
            # Generează job_id unic
            job_id = f"manole_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Pregătește payload pentru Supabase
            job_data = {
                "client_job_id": job_id,
                "type": payload.get("type", "manole"),
                "status": "queued",
                "progress": 0,
                "payload": payload,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Inserează în Supabase
            result = supabase_service._table_insert("video_jobs", job_data)
            
            logger.info(f"Job {job_id} enqueued successfully")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to enqueue job: {e}")
            raise
    
    def update_status(self, job_id: str, status: str, **kwargs):
        """Actualizează statusul job-ului în Supabase."""
        try:
            from .supabase_client import supabase_service
            
            update_data = {
                "status": status,
                "updated_at": datetime.now().isoformat()
            }
            
            # Adaugă câmpuri opționale
            if "progress" in kwargs:
                update_data["progress"] = kwargs["progress"]
            if "output_url" in kwargs:
                update_data["output_url"] = kwargs["output_url"]
            if "error_message" in kwargs:
                update_data["error_message"] = kwargs["error_message"]
            if "file_size_mb" in kwargs:
                update_data["file_size_mb"] = kwargs["file_size_mb"]
            if "completed_at" in kwargs:
                update_data["completed_at"] = kwargs["completed_at"]
            
            # Actualizează în Supabase
            supabase_service._table_update_eq("video_jobs", "client_job_id", job_id, update_data)
            logger.info(f"Job {job_id} status updated to {status}")
            
        except Exception as e:
            logger.error(f"Failed to update job {job_id} status: {e}")
            raise
    
    def get_jobs(self, status: str = None) -> List[dict]:
        """Returnează lista de job-uri din Supabase."""
        try:
            from .supabase_client import supabase_service
            
            filters = []
            if status:
                filters.append(("eq", "status", status))
            
            jobs = supabase_service._table_select("video_jobs", "*", filters=filters)
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to get jobs: {e}")
            return []
    
    def retry_job(self, job_id: str):
        """Resetează job-ul pentru retry."""
        try:
            self.update_status(job_id, "queued", error_message=None)
            logger.info(f"Job {job_id} marked for retry")
            
        except Exception as e:
            logger.error(f"Failed to retry job {job_id}: {e}")
            raise

def get_video_queue() -> VideoQueue:
    """Returnează instanța singleton a VideoQueue"""
    global _video_queue
    if _video_queue is None:
        _video_queue = VideoQueue()
    return _video_queue
