from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import get_settings, repo_root
from .tools.github_tool import commit_changes
from .tools.supabase_tool import run_supabase_action, log_task_event
from .tools.discord_tool import send_discord_message
from .tools.filesystem_tool import fs_read_file, fs_write_file


app = FastAPI(title="AutoPro FastMCP Server", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# Models
class ExecuteRequest(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = None


class ExecuteResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None


class GitFile(BaseModel):
    path: str
    content: str


class GitCommitRequest(BaseModel):
    repo_dir: Optional[str] = None
    commit_message: str = Field(..., min_length=3)
    files: List[GitFile] = Field(default_factory=list)


class SupabaseQueryRequest(BaseModel):
    table: str
    action: str = Field(..., pattern="^(select|insert|update|delete)$")
    filters: Optional[Dict[str, Any]] = None
    values: Optional[Dict[str, Any]] = None
    select: Optional[str] = "*"


class DiscordNotifyRequest(BaseModel):
    message: str
    webhook_url: Optional[str] = None
    title: Optional[str] = None
    level: Optional[str] = Field(default="info", pattern="^(info|success|warning|error)$")


class FSWriteRequest(BaseModel):
    path: str
    content: str


class FSReadRequest(BaseModel):
    path: str


@app.get("/health")
def health() -> Dict[str, Any]:
    settings = get_settings()
    return {
        "status": "ok",
        "environment": settings.environment,
        "port": settings.server_port,
    }


@app.post("/mcp/execute", response_model=ExecuteResponse)
def mcp_execute(req: ExecuteRequest, background_tasks: BackgroundTasks) -> ExecuteResponse:
    tasks = _load_tasks()
    task_id = f"task_{uuid4().hex[:8]}"
    tasks[task_id] = {
        "title": req.task,
        "context": req.context or {},
        "status": "queued",
    }
    _save_tasks(tasks)

    # Log to Supabase (best-effort)
    settings = get_settings()
    try:
        log_task_event(
            base_url=settings.supabase_url,
            api_key=settings.supabase_service_key or settings.supabase_key,
            event={"task_id": task_id, "title": req.task, "status": "queued", "result": None},
        )
    except Exception:
        pass

    background_tasks.add_task(_process_task, task_id)
    return ExecuteResponse(task_id=task_id, status="queued", message="Task accepted")


def _process_task(task_id: str) -> None:
    tasks = _load_tasks()
    task = tasks.get(task_id)
    if not task:
        return
    try:
        tasks[task_id]["status"] = "running"
        _save_tasks(tasks)
        # Log running
        settings = get_settings()
        try:
            log_task_event(
                base_url=settings.supabase_url,
                api_key=settings.supabase_service_key or settings.supabase_key,
                event={"task_id": task_id, "title": task.get("title"), "status": "running", "result": None},
            )
        except Exception:
            pass
        # Stub: echo result; integrate analyzer/coder/tester agents later
        result = {"summary": f"Executed task: {task['title']}", "success": True}
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = result
        try:
            log_task_event(
                base_url=settings.supabase_url,
                api_key=settings.supabase_service_key or settings.supabase_key,
                event={"task_id": task_id, "title": task.get("title"), "status": "completed", "result": result},
            )
        except Exception:
            pass
    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = {"error": str(e)}
        try:
            log_task_event(
                base_url=settings.supabase_url,
                api_key=settings.supabase_service_key or settings.supabase_key,
                event={"task_id": task_id, "title": task.get("title"), "status": "error", "result": {"error": str(e)}},
            )
        except Exception:
            pass
    finally:
        _save_tasks(tasks)


@app.post("/mcp/task/create", response_model=ExecuteResponse)
def mcp_task_create(req: TaskCreateRequest) -> ExecuteResponse:
    tasks = _load_tasks()
    task_id = f"task_{uuid4().hex[:8]}"
    tasks[task_id] = {
        "title": req.title,
        "description": req.description,
        "metadata": req.metadata or {},
        "status": "created",
    }
    _save_tasks(tasks)
    return ExecuteResponse(task_id=task_id, status="created", message="Task created")


@app.get("/mcp/task/{task_id}/status", response_model=TaskStatusResponse)
def mcp_task_status(task_id: str) -> TaskStatusResponse:
    tasks = _load_tasks()
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatusResponse(task_id=task_id, status=task.get("status", "unknown"), result=task.get("result"))


@app.post("/mcp/tools/github/commit")
def mcp_github_commit(req: GitCommitRequest) -> Dict[str, Any]:
    repo_dir = Path(req.repo_dir) if req.repo_dir else repo_root()
    return commit_changes(repo_dir=repo_dir, files=[f.model_dump() for f in req.files], message=req.commit_message)


@app.post("/mcp/tools/supabase/query")
def mcp_supabase_query(req: SupabaseQueryRequest) -> Dict[str, Any]:
    settings = get_settings()
    result = run_supabase_action(
        base_url=settings.supabase_url,
        api_key=settings.supabase_key or settings.supabase_service_key,
        table=req.table,
        action=req.action,
        filters=req.filters or {},
        values=req.values or {},
        select=req.select or "*",
    )
    return {"ok": True, "data": result}


@app.post("/mcp/tools/discord/notify")
def mcp_discord_notify(req: DiscordNotifyRequest) -> Dict[str, Any]:
    settings = get_settings()
    url = req.webhook_url or settings.discord_webhook_url
    if not url:
        raise HTTPException(status_code=400, detail="Missing Discord webhook URL")
    res = send_discord_message(url=url, message=req.message, title=req.title, level=req.level)
    return {"ok": res}


@app.post("/mcp/tools/fs/write")
def mcp_fs_write(req: FSWriteRequest) -> Dict[str, Any]:
    path = Path(req.path)
    return {"ok": True, "written": fs_write_file(path, req.content)}


@app.post("/mcp/tools/fs/read")
def mcp_fs_read(req: FSReadRequest) -> Dict[str, Any]:
    path = Path(req.path)
    return {"ok": True, "content": fs_read_file(path)}


# Optional: helpers for calling Node orchestrator (placeholder)
def call_orchestrator_tool(tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    # Placeholder showing where integration would occur
    # e.g., subprocess.run([settings.orchestrator_node_path, settings.orchestrator_index_path, ...])
    return {"ok": False, "message": "orchestrator bridge not implemented"}
