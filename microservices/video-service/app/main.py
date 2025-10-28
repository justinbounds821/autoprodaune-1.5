"""
Video Service - Async Video Generation
Port: 8002 (8000 intern)
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from redis import Redis
from typing import Dict, Optional
import asyncio
import uuid
import json
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AutoPro Video Service",
    version="3.0.0",
    description="Async video generation with worker pool"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
try:
    redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    logger.info(f"✅ Redis connected: {REDIS_URL}")
except Exception as e:
    logger.error(f"❌ Redis connection failed: {e}")
    redis_client = None

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[job_id] = websocket
        logger.info(f"WebSocket connected for job {job_id}")
    
    async def disconnect(self, job_id: str):
        if job_id in self.active_connections:
            del self.active_connections[job_id]
            logger.info(f"WebSocket disconnected for job {job_id}")
    
    async def send_progress(self, job_id: str, progress: int, status: str, **kwargs):
        if job_id in self.active_connections:
            message = {
                "job_id": job_id,
                "progress": progress,
                "status": status,
                "timestamp": datetime.now().isoformat(),
                **kwargs
            }
            try:
                await self.active_connections[job_id].send_json(message)
                logger.info(f"Progress update sent for job {job_id}: {progress}%")
            except Exception as e:
                logger.error(f"Failed to send progress for job {job_id}: {e}")

manager = ConnectionManager()

# Request Models
class VideoGenerateRequest(BaseModel):
    prompt: str
    duration: int = 30
    resolution: str = "1080p"
    tts_text: Optional[str] = None
    bg_type: str = "color"
    bg_value: str = "#073B7A"

# Health check
@app.get("/health")
def health():
    redis_status = "connected" if redis_client and redis_client.ping() else "disconnected"
    return {
        "service": "video-service",
        "status": "healthy",
        "version": "3.0.0",
        "redis": redis_status,
        "port": int(os.getenv("PORT", "8000"))
    }

# Generate video endpoint (async - returns immediately)
@app.post("/api/video/generate")
async def generate_video(request: VideoGenerateRequest):
    """
    Enqueue video generation job.
    Returns immediately with job_id for tracking.
    """
    try:
        # Create job
        job_id = str(uuid.uuid4())
        job_data = {
            "job_id": job_id,
            "prompt": request.prompt,
            "duration": request.duration,
            "resolution": request.resolution,
            "tts_text": request.tts_text,
            "bg_type": request.bg_type,
            "bg_value": request.bg_value,
            "status": "queued",
            "progress": 0,
            "created_at": datetime.now().isoformat()
        }
        
        # Store in Redis (as fallback if no Supabase)
        if redis_client:
            redis_client.set(f"video_job:{job_id}", json.dumps(job_data), ex=3600)
            
            # Push to queue
            redis_client.xadd("video_jobs_queue", {
                "job_id": job_id,
                "payload": json.dumps(job_data)
            })
            
            logger.info(f"✅ Video job {job_id} enqueued")
        else:
            logger.warning("⚠️ Redis not available, job cannot be queued")
            raise HTTPException(status_code=503, detail="Video service unavailable (Redis offline)")
        
        return {
            "success": True,
            "job_id": job_id,
            "status": "queued",
            "message": "Video generation queued. Connect to WebSocket for progress updates.",
            "websocket_url": f"ws://localhost:8002/api/video/progress?job_id={job_id}"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to enqueue video job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to enqueue job: {str(e)}")

# Get job status
@app.get("/api/video/status/{job_id}")
async def get_video_status(job_id: str):
    """Get current status of video generation job."""
    try:
        if redis_client:
            job_data = redis_client.get(f"video_job:{job_id}")
            if job_data:
                return json.loads(job_data)
        
        raise HTTPException(status_code=404, detail="Job not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for progress updates
@app.websocket("/api/video/progress")
async def video_progress_websocket(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time progress updates.
    Usage: ws://localhost:8002/api/video/progress?job_id=xxx
    """
    await manager.connect(job_id, websocket)
    
    try:
        # Send initial status
        if redis_client:
            job_data = redis_client.get(f"video_job:{job_id}")
            if job_data:
                await websocket.send_json(json.loads(job_data))
        
        # Keep connection alive
        while True:
            await asyncio.sleep(1)
            
            # Check if job is completed
            if redis_client:
                job_data = redis_client.get(f"video_job:{job_id}")
                if job_data:
                    data = json.loads(job_data)
                    if data["status"] in ["completed", "failed"]:
                        await websocket.send_json(data)
                        break
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for job {job_id}")
    finally:
        await manager.disconnect(job_id)

# Internal endpoint for workers to update progress
@app.post("/internal/update-progress")
async def update_progress(
    job_id: str,
    progress: int,
    status: str,
    message: str = "",
    video_url: str = None
):
    """Internal endpoint for workers to update job progress."""
    try:
        # Update Redis
        if redis_client:
            job_data = redis_client.get(f"video_job:{job_id}")
            if job_data:
                data = json.loads(job_data)
                data.update({
                    "progress": progress,
                    "status": status,
                    "message": message,
                    "updated_at": datetime.now().isoformat()
                })
                if video_url:
                    data["video_url"] = video_url
                
                redis_client.set(f"video_job:{job_id}", json.dumps(data), ex=3600)
        
        # Send WebSocket update
        await manager.send_progress(
            job_id, 
            progress, 
            status, 
            message=message,
            video_url=video_url
        )
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Failed to update progress: {e}")
        return {"success": False, "error": str(e)}

# List all jobs
@app.get("/api/video/jobs")
async def list_jobs(limit: int = 50):
    """List recent video jobs."""
    try:
        if not redis_client:
            return {"jobs": [], "message": "Redis unavailable"}
        
        # Get all job keys
        job_keys = redis_client.keys("video_job:*")
        jobs = []
        
        for key in job_keys[:limit]:
            job_data = redis_client.get(key)
            if job_data:
                jobs.append(json.loads(job_data))
        
        # Sort by created_at (newest first)
        jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return {
            "jobs": jobs[:limit],
            "total": len(jobs)
        }
        
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

logger.info("🚀 Video Service started")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
