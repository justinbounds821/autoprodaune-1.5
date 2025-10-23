"""Pydantic Models for MCP Server"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ==================== TASK MODELS ====================


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


# ==================== WORKFLOW MODELS ====================


class OrchestrateWorkflowRequest(BaseModel):
    command: str
    context: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None


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


# ==================== TESTING MODELS ====================


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


# ==================== GPT MODELS ====================


class GPTTestRequest(BaseModel):
    test_type: str
    config: Dict[str, Any]
