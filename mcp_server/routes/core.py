"""
Core MCP Routes
Task execution, task status, and core MCP functionality
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from config import repo_root
from clients.orchestrator_client import get_orchestrator_client

router = APIRouter(
    prefix="/mcp",
    tags=["Core MCP"],
    responses={404: {"description": "Not found"}},
)

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


# ==================== ROUTES ====================


@router.post("/execute", response_model=ExecuteResponse)
def mcp_execute(req: ExecuteRequest, background_tasks: BackgroundTasks) -> ExecuteResponse:
    """
    Execute a free-form MCP task
    
    This is a high-level endpoint that interprets natural language commands
    and executes them via the orchestrator in the background.
    
    Args:
        req: ExecuteRequest containing task description and optional context
        background_tasks: FastAPI background tasks handler
        
    Returns:
        ExecuteResponse with task_id for status tracking
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
    return ExecuteResponse(
        task_id=task_id,
        status="queued",
        message="Task accepted for processing",
    )


def _process_task(task_id: str) -> None:
    """
    Process task in background using orchestrator
    
    Args:
        task_id: Unique task identifier
    """
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


@router.get("/task/{task_id}/status", response_model=TaskStatusResponse)
def mcp_task_status(task_id: str) -> TaskStatusResponse:
    """
    Get task status and result
    
    Args:
        task_id: Unique task identifier
        
    Returns:
        TaskStatusResponse with current status and result (if completed)
        
    Raises:
        HTTPException: 404 if task not found
    """
    tasks = _load_tasks()
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatusResponse(
        task_id=task_id,
        status=task.get("status", "unknown"),
        result=task.get("result"),
    )


@router.get("/tasks")
def list_tasks(limit: int = 50, status: Optional[str] = None) -> Dict[str, Any]:
    """
    List all tasks with optional filtering
    
    Args:
        limit: Maximum number of tasks to return (default: 50)
        status: Filter by status (queued, running, completed, error)
        
    Returns:
        Dictionary with tasks list and metadata
    """
    tasks = _load_tasks()
    
    # Filter by status if provided
    if status:
        filtered_tasks = {
            tid: t for tid, t in tasks.items() 
            if t.get("status") == status
        }
    else:
        filtered_tasks = tasks
    
    # Apply limit
    task_items = list(filtered_tasks.items())[:limit]
    
    return {
        "tasks": [
            {
                "task_id": tid,
                "title": t.get("title"),
                "status": t.get("status"),
                "context": t.get("context"),
                "result": t.get("result"),
            }
            for tid, t in task_items
        ],
        "total": len(filtered_tasks),
        "limit": limit,
        "filter": {"status": status} if status else None,
    }


@router.delete("/task/{task_id}")
def delete_task(task_id: str) -> Dict[str, Any]:
    """
    Delete a task by ID
    
    Args:
        task_id: Unique task identifier
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if task not found
    """
    tasks = _load_tasks()
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del tasks[task_id]
    _save_tasks(tasks)
    
    return {
        "success": True,
        "message": f"Task {task_id} deleted",
    }


@router.post("/tasks/clear")
def clear_tasks(status: Optional[str] = None) -> Dict[str, Any]:
    """
    Clear tasks (optionally by status)
    
    Args:
        status: Only clear tasks with this status (optional)
        
    Returns:
        Number of tasks cleared
    """
    tasks = _load_tasks()
    
    if status:
        # Only clear tasks with specific status
        tasks_to_keep = {
            tid: t for tid, t in tasks.items() 
            if t.get("status") != status
        }
        cleared = len(tasks) - len(tasks_to_keep)
        _save_tasks(tasks_to_keep)
    else:
        # Clear all tasks
        cleared = len(tasks)
        _save_tasks({})
    
    return {
        "success": True,
        "cleared": cleared,
        "filter": {"status": status} if status else None,
    }
