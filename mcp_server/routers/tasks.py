"""Task Execution Routes"""

import json
from typing import Any, Dict
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException

from config import repo_root
from clients.orchestrator_client import get_orchestrator_client
from models import ExecuteRequest, ExecuteResponse, TaskStatusResponse

router = APIRouter(prefix="/mcp", tags=["Tasks"])

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


@router.post("/execute", response_model=ExecuteResponse)
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


@router.get("/task/{task_id}/status", response_model=TaskStatusResponse)
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
