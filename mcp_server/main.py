"""
FastMCP Server - Main Application
Port: 8012 (configurable via PORT env var)

Architecture:
- All routes organized in /routers/ directory
- Models in /models.py
- Middleware in /middleware.py
- Configuration in /config.py
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from clients.orchestrator_client import get_orchestrator_client
from middleware import RequestLoggingMiddleware, OrchestratorHealthMiddleware
from openapi_customization import customize_openapi_for_gpt
from routers import (
    health_router,
    tasks_router,
    workflows_router,
    tools_router,
    gpt_router,
)

# Initialize FastAPI app
app = FastAPI(
    title="AutoPro FastMCP Server",
    version="0.2.0",
    description="Python/FastAPI MCP Server with full orchestrator integration",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(OrchestratorHealthMiddleware)

# ==================== ROUTERS ====================

# Include all routers with proper organization
app.include_router(health_router)  # /health
app.include_router(tasks_router)  # /mcp/execute, /mcp/task/{task_id}/status
app.include_router(workflows_router)  # /mcp/workflows/*
app.include_router(tools_router)  # /mcp/tools/* (Linear, GitHub, Supabase, Testing, System)
app.include_router(gpt_router)  # /mcp/tools/gpt/* (ChatGPT Developer Mode)


# ==================== OPENAPI CUSTOMIZATION ====================


def custom_openapi():
    """Generate custom OpenAPI schema with GPT compatibility"""
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Customize for GPT
    openapi_schema = customize_openapi_for_gpt(openapi_schema)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ==================== STARTUP & MAIN ====================


@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    print("=" * 60)
    print("🚀 AutoPro FastMCP Server Starting")
    print("=" * 60)
    print(f"📦 Version: 0.2.0")
    print(f"🌐 Port: {get_settings().server_port}")
    print(f"📡 Orchestrator: {get_settings().orchestrator_url}")
    print("=" * 60)

    # Check orchestrator connection
    orchestrator = get_orchestrator_client()
    if orchestrator.ping():
        print("✅ Orchestrator connected")
    else:
        print("⚠️  Orchestrator not responding - some features may be unavailable")

    print("=" * 60)
    print("📋 Route Organization:")
    print("  - /health              → Health & Status")
    print("  - /mcp/execute         → Task Execution")
    print("  - /mcp/workflows/*     → Workflow Orchestration")
    print("  - /mcp/tools/linear/*  → Linear Integration")
    print("  - /mcp/tools/github/*  → GitHub Integration")
    print("  - /mcp/tools/supabase/* → Supabase Integration")
    print("  - /mcp/tools/test/*    → Testing Tools")
    print("  - /mcp/tools/system/*  → System Tools")
    print("  - /mcp/tools/gpt/*     → ChatGPT Developer Mode")
    print("=" * 60)


if __name__ == "__main__":
    import uvicorn

    # Get port from environment or default to 8012
    port = int(os.getenv("PORT", "8012"))
    host = os.getenv("HOST", "127.0.0.1")

    print(f"🚀 Starting AutoPro FastMCP Server on {host}:{port}")
    print(f"📋 API Docs: http://{host}:{port}/docs")
    print(f"📊 Health: http://{host}:{port}/health")

    uvicorn.run(app, host=host, port=port, log_level="info")
