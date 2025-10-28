"""
Whatsapp Service
Port: 8009
Description: WhatsApp integration and bot
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import sys
sys.path.insert(0, "/workspace/microservices/autopro-common")

from autopro_common import (
    setup_logging,
    get_logger,
    init_database,
    init_redis,
    init_rabbitmq,
    setup_metrics,
    init_health_check,
    create_health_router,
    get_database,
    get_redis,
    get_mq_connection,
)

from app.api import router as api_router

setup_logging("whatsapp-service", level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Whatsapp Service starting up...")
    
    try:
        db = init_database(database_url=os.getenv("DATABASE_URL"), pool_size=10)
        if await db.test_connection():
            logger.info("✅ Database connected")
        
        cache = init_redis(redis_url=os.getenv("REDIS_URL", "redis://redis:6379/0"))
        if await cache.ping():
            logger.info("✅ Redis connected")
        
        try:
            await init_rabbitmq(amqp_url=os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/"))
            logger.info("✅ RabbitMQ connected")
        except Exception as e:
            logger.warning(f"⚠️ RabbitMQ connection failed: {e}")
        
        logger.info("✅ Whatsapp Service ready")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    logger.info("🛑 Whatsapp Service shutting down...")
    try:
        db = get_database()
        await db.close()
        cache = get_redis()
        await cache.close()
        try:
            mq = get_mq_connection()
            await mq.close()
        except:
            pass
        logger.info("✅ All connections closed")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")


app = FastAPI(
    title="Whatsapp Service",
    version="1.0.0",
    description="WhatsApp integration and bot",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

metrics = setup_metrics(app, "whatsapp-service")
health = init_health_check("whatsapp-service")

async def check_database():
    try:
        return await get_database().test_connection()
    except:
        return False

async def check_redis():
    try:
        return await get_redis().ping()
    except:
        return False

health.add_check("database", check_database)
health.add_check("redis", check_redis)

app.include_router(create_health_router(health))
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "service": "whatsapp-service",
        "version": "1.0.0",
        "status": "operational",
        "port": 8009,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8009, reload=True)
