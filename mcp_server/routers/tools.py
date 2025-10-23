"""MCP Tools Routes (Linear, GitHub, Supabase, Testing, System)"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from clients.orchestrator_client import get_orchestrator_client
from models import (
    LinearTaskRequest,
    LinearUpdateRequest,
    GitHubIssueRequest,
    GitHubCommitRequest,
    SupabaseQueryRequest,
    SupabaseVerifyRequest,
    BrowserTestRequest,
    APITestRequest,
)

router = APIRouter(prefix="/mcp/tools", tags=["Tools"])


# ==================== LINEAR INTEGRATION ====================


@router.post("/linear/task")
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


@router.put("/linear/task")
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


@router.get("/linear/tasks")
def mcp_linear_list_tasks(limit: int = 50) -> Dict[str, Any]:
    """List Linear tasks via orchestrator"""
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.linear_list_tasks(limit=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== GITHUB INTEGRATION ====================


@router.post("/github/issue")
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


@router.post("/github/commit")
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


@router.post("/supabase/query")
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


@router.post("/supabase/verify")
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


@router.post("/test/browser")
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


@router.post("/test/api")
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


@router.get("/system/health")
def mcp_system_health(detailed: bool = False) -> Dict[str, Any]:
    """Check system health via orchestrator"""
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.system_health_check(detailed=detailed)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
