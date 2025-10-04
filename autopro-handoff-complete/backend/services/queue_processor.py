"""
Queue Processor - Worker pentru procesarea cozii de generare video
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import signal
import sys
from contextlib import asynccontextmanager

# Configurează logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProcessorStatus(Enum):
    """Statusurile procesorului"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"

@dataclass
class ProcessorConfig:
    """Configurația procesorului"""
    max_concurrent_jobs: int = 3
    poll_interval: float = 5.0  # secunde
    cleanup_interval: float = 3600.0  # 1 oră
    max_retries: int = 3
    retry_delay: float = 60.0  # secunde
    health_check_interval: float = 300.0  # 5 minute

class QueueProcessor:
    """Procesor pentru coada de generare video"""
    
    def __init__(self, config: Optional[ProcessorConfig] = None):
        self.config = config or ProcessorConfig()
        self.status = ProcessorStatus.STOPPED
        self.start_time: Optional[datetime] = None
        self.last_health_check: Optional[datetime] = None
        self.processed_jobs = 0
        self.failed_jobs = 0
        self._tasks: List[asyncio.Task] = []
        self._shutdown_event = asyncio.Event()
        
        # Importă coada
        from services.video_queue import get_video_queue
        self.queue = get_video_queue()
    
    async def start(self):
        """Pornește procesorul"""
        if self.status != ProcessorStatus.STOPPED:
            logger.warning("Procesorul este deja pornit sau în proces de pornire")
            return
        
        logger.info("Pornește procesorul de coadă...")
        self.status = ProcessorStatus.STARTING
        self.start_time = datetime.now()
        
        try:
            # Pornește task-urile principale
            self._tasks = [
                asyncio.create_task(self._health_check_loop()),
                asyncio.create_task(self._cleanup_loop()),
                asyncio.create_task(self._monitoring_loop())
            ]
            
            self.status = ProcessorStatus.RUNNING
            logger.info("Procesorul pornit cu succes")
            
            # Așteaptă semnalul de oprire
            await self._shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"Eroare la pornirea procesorului: {str(e)}")
            self.status = ProcessorStatus.ERROR
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """Oprește procesorul"""
        if self.status == ProcessorStatus.STOPPED:
            return
        
        logger.info("Oprește procesorul de coadă...")
        self.status = ProcessorStatus.STOPPING
        
        # Anulează toate task-urile
        for task in self._tasks:
            if not task.done():
                task.cancel()
        
        # Așteaptă ca task-urile să se termine
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        
        # Oprește coada
        await self.queue.shutdown()
        
        self.status = ProcessorStatus.STOPPED
        logger.info("Procesorul oprit")
    
    async def _health_check_loop(self):
        """Loop pentru verificarea sănătății procesorului"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config.health_check_interval)
                
                if self._shutdown_event.is_set():
                    break
                
                await self._perform_health_check()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Eroare în health check loop: {str(e)}")
    
    async def _cleanup_loop(self):
        """Loop pentru curățarea job-urilor vechi"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                
                if self._shutdown_event.is_set():
                    break
                
                await self._perform_cleanup()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Eroare în cleanup loop: {str(e)}")
    
    async def _monitoring_loop(self):
        """Loop pentru monitorizarea performanței"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Monitorizează la fiecare minut
                
                if self._shutdown_event.is_set():
                    break
                
                await self._log_performance_stats()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Eroare în monitoring loop: {str(e)}")
    
    async def _perform_health_check(self):
        """Verifică sănătatea procesorului"""
        try:
            self.last_health_check = datetime.now()
            
            # Verifică statisticile cozii
            stats = await self.queue.get_queue_stats()
            
            # Verifică dacă există job-uri blocate
            blocked_jobs = 0
            for job in self.queue.jobs.values():
                if (job.status.value in ["processing"] and 
                    job.started_at and 
                    datetime.now() - job.started_at > timedelta(hours=2)):
                    blocked_jobs += 1
            
            if blocked_jobs > 0:
                logger.warning(f"Găsite {blocked_jobs} job-uri blocate")
            
            # Verifică memoria și resursele
            import psutil
            memory_percent = psutil.virtual_memory().percent
            cpu_percent = psutil.cpu_percent()
            
            if memory_percent > 90:
                logger.warning(f"Utilizarea memoriei este ridicată: {memory_percent}%")
            
            if cpu_percent > 90:
                logger.warning(f"Utilizarea CPU este ridicată: {cpu_percent}%")
            
            logger.info(f"Health check OK - Memorie: {memory_percent}%, CPU: {cpu_percent}%")
            
        except Exception as e:
            logger.error(f"Eroare la health check: {str(e)}")
    
    async def _perform_cleanup(self):
        """Curăță job-urile vechi"""
        try:
            await self.queue.cleanup_old_jobs(days=7)
            logger.info("Cleanup completat")
        except Exception as e:
            logger.error(f"Eroare la cleanup: {str(e)}")
    
    async def _log_performance_stats(self):
        """Loghează statisticile de performanță"""
        try:
            stats = await self.queue.get_queue_stats()
            
            logger.info(
                f"Stats: Total={stats.total_jobs}, "
                f"Pending={stats.pending_jobs}, "
                f"Processing={stats.processing_jobs}, "
                f"Completed={stats.completed_jobs}, "
                f"Failed={stats.failed_jobs}, "
                f"Success Rate={stats.success_rate:.1f}%, "
                f"Avg Time={stats.average_processing_time:.1f}s"
            )
            
        except Exception as e:
            logger.error(f"Eroare la logarea statisticilor: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Returnează statusul procesorului"""
        uptime = None
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "uptime_seconds": uptime,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "processed_jobs": self.processed_jobs,
            "failed_jobs": self.failed_jobs,
            "config": {
                "max_concurrent_jobs": self.config.max_concurrent_jobs,
                "poll_interval": self.config.poll_interval,
                "cleanup_interval": self.config.cleanup_interval,
                "max_retries": self.config.max_retries,
                "retry_delay": self.config.retry_delay
            }
        }
    
    async def restart(self):
        """Repornește procesorul"""
        logger.info("Repornește procesorul...")
        await self.stop()
        await asyncio.sleep(2)  # Pauză scurtă
        await self.start()
    
    def signal_handler(self, signum, frame):
        """Handler pentru semnalele de oprire"""
        logger.info(f"Primit semnal {signum}, oprește procesorul...")
        self._shutdown_event.set()

# Context manager pentru rularea procesorului
@asynccontextmanager
async def run_processor(config: Optional[ProcessorConfig] = None):
    """
    Context manager pentru rularea procesorului
    
    Usage:
        async with run_processor() as processor:
            # Procesorul rulează
            pass
        # Procesorul se oprește automat
    """
    processor = QueueProcessor(config)
    
    # Configurează handler-ele pentru semnale
    signal.signal(signal.SIGINT, processor.signal_handler)
    signal.signal(signal.SIGTERM, processor.signal_handler)
    
    try:
        await processor.start()
        yield processor
    finally:
        await processor.stop()

# Funcție pentru rularea procesorului ca script standalone
async def main():
    """Funcția principală pentru rularea procesorului"""
    config = ProcessorConfig(
        max_concurrent_jobs=3,
        poll_interval=5.0,
        cleanup_interval=3600.0,
        max_retries=3,
        retry_delay=60.0,
        health_check_interval=300.0
    )
    
    async with run_processor(config) as processor:
        logger.info("Procesorul rulează. Apasă Ctrl+C pentru oprire.")
        
        # Așteaptă până când se primește semnalul de oprire
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Primit Ctrl+C, oprește procesorul...")

if __name__ == "__main__":
    asyncio.run(main())
