"""
MCP Server Routes Package
Organized route structure for AutoPro FastMCP Server
"""
from .system import router as system_router
from .core import router as core_router
from .workflows import router as workflows_router
from .integrations import router as integrations_router
from .testing import router as testing_router
from .gpt import router as gpt_router

__all__ = [
    "system_router",
    "core_router",
    "workflows_router",
    "integrations_router",
    "testing_router",
    "gpt_router",
]
