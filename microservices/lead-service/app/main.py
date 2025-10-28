"""
Lead Service - Microservice for lead management
Port: 8001
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import shared utilities
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

# Import local modules
from app.api import leads_router, scoring_router
from app.queue.consumers import start_lead_consumers


# Setup logging
setup_logging("lead-service", level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Lead Service starting up...")
    
    try:
        # Initialize database
        db = init_database(
            database_url=os.getenv("DATABASE_URL"),
            pool_size=10,
        )
        if await db.test_connection():
            logger.info("✅ Database connected")
        else:
            logger.error("❌ Database connection failed")
        
        # Initialize Redis cache
        cache = init_redis(redis_url=os.getenv("REDIS_URL", "redis://redis:6379/0"))
        if await cache.ping():
            logger.info("✅ Redis connected")
        else:
            logger.warning("⚠️ Redis connection failed")
        
        # Initialize RabbitMQ
        try:
            await init_rabbitmq(amqp_url=os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/"))
            logger.info("✅ RabbitMQ connected")
            
            # Start consuming messages
            await start_lead_consumers()
            logger.info("✅ Lead consumers started")
        except Exception as e:
            logger.warning(f"⚠️ RabbitMQ connection failed: {e}")
        
        logger.info("✅ Lead Service ready")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Lead Service shutting down...")
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


# Create FastAPI app
app = FastAPI(
    title="Lead Service",
    version="1.0.0",
    description="Microservice for lead management and scoring",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Prometheus metrics
metrics = setup_metrics(app, "lead-service")

# Setup health checks
health = init_health_check("lead-service")

async def check_database():
    try:
        db = get_database()
        return await db.test_connection()
    except:
        return False

async def check_redis():
    try:
        cache = get_redis()
        return await cache.ping()
    except:
        return False

async def check_rabbitmq():
    try:
        mq = get_mq_connection()
        return mq.connection is not None and not mq.connection.is_closed
    except:
        return False

health.add_check("database", check_database)
health.add_check("redis", check_redis)
health.add_check("rabbitmq", check_rabbitmq)

# Include routers
app.include_router(create_health_router(health))
app.include_router(leads_router, prefix="/api")
app.include_router(scoring_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "lead-service",
        "version": "1.0.0",
        "status": "operational",
        "port": 8001,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )
