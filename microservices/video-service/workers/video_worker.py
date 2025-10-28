"""
Video Worker - Process video generation jobs from Redis queue
Run multiple instances for parallel processing
"""
import asyncio
import json
import os
import sys
import logging
import httpx
from redis import Redis
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoWorker:
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.running = True
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        self.redis = Redis.from_url(self.redis_url, decode_responses=True)
        self.api_url = os.getenv("VIDEO_SERVICE_URL", "http://localhost:8000")
        
        logger.info(f"[Worker {worker_id}] Initialized")
        
    async def start(self):
        """Start processing jobs from Redis queue."""
        logger.info(f"[Worker {self.worker_id}] Starting...")
        
        # Create consumer group if not exists
        try:
            self.redis.xgroup_create("video_jobs_queue", "video_workers", id="0", mkstream=True)
        except Exception:
            pass  # Group already exists
        
        while self.running:
            try:
                # Read from queue (blocking for 5 seconds)
                messages = self.redis.xreadgroup(
                    groupname="video_workers",
                    consumername=f"worker_{self.worker_id}",
                    streams={"video_jobs_queue": ">"},
                    count=1,
                    block=5000
                )
                
                if messages:
                    for stream, message_list in messages:
                        for message_id, data in message_list:
                            try:
                                # Process job
                                payload = json.loads(data["payload"])
                                await self.process_job(payload)
                                
                                # Acknowledge message
                                self.redis.xack("video_jobs_queue", "video_workers", message_id)
                                
                            except Exception as e:
                                logger.error(f"[Worker {self.worker_id}] Job processing error: {e}")
                                
            except Exception as e:
                logger.error(f"[Worker {self.worker_id}] Queue reading error: {e}")
                await asyncio.sleep(5)
    
    async def process_job(self, job_data: dict):
        """Process a single video generation job."""
        job_id = job_data["job_id"]
        
        logger.info(f"[Worker {self.worker_id}] Processing job {job_id}")
        
        try:
            # Step 1: Update status to processing
            await self.update_progress(job_id, 0, "processing", "Starting video generation")
            
            # Step 2: Generate audio (30%)
            await asyncio.sleep(2)  # Simulate TTS generation
            audio_path = "/tmp/audio.mp3"
            await self.update_progress(job_id, 30, "processing", "Audio generated")
            
            # Step 3: Compose video (60%)
            await asyncio.sleep(5)  # Simulate video composition
            video_path = "/tmp/video.mp4"
            await self.update_progress(job_id, 60, "processing", "Video composed")
            
            # Step 4: Upload video (80%)
            await asyncio.sleep(2)  # Simulate upload
            video_url = f"https://example.com/videos/{job_id}.mp4"
            await self.update_progress(job_id, 80, "processing", "Video uploaded")
            
            # Step 5: Complete (100%)
            await self.update_progress(job_id, 100, "completed", "Video generation completed", video_url=video_url)
            
            logger.info(f"[Worker {self.worker_id}] Job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"[Worker {self.worker_id}] Job {job_id} failed: {e}")
            await self.update_progress(job_id, 0, "failed", f"Error: {str(e)}")
    
    async def update_progress(self, job_id: str, progress: int, status: str, message: str = "", video_url: str = None):
        """Send progress update to API."""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "job_id": job_id,
                    "progress": progress,
                    "status": status,
                    "message": message
                }
                if video_url:
                    params["video_url"] = video_url
                
                await client.post(
                    f"{self.api_url}/internal/update-progress",
                    params=params,
                    timeout=10.0
                )
                
                logger.info(f"[Worker {self.worker_id}] Progress update sent: {job_id} - {progress}%")
                
        except Exception as e:
            logger.error(f"[Worker {self.worker_id}] Failed to send progress: {e}")

# Entry point
if __name__ == "__main__":
    # Get worker ID from command line or use 1
    worker_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    worker = VideoWorker(worker_id)
    
    try:
        asyncio.run(worker.start())
    except KeyboardInterrupt:
        logger.info(f"[Worker {worker_id}] Shutting down...")
        worker.running = False
