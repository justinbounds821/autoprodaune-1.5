from fastapi import FastAPI
from autopro_common.telemetry import setup_observability
from autopro_common.logger import get_logger
from .health import router as health_router
from .routes import router as mcp_router
import uvicorn

app = FastAPI(title="MCP Dispatcher Service", version="1.0.0")
app.include_router(health_router)
app.include_router(mcp_router, prefix="/api/v1")

setup_observability(app)
logger = get_logger("mcp-service")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8010, reload=True)
