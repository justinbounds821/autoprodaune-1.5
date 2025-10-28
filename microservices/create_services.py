"""
Script to generate all microservices with standardized structure
"""
import os
from pathlib import Path

SERVICES = {
    "video-service": {
        "port": 8002,
        "description": "Video generation and processing engine",
        "features": ["video_generation", "template_management", "heygen_integration", "video_queue"],
        "dependencies": ["moviepy==1.0.3", "opencv-python==4.9.0.80", "Pillow==10.2.0", "openai==1.6.1"],
    },
    "social-service": {
        "port": 8003,
        "description": "Social media integrations and posting",
        "features": ["tiktok_posting", "instagram_posting", "facebook_posting", "youtube_posting", "scheduler"],
        "dependencies": ["instagrapi==2.0.0", "google-api-python-client==2.111.0", "httpx==0.25.0"],
    },
    "financial-service": {
        "port": 8004,
        "description": "Financial tracking and invoicing",
        "features": ["cost_calculation", "roi_tracking", "invoicing", "expense_management"],
        "dependencies": ["stripe==7.0.0", "reportlab==4.0.7"],
    },
    "referral-service": {
        "port": 8005,
        "description": "Referral program management",
        "features": ["referral_creation", "commission_tracking", "reward_management", "analytics"],
        "dependencies": [],
    },
    "automation-service": {
        "port": 8006,
        "description": "Workflow automation and scheduling",
        "features": ["workflow_execution", "scheduling", "trigger_management", "action_execution"],
        "dependencies": ["apscheduler==3.10.4", "croniter==2.0.1"],
    },
    "notification-service": {
        "port": 8007,
        "description": "Multi-channel notification delivery",
        "features": ["email_sending", "sms_sending", "push_notifications", "template_management"],
        "dependencies": ["sendgrid==6.10.0", "twilio==8.10.0", "jinja2==3.1.2"],
    },
    "analytics-service": {
        "port": 8008,
        "description": "Business metrics and analytics",
        "features": ["metrics_collection", "reporting", "dashboard_data", "kpi_calculation"],
        "dependencies": ["pandas==2.1.0", "numpy==1.25.0"],
    },
    "whatsapp-service": {
        "port": 8009,
        "description": "WhatsApp integration and bot",
        "features": ["webhook_handling", "message_sending", "group_management", "bot_responses"],
        "dependencies": ["twilio==8.10.0"],
    },
    "mcp-service": {
        "port": 8010,
        "description": "MCP orchestration (Python-only)",
        "features": ["linear_integration", "github_integration", "supabase_integration", "task_orchestration"],
        "dependencies": ["httpx==0.25.0", "pydantic==2.5.3"],
    },
}


def generate_main_py(service_name: str, config: dict) -> str:
    """Generate main.py for a service"""
    service_title = service_name.replace("-", " ").title()
    return f'''"""
{service_title}
Port: {config["port"]}
Description: {config["description"]}
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

setup_logging("{service_name}", level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 {service_title} starting up...")
    
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
            logger.warning(f"⚠️ RabbitMQ connection failed: {{e}}")
        
        logger.info("✅ {service_title} ready")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {{e}}")
        raise
    
    yield
    
    logger.info("🛑 {service_title} shutting down...")
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
        logger.error(f"❌ Shutdown error: {{e}}")


app = FastAPI(
    title="{service_title}",
    version="1.0.0",
    description="{config["description"]}",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

metrics = setup_metrics(app, "{service_name}")
health = init_health_check("{service_name}")

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
    return {{
        "service": "{service_name}",
        "version": "1.0.0",
        "status": "operational",
        "port": {config["port"]},
    }}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port={config["port"]}, reload=True)
'''


def generate_dockerfile(service_name: str, config: dict) -> str:
    """Generate Dockerfile for a service"""
    return f'''FROM python:3.11-slim as builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*

COPY microservices/autopro-common /build/autopro-common
RUN cd /build/autopro-common && pip install --user -e .

COPY microservices/{service_name}/requirements.txt /build/
RUN pip install --user -r /build/requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY microservices/autopro-common /workspace/microservices/autopro-common
COPY microservices/{service_name}/app /app/app

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE {config["port"]}

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:{config["port"]}/health/live')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "{config["port"]}", "--log-level", "info"]
'''


def generate_requirements(service_name: str, config: dict) -> str:
    """Generate requirements.txt for a service"""
    base_deps = [
        "fastapi>=0.110.0",
        "uvicorn[standard]>=0.27.0",
        "sqlalchemy[asyncio]>=2.0.0",
        "asyncpg>=0.29.0",
        "redis[hiredis]>=5.0.0",
        "aio-pika>=9.3.0",
        "pydantic>=2.5.0",
        "prometheus-client>=0.19.0",
    ]
    
    all_deps = base_deps + config.get("dependencies", [])
    return "\\n".join(all_deps) + "\\n"


def generate_api_router(service_name: str, config: dict) -> str:
    """Generate API router for a service"""
    service_title = service_name.replace("-", " ").title()
    return f'''"""
{service_title} API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

import sys
sys.path.insert(0, "/workspace/microservices/autopro-common")
from autopro_common import get_db_session, get_logger, get_metrics

router = APIRouter(tags=["{service_name}"])
logger = get_logger(__name__)


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """Get service status"""
    return {{
        "service": "{service_name}",
        "status": "operational",
        "features": {config["features"]},
    }}


@router.get("/info")
async def get_info() -> Dict[str, Any]:
    """Get service information"""
    return {{
        "service": "{service_name}",
        "description": "{config["description"]}",
        "version": "1.0.0",
        "features": {config["features"]},
    }}
'''


def create_service(service_name: str, config: dict):
    """Create a complete microservice"""
    base_path = Path(f"/workspace/microservices/{service_name}")
    
    # Create main.py
    (base_path / "app" / "main.py").write_text(generate_main_py(service_name, config))
    
    # Create __init__.py files
    (base_path / "app" / "__init__.py").write_text(f'"""{service_name.replace("-", " ").title()}"""\\n__version__ = "1.0.0"\\n')
    (base_path / "app" / "api" / "__init__.py").write_text(f'from .routes import router\\n__all__ = ["router"]\\n')
    (base_path / "app" / "services" / "__init__.py").write_text("")
    (base_path / "app" / "models" / "__init__.py").write_text("")
    (base_path / "app" / "queue" / "__init__.py").write_text("")
    
    # Create API router
    (base_path / "app" / "api" / "routes.py").write_text(generate_api_router(service_name, config))
    
    # Create Dockerfile
    (base_path / "Dockerfile").write_text(generate_dockerfile(service_name, config))
    
    # Create requirements.txt
    (base_path / "requirements.txt").write_text(generate_requirements(service_name, config))
    
    # Create README.md
    readme = f"""# {service_name.replace("-", " ").title()}

{config["description"]}

## Port: {config["port"]}

## Features

{chr(10).join(f"- {f}" for f in config["features"])}

## Running

```bash
docker build -t {service_name}:latest .
docker run -p {config["port"]}:{config["port"]} {service_name}:latest
```

## API Endpoints

- `GET /` - Service info
- `GET /api/status` - Service status
- `GET /api/info` - Detailed information
- `GET /health` - Health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe
- `GET /metrics` - Prometheus metrics
"""
    (base_path / "README.md").write_text(readme)
    
    print(f"✅ {service_name} created successfully")


# Generate all services
if __name__ == "__main__":
    for service_name, config in SERVICES.items():
        create_service(service_name, config)
    print(f"\\n🎉 All {len(SERVICES)} microservices created successfully!")
