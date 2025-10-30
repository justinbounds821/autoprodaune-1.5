from fastapi import FastAPI
from autopro_common.telemetry import setup_observability
from autopro_common.logger import get_logger
from autopro_common.db import init_db
from .health import router as health_router
from .routes import router as leads_router
import uvicorn

app = FastAPI(title="Lead Service", version="1.0.0")
app.include_router(health_router)
app.include_router(leads_router, prefix="/api/v1")

setup_observability(app)
logger = get_logger("lead-service")

@app.on_event("startup")
async def startup():
    await init_db()
    logger.info("Lead service started")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
