"""
System Routes
Health checks, status monitoring, and system information endpoints
"""
from typing import Any, Dict

from fastapi import APIRouter

from config import get_settings
from clients.orchestrator_client import get_orchestrator_client

router = APIRouter(
    prefix="/system",
    tags=["System"],
    responses={404: {"description": "Not found"}},
)


@router.get("/health")
def system_health() -> Dict[str, Any]:
    """
    System health check endpoint
    Returns: Service status, version, environment, and orchestrator connectivity
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
    }


@router.get("/status")
def system_status() -> Dict[str, Any]:
    """
    Detailed system status
    Returns: Extended system information and component status
    """
    settings = get_settings()
    orchestrator = get_orchestrator_client()

    return {
        "service": "AutoPro FastMCP Server",
        "version": "0.2.0",
        "environment": settings.environment,
        "components": {
            "mcp_server": {"status": "running", "port": settings.server_port},
            "orchestrator": {
                "status": "connected" if orchestrator.ping() else "disconnected",
                "url": settings.orchestrator_url,
            },
        },
        "capabilities": {
            "workflows": True,
            "linear_integration": True,
            "github_integration": True,
            "supabase_integration": True,
            "browser_testing": True,
            "api_testing": True,
            "gpt_developer_mode": True,
        },
    }


@router.get("/tools")
def list_tools() -> Dict[str, Any]:
    """
    List all available MCP tools
    Returns: Complete list of tools with descriptions
    """
    return {
        "tools": [
            {
                "name": "orchestrate_workflow",
                "description": "Orchestrate complex multi-step workflows",
                "category": "workflow",
            },
            {
                "name": "linear_create_task",
                "description": "Create Linear task with details",
                "category": "integration",
            },
            {
                "name": "linear_update_task",
                "description": "Update Linear task status and add comments",
                "category": "integration",
            },
            {
                "name": "linear_list_tasks",
                "description": "List Linear tasks with filtering",
                "category": "integration",
            },
            {
                "name": "github_create_issue",
                "description": "Create GitHub issue linked to Linear task",
                "category": "integration",
            },
            {
                "name": "github_commit",
                "description": "Create Git commit linked to Linear/GitHub",
                "category": "integration",
            },
            {
                "name": "supabase_query",
                "description": "Execute Supabase database queries",
                "category": "integration",
            },
            {
                "name": "supabase_verify",
                "description": "Verify database state after operations",
                "category": "integration",
            },
            {
                "name": "browser_test",
                "description": "Execute browser E2E tests with verification",
                "category": "testing",
            },
            {
                "name": "api_test",
                "description": "Execute API tests with validation",
                "category": "testing",
            },
            {
                "name": "system_health_check",
                "description": "Check system health and service status",
                "category": "system",
            },
        ],
        "total": 11,
        "categories": ["workflow", "integration", "testing", "system"],
    }


@router.get("/info")
def system_info() -> Dict[str, Any]:
    """
    System information and configuration
    Returns: System configuration and runtime information
    """
    settings = get_settings()

    return {
        "name": "AutoPro FastMCP Server",
        "version": "0.2.0",
        "description": "Python/FastAPI MCP Server with full orchestrator integration",
        "server": {
            "host": settings.server_host,
            "port": settings.server_port,
        },
        "orchestrator": {
            "url": settings.orchestrator_url,
            "enabled": True,
        },
        "environment": settings.environment,
        "features": {
            "workflow_orchestration": True,
            "linear_integration": True,
            "github_integration": True,
            "supabase_integration": True,
            "browser_testing": True,
            "api_testing": True,
            "gpt_developer_mode": True,
            "oauth_authentication": False,  # To be implemented
            "webhook_support": False,  # To be implemented
        },
    }
