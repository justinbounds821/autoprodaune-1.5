"""
FastMCP Server - Main Application
Port: 8012 (configurable via PORT env var)
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from config import get_settings, repo_root
from clients.orchestrator_client import get_orchestrator_client
from middleware import RequestLoggingMiddleware, OrchestratorHealthMiddleware
from openapi_customization import customize_openapi_for_gpt

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

# Data persistence
DATA_DIR = repo_root() / "mcp_server" / "data"
TASKS_FILE = DATA_DIR / "tasks.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)
if not TASKS_FILE.exists():
    TASKS_FILE.write_text(json.dumps({}), encoding="utf-8")


def _load_tasks() -> Dict[str, Any]:
    try:
        return json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_tasks(tasks: Dict[str, Any]) -> None:
    TASKS_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


# ==================== MODELS ====================


class ExecuteRequest(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = None


class ExecuteResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None


class OrchestrateWorkflowRequest(BaseModel):
    command: str
    context: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None


class LinearTaskRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 0
    labels: Optional[List[str]] = None
    epic_id: Optional[str] = None
    assignee: Optional[str] = None


class LinearUpdateRequest(BaseModel):
    task_id: str
    status: Optional[str] = None
    comment: Optional[str] = None


class GitHubIssueRequest(BaseModel):
    title: str
    body: str
    labels: Optional[List[str]] = None
    assignees: Optional[List[str]] = None
    linear_task_id: Optional[str] = None


class GitHubCommitRequest(BaseModel):
    message: str
    files: Optional[List[str]] = None
    linear_task_id: Optional[str] = None
    github_issue_number: Optional[int] = None


class SupabaseQueryRequest(BaseModel):
    table: str
    operation: str = Field(..., pattern="^(select|insert|update|delete)$")
    filters: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    limit: Optional[int] = None


class SupabaseVerifyRequest(BaseModel):
    table: str
    expected: Dict[str, Any]
    description: Optional[str] = None


class BrowserTestRequest(BaseModel):
    test_name: str
    url: str
    steps: List[Dict[str, Any]]
    verify_in_db: Optional[Dict[str, Any]] = None


class APITestRequest(BaseModel):
    method: str = Field(..., pattern="^(GET|POST|PUT|DELETE|PATCH)$")
    url: str
    body: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    expected_status: int = 200
    expected_response: Optional[Dict[str, Any]] = None


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


# ==================== HEALTH & STATUS ====================


@app.get("/health")
def health() -> Dict[str, Any]:
    """Health check endpoint"""
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


# ==================== TASK EXECUTION ====================


@app.post("/mcp/execute", response_model=ExecuteResponse)
def mcp_execute(req: ExecuteRequest, background_tasks: BackgroundTasks) -> ExecuteResponse:
    """
    Execute a free-form MCP task
    This is a high-level endpoint that interprets natural language commands
    """
    tasks = _load_tasks()
    task_id = f"task_{uuid4().hex[:8]}"
    tasks[task_id] = {
        "title": req.task,
        "context": req.context or {},
        "status": "queued",
    }
    _save_tasks(tasks)

    background_tasks.add_task(_process_task, task_id)
    return ExecuteResponse(task_id=task_id, status="queued", message="Task accepted for processing")


def _process_task(task_id: str) -> None:
    """Process task in background using orchestrator"""
    tasks = _load_tasks()
    task = tasks.get(task_id)
    if not task:
        return

    try:
        tasks[task_id]["status"] = "running"
        _save_tasks(tasks)

        # Use orchestrator to execute task
        orchestrator = get_orchestrator_client()
        result = orchestrator.orchestrate_workflow(
            command=task["title"],
            context=task.get("context", {}),
            options={"auto_execute": False},
        )

        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = result
    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = {"error": str(e)}
    finally:
        _save_tasks(tasks)


@app.get("/mcp/task/{task_id}/status", response_model=TaskStatusResponse)
def mcp_task_status(task_id: str) -> TaskStatusResponse:
    """Get task status and result"""
    tasks = _load_tasks()
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatusResponse(
        task_id=task_id,
        status=task.get("status", "unknown"),
        result=task.get("result"),
    )


# ==================== WORKFLOW ORCHESTRATION ====================


@app.post("/mcp/workflows/orchestrate")
def mcp_orchestrate_workflow(req: OrchestrateWorkflowRequest) -> Dict[str, Any]:
    """
    Orchestrate a complete workflow using the orchestrator
    This is the main entry point for complex multi-step operations
    """
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.orchestrate_workflow(
            command=req.command,
            context=req.context,
            options=req.options,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== LINEAR INTEGRATION ====================


@app.post("/mcp/tools/linear/task")
def mcp_linear_create_task(req: LinearTaskRequest) -> Dict[str, Any]:
    """Create Linear task via orchestrator"""
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.linear_create_task(
            title=req.title,
            description=req.description,
            priority=req.priority,
            labels=req.labels,
            epic_id=req.epic_id,
            assignee=req.assignee,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/mcp/tools/linear/task")
def mcp_linear_update_task(req: LinearUpdateRequest) -> Dict[str, Any]:
    """Update Linear task via orchestrator"""
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.linear_update_task(
            task_id=req.task_id,
            status=req.status,
            comment=req.comment,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcp/tools/linear/tasks")
def mcp_linear_list_tasks(limit: int = 50) -> Dict[str, Any]:
    """List Linear tasks via orchestrator"""
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.linear_list_tasks(limit=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== GITHUB INTEGRATION ====================


@app.post("/mcp/tools/github/issue")
def mcp_github_create_issue(req: GitHubIssueRequest) -> Dict[str, Any]:
    """Create GitHub issue via orchestrator"""
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.github_create_issue(
            title=req.title,
            body=req.body,
            labels=req.labels,
            assignees=req.assignees,
            linear_task_id=req.linear_task_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/tools/github/commit")
def mcp_github_commit(req: GitHubCommitRequest) -> Dict[str, Any]:
    """Create Git commit via orchestrator"""
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.github_commit(
            message=req.message,
            files=req.files,
            linear_task_id=req.linear_task_id,
            github_issue_number=req.github_issue_number,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SUPABASE INTEGRATION ====================


@app.post("/mcp/tools/supabase/query")
def mcp_supabase_query(req: SupabaseQueryRequest) -> Dict[str, Any]:
    """Execute Supabase query via orchestrator"""
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.supabase_query(
            table=req.table,
            operation=req.operation,
            filters=req.filters,
            data=req.data,
            limit=req.limit,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/tools/supabase/verify")
def mcp_supabase_verify(req: SupabaseVerifyRequest) -> Dict[str, Any]:
    """Verify database fix via orchestrator"""
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.supabase_verify_fix(
            table=req.table,
            expected=req.expected,
            description=req.description,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== TESTING ====================


@app.post("/mcp/tools/test/browser")
def mcp_browser_test(req: BrowserTestRequest) -> Dict[str, Any]:
    """Execute browser E2E test via orchestrator"""
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.browser_test(
            test_name=req.test_name,
            url=req.url,
            steps=req.steps,
            verify_in_db=req.verify_in_db,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/tools/test/api")
def mcp_api_test(req: APITestRequest) -> Dict[str, Any]:
    """Execute API test via orchestrator"""
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.api_test(
            method=req.method,
            url=req.url,
            body=req.body,
            headers=req.headers,
            expected_status=req.expected_status,
            expected_response=req.expected_response,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SYSTEM ====================


@app.get("/mcp/tools/system/health")
def mcp_system_health(detailed: bool = False) -> Dict[str, Any]:
    """Check system health via orchestrator"""
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.system_health_check(detailed=detailed)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== GPT DEVELOPER MODE ENDPOINTS ====================


@app.post("/mcp/tools/gpt/orchestrate")
def gpt_orchestrate(req: OrchestrateWorkflowRequest) -> Dict[str, Any]:
    """
    GPT Developer Mode: Orchestrate workflow
    Special endpoint for GPT integration with enhanced response formatting
    """
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.orchestrate_workflow(
            command=req.command,
            context=req.context,
            options=req.options,
        )

        # Format response for GPT
        if result.get("ok"):
            formatted = {
                "success": True,
                "workflow_id": result.get("workflow_id"),
                "summary": result.get("summary"),
                "tasks": result.get("tasks", []),
                "agent_prompts": result.get("agent_prompts", []),
                "next_steps": "Execute agent prompts and report back",
            }
            return formatted
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/tools/gpt/create_task")
def gpt_create_task(req: LinearTaskRequest) -> Dict[str, Any]:
    """GPT Developer Mode: Create Linear task with GPT-friendly response"""
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.linear_create_task(
            title=req.title,
            description=req.description,
            priority=req.priority,
            labels=req.labels,
            epic_id=req.epic_id,
            assignee=req.assignee,
        )

        if result.get("ok"):
            return {
                "success": True,
                "task_id": result.get("task_id"),
                "url": result.get("url"),
                "message": f"Task created: {req.title}",
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/tools/gpt/test")
def gpt_run_test(test_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    GPT Developer Mode: Run test (browser or API)
    Unified endpoint for all test types
    """
    try:
        orchestrator = get_orchestrator_client()

        if test_type == "browser":
            result = orchestrator.browser_test(**config)
        elif test_type == "api":
            result = orchestrator.api_test(**config)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown test type: {test_type}")

        if result.get("ok"):
            return {
                "success": True,
                "test_type": test_type,
                "results": result.get("results") or result.get("data"),
                "message": result.get("message", "Test completed"),
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcp/tools/gpt/status")
def gpt_system_status() -> Dict[str, Any]:
    """
    GPT Developer Mode: Get comprehensive system status
    Includes orchestrator, backend, database, etc.
    """
    try:
        orchestrator = get_orchestrator_client()
        health = orchestrator.system_health_check(detailed=True)

        if health.get("ok"):
            return {
                "success": True,
                "overall_status": health.get("overall_status"),
                "services": health.get("services", {}),
                "timestamp": health.get("timestamp"),
            }
        else:
            return {
                "success": False,
                "error": health.get("error"),
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# ==================== STARTUP & MAIN ====================


@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    print("=" * 60)
    print("🚀 AutoPro FastMCP Server Starting")
    print("=" * 60)
    print(f"📦 Version: 0.2.0")
    print(f"🌐 Port: {get_settings().server_port}")
    print(f"📡 Orchestrator: {get_settings().orchestrator_index_path}")
    print("=" * 60)

    # Check orchestrator connection
    orchestrator = get_orchestrator_client()
    if orchestrator.ping():
        print("✅ Orchestrator connected")
    else:
        print("⚠️  Orchestrator not responding - some features may be unavailable")

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
