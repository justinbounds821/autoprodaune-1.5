"""
Video Service - Subset of main.py pentru Video Generation
Acest fișier rulează ca serviciu separat pe port 8003
Cu support pentru async processing prin Redis
"""
from __future__ import annotations
import logging
import os
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from redis import Redis

try:
    from dotenv import load_dotenv
    load_dotenv()
except: pass

log = logging.getLogger(__name__)

# Initialize FastAPI app pentru Video Service
app = FastAPI(
    title="AutoPro Video Service",
    version="3.0.0",
    description="Async video generation service"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection pentru async queue
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
try:
    redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    log.info(f"✅ Redis connected: {REDIS_URL}")
except Exception as e:
    log.warning(f"⚠️ Redis not available: {e}")
    redis_client = None

# Health
@app.get("/health")
def health():
    redis_status = "connected" if redis_client else "disconnected"
    return {
        "status": "ok", 
        "service": "video-service", 
        "port": int(os.getenv("PORT", "8003")),
        "redis": redis_status
    }

# Import DOAR routerele pentru video
try:
    from .routes.video import router as video_router
    from .routes.simple_video import router as simple_video_router
    from .routes.advanced_video import router as advanced_video_router
    
    app.include_router(video_router)
    app.include_router(simple_video_router)
    app.include_router(advanced_video_router)
    log.info("✅ Video routers loaded")
except Exception as e:
    log.error(f"❌ Failed to load video routers: {e}")

# Metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8003")))
