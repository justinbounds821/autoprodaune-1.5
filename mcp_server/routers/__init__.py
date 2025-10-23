"""FastAPI Routers for MCP Server"""

from .health import router as health_router
from .tasks import router as tasks_router
from .workflows import router as workflows_router
from .tools import router as tools_router
from .gpt import router as gpt_router

__all__ = [
    "health_router",
    "tasks_router",
    "workflows_router",
    "tools_router",
    "gpt_router",
]
