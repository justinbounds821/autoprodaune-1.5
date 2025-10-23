"""
Integration Routes
Linear, GitHub, and Supabase integrations via orchestrator
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from clients.orchestrator_client import get_orchestrator_client

router = APIRouter(
    prefix="/mcp/tools",
    tags=["Integrations"],
    responses={404: {"description": "Not found"}},
)


# ==================== LINEAR MODELS ====================


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


# ==================== GITHUB MODELS ====================


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


# ==================== SUPABASE MODELS ====================


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


# ==================== LINEAR ROUTES ====================


@router.post("/linear/task")
def linear_create_task(req: LinearTaskRequest) -> Dict[str, Any]:
    """
    Create Linear task via orchestrator
    
    Args:
        req: LinearTaskRequest with task details
        
    Returns:
        Created task information with ID and URL
        
    Example:
        ```json
        {
            "title": "Fix login bug",
            "description": "Users cannot login with email",
            "priority": 1,
            "labels": ["bug", "authentication"],
            "assignee": "user@example.com"
        }
        ```
    """
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


@router.put("/linear/task")
def linear_update_task(req: LinearUpdateRequest) -> Dict[str, Any]:
    """
    Update Linear task via orchestrator
    
    Args:
        req: LinearUpdateRequest with task ID and updates
        
    Returns:
        Updated task information
    """
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


@router.get("/linear/tasks")
def linear_list_tasks(limit: int = 50) -> Dict[str, Any]:
    """
    List Linear tasks via orchestrator
    
    Args:
        limit: Maximum number of tasks to return (default: 50)
        
    Returns:
        List of Linear tasks
    """
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.linear_list_tasks(limit=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/linear/task/{task_id}")
def linear_get_task(task_id: str) -> Dict[str, Any]:
    """
    Get Linear task details
    
    Args:
        task_id: Linear task identifier
        
    Returns:
        Task details
    """
    try:
        orchestrator = get_orchestrator_client()
        # This would require the orchestrator to implement task retrieval
        return {
            "task_id": task_id,
            "message": "Task retrieval not yet implemented in orchestrator",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== GITHUB ROUTES ====================


@router.post("/github/issue")
def github_create_issue(req: GitHubIssueRequest) -> Dict[str, Any]:
    """
    Create GitHub issue via orchestrator
    
    Args:
        req: GitHubIssueRequest with issue details
        
    Returns:
        Created issue information with number and URL
        
    Example:
        ```json
        {
            "title": "Login bug fix",
            "body": "Fixes authentication issue",
            "labels": ["bug"],
            "assignees": ["username"],
            "linear_task_id": "TASK-123"
        }
        ```
    """
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


@router.post("/github/commit")
def github_commit(req: GitHubCommitRequest) -> Dict[str, Any]:
    """
    Create Git commit via orchestrator
    
    Args:
        req: GitHubCommitRequest with commit details
        
    Returns:
        Commit information with hash and status
    """
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


@router.get("/github/status")
def github_status() -> Dict[str, Any]:
    """
    Get GitHub integration status
    
    Returns:
        GitHub integration status and configuration
    """
    try:
        orchestrator = get_orchestrator_client()
        # Check if GitHub integration is available
        health = orchestrator.system_health_check(detailed=False)
        
        return {
            "integration": "github",
            "status": "available" if health.get("ok") else "unavailable",
            "capabilities": {
                "create_issue": True,
                "create_commit": True,
                "link_linear": True,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SUPABASE ROUTES ====================


@router.post("/supabase/query")
def supabase_query(req: SupabaseQueryRequest) -> Dict[str, Any]:
    """
    Execute Supabase query via orchestrator
    
    Args:
        req: SupabaseQueryRequest with query details
        
    Returns:
        Query results
        
    Example:
        ```json
        {
            "table": "leads",
            "operation": "select",
            "filters": {"status": "new"},
            "limit": 10
        }
        ```
    """
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


@router.post("/supabase/verify")
def supabase_verify(req: SupabaseVerifyRequest) -> Dict[str, Any]:
    """
    Verify database fix via orchestrator
    
    Args:
        req: SupabaseVerifyRequest with verification details
        
    Returns:
        Verification result with success status
    """
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


@router.get("/supabase/tables")
def supabase_list_tables() -> Dict[str, Any]:
    """
    List available Supabase tables
    
    Returns:
        List of database tables
    """
    try:
        # This would query the database schema
        return {
            "tables": [
                "leads",
                "referrals",
                "financial_data",
                "social_posts",
                "automation_logs",
                "video_queue",
            ],
            "message": "Table listing is a placeholder - implement schema query",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supabase/status")
def supabase_status() -> Dict[str, Any]:
    """
    Get Supabase integration status
    
    Returns:
        Supabase integration status and configuration
    """
    try:
        orchestrator = get_orchestrator_client()
        health = orchestrator.system_health_check(detailed=False)
        
        return {
            "integration": "supabase",
            "status": "available" if health.get("ok") else "unavailable",
            "capabilities": {
                "query": True,
                "verify": True,
                "operations": ["select", "insert", "update", "delete"],
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
