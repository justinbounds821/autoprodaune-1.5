from fastapi import FastAPI
from autopro_common.telemetry import setup_observability
from autopro_common.logger import get_logger
from .health import router as health_router
import uvicorn

app = FastAPI(title="Video Service", version="1.0.0")
app.include_router(health_router)

setup_observability(app)
logger = get_logger("video-service")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)
