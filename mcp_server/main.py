"""
FastMCP Server - Main Application
Port: 8012 (configurable via PORT env var)

Organized route structure with logical categorization:
- System Routes: Health, status, monitoring, tools list
- Core MCP Routes: Task execution, task management
- Workflow Routes: Orchestration, templates, workflow management
- Integration Routes: Linear, GitHub, Supabase
- Testing Routes: Browser tests, API tests, test suites
- GPT Routes: ChatGPT developer mode optimized endpoints
"""

from __future__ import annotations

import os
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings, repo_root
from clients.orchestrator_client import get_orchestrator_client
from middleware import RequestLoggingMiddleware, OrchestratorHealthMiddleware
from openapi_customization import customize_openapi_for_gpt

# Import route modules
from routes import (
    system_router,
    core_router,
    workflows_router,
    integrations_router,
    testing_router,
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


# ==================== ROOT & LEGACY HEALTH ====================


@app.get("/")
def root() -> Dict[str, Any]:
    """Root endpoint - API information"""
    return {
        "service": "AutoPro FastMCP Server",
        "version": "0.2.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "routes": {
            "system": "/system/*",
            "core_mcp": "/mcp/*",
            "workflows": "/mcp/workflows/*",
            "integrations": "/mcp/tools/{linear,github,supabase}/*",
            "testing": "/mcp/tools/test/*",
            "gpt": "/mcp/tools/gpt/*",
        },
    }


@app.get("/health")
def health_legacy() -> Dict[str, Any]:
    """
    Legacy health check endpoint (for backwards compatibility)
    Use /system/health for the new standard endpoint
    """
    settings = get_settings()
    orchestrator = get_orchestrator_client()

    return {
        "status": "ok",
        "service": "mcp_server",
        "environment": settings.environment,
        "port": settings.server_port,
        "orchestrator_connected": orchestrator.ping(),
        "version": "0.2.0",
        "message": "Use /system/health for the new standard health endpoint",
    }


@app.get("/favicon.ico")
def favicon():
    """Favicon endpoint to prevent 404 errors in browsers"""
    return JSONResponse(content={}, status_code=204)


# ==================== ERROR HANDLERS ====================


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    import logging
    import traceback

    log = logging.getLogger("uvicorn.error")
    log.error(f"Unhandled exception on {request.url.path}: {exc}")
    log.error(traceback.format_exc())

    return JSONResponse(
        status_code=500,
        content={
            "ok": False,
            "error": "internal_error",
            "message": str(exc),
            "path": str(request.url.path),
        },
    )


# ==================== EVENT LOGGING ====================


@app.post("/events/error")
async def log_error_event(request: Request):
    """Log error events from clients"""
    import logging

    log = logging.getLogger("uvicorn.error")

    try:
        body = await request.json()
        log.error(f"Client error event: {body}")
        return {"ok": True, "message": "Error logged"}
    except Exception as e:
        log.error(f"Failed to log error event: {e}")
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": "invalid_request"},
        )


# ==================== INCLUDE ROUTERS ====================

# System routes: /system/*
app.include_router(system_router)

# Core MCP routes: /mcp/*
app.include_router(core_router)

# Workflow routes: /mcp/workflows/*
app.include_router(workflows_router)

# Integration routes: /mcp/tools/{linear,github,supabase}/*
app.include_router(integrations_router)

# Testing routes: /mcp/tools/test/*
app.include_router(testing_router)

# GPT routes: /mcp/tools/gpt/*
app.include_router(gpt_router)


# ==================== STARTUP & SHUTDOWN ====================


@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    import logging

    log = logging.getLogger("uvicorn.error")

    print("=" * 80)
    print("🚀 AutoPro FastMCP Server Starting")
    print("=" * 80)
    print(f"📦 Version: 0.2.0")
    print(f"🌐 Port: {get_settings().server_port}")
    print(f"📡 Orchestrator: {get_settings().orchestrator_url}")
    print("=" * 80)

    # Check orchestrator connection
    orchestrator = get_orchestrator_client()
    if orchestrator.ping():
        print("✅ Orchestrator connected")
    else:
        print("⚠️  Orchestrator not responding - some features may be unavailable")

    print("=" * 80)
    print("📋 Route Structure:")
    print("  • System Routes:      /system/*")
    print("  • Core MCP Routes:    /mcp/*")
    print("  • Workflow Routes:    /mcp/workflows/*")
    print("  • Integration Routes: /mcp/tools/{linear,github,supabase}/*")
    print("  • Testing Routes:     /mcp/tools/test/*")
    print("  • GPT Routes:         /mcp/tools/gpt/*")
    print("=" * 80)

    # Log all registered routes
    log.info("=" * 80)
    log.info("🚀 AutoPro FastMCP Server Started")
    log.info("=" * 80)
    routes = []
    for route in app.routes:
        methods = ",".join(sorted(getattr(route, "methods", []))) or "GET"
        routes.append(f"{methods:10s} {route.path}")
    log.info(f"📋 Registered {len(routes)} routes:\n" + "\n".join(routes))
    log.info("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown tasks"""
    import logging

    log = logging.getLogger("uvicorn.error")
    log.info("🛑 AutoPro FastMCP Server shutting down")


# ==================== MAIN ====================


if __name__ == "__main__":
    import uvicorn

    # Get port from environment or default to 8012
    port = int(os.getenv("PORT", "8012"))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"🚀 Starting AutoPro FastMCP Server on {host}:{port}")
    print(f"📋 API Docs: http://{host}:{port}/docs")
    print(f"📊 Health: http://{host}:{port}/health")
    print(f"📊 System Health: http://{host}:{port}/system/health")
    print(f"🔧 Tools List: http://{host}:{port}/system/tools")

    uvicorn.run(app, host=host, port=port, log_level="info")
