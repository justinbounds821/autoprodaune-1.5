"""
GPT Developer Mode Routes
ChatGPT-optimized endpoints with enhanced response formatting
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from clients.orchestrator_client import get_orchestrator_client

router = APIRouter(
    prefix="/mcp/tools/gpt",
    tags=["GPT Developer Mode"],
    responses={404: {"description": "Not found"}},
)


# ==================== MODELS ====================


class GPTOrchestrateRequest(BaseModel):
    command: str
    context: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None


class GPTTaskRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 0
    labels: Optional[List[str]] = None
    epic_id: Optional[str] = None
    assignee: Optional[str] = None


class GPTTestRequest(BaseModel):
    test_type: str
    config: Dict[str, Any]


# ==================== WORKFLOW ORCHESTRATION ====================


@router.post("/orchestrate")
def gpt_orchestrate(req: GPTOrchestrateRequest) -> Dict[str, Any]:
    """
    GPT Developer Mode: Orchestrate workflow
    
    Special endpoint for GPT integration with enhanced response formatting.
    Returns workflow execution plan with clear next steps for GPT to follow.
    
    Args:
        req: GPTOrchestrateRequest with command, context, and options
        
    Returns:
        GPT-formatted response with workflow summary and action items
        
    Example Response:
        ```json
        {
            "success": true,
            "workflow_id": "wf_abc123",
            "summary": "Created Linear task and GitHub issue",
            "tasks": [
                {"type": "linear_task", "status": "completed", "result": {...}},
                {"type": "github_issue", "status": "completed", "result": {...}}
            ],
            "agent_prompts": [
                "Task created in Linear: TASK-123",
                "Issue created in GitHub: #456"
            ],
            "next_steps": "Execute agent prompts and report back"
        }
        ```
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


@router.post("/orchestrate/stream")
def gpt_orchestrate_stream(req: GPTOrchestrateRequest) -> Dict[str, Any]:
    """
    GPT Developer Mode: Orchestrate workflow with streaming updates
    
    Similar to /orchestrate but with support for real-time progress updates.
    Useful for long-running workflows where GPT needs intermediate feedback.
    
    Args:
        req: GPTOrchestrateRequest with command, context, and options
        
    Returns:
        GPT-formatted streaming response
        
    Note:
        Current implementation returns full result (streaming not yet implemented)
    """
    # For now, just call the regular orchestrate endpoint
    # In future, implement SSE (Server-Sent Events) for real streaming
    return gpt_orchestrate(req)


# ==================== TASK MANAGEMENT ====================


@router.post("/create_task")
def gpt_create_task(req: GPTTaskRequest) -> Dict[str, Any]:
    """
    GPT Developer Mode: Create Linear task with GPT-friendly response
    
    Creates a Linear task and returns a simplified, GPT-optimized response
    with clear success indicators and actionable next steps.
    
    Args:
        req: GPTTaskRequest with task details
        
    Returns:
        GPT-formatted task creation response
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


@router.get("/tasks")
def gpt_list_tasks(limit: int = 10, status: Optional[str] = None) -> Dict[str, Any]:
    """
    GPT Developer Mode: List tasks with GPT-friendly formatting
    
    Args:
        limit: Maximum number of tasks (default: 10)
        status: Filter by status (optional)
        
    Returns:
        Simplified task list for GPT consumption
    """
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.linear_list_tasks(limit=limit)

        if result.get("ok"):
            tasks = result.get("tasks", [])
            return {
                "success": True,
                "total": len(tasks),
                "tasks": [
                    {
                        "id": t.get("id"),
                        "title": t.get("title"),
                        "status": t.get("status"),
                        "priority": t.get("priority"),
                    }
                    for t in tasks
                ],
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== TESTING ====================


@router.post("/test")
def gpt_run_test(req: GPTTestRequest) -> Dict[str, Any]:
    """
    GPT Developer Mode: Run test (browser or API)
    
    Unified endpoint for all test types with GPT-optimized responses.
    Automatically determines test type and executes appropriately.
    
    Args:
        req: GPTTestRequest with test type and configuration
        
    Returns:
        GPT-formatted test results
        
    Example:
        ```json
        {
            "test_type": "api",
            "config": {
                "method": "GET",
                "url": "https://api.example.com/health",
                "expected_status": 200
            }
        }
        ```
    """
    try:
        orchestrator = get_orchestrator_client()

        if req.test_type == "browser":
            result = orchestrator.browser_test(**req.config)
        elif req.test_type == "api":
            result = orchestrator.api_test(**req.config)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown test type: {req.test_type}",
            )

        if result.get("ok"):
            return {
                "success": True,
                "test_type": req.test_type,
                "results": result.get("results") or result.get("data"),
                "message": result.get("message", "Test completed"),
            }
        else:
            return {
                "success": False,
                "test_type": req.test_type,
                "error": result.get("error", "Test failed"),
            }
    except Exception as e:
        return {
            "success": False,
            "test_type": req.test_type,
            "error": str(e),
        }


# ==================== SYSTEM STATUS ====================


@router.get("/status")
def gpt_system_status() -> Dict[str, Any]:
    """
    GPT Developer Mode: Get comprehensive system status
    
    Returns simplified system status optimized for GPT interpretation.
    Includes orchestrator, backend, database, and service availability.
    
    Returns:
        GPT-formatted system status with clear indicators
    """
    try:
        orchestrator = get_orchestrator_client()
        health = orchestrator.system_health_check(detailed=True)

        if health.get("ok"):
            return {
                "success": True,
                "overall_status": health.get("overall_status", "unknown"),
                "services": health.get("services", {}),
                "timestamp": health.get("timestamp"),
                "message": "All systems operational",
            }
        else:
            return {
                "success": False,
                "overall_status": "degraded",
                "error": health.get("error"),
                "message": "System health check failed",
            }
    except Exception as e:
        return {
            "success": False,
            "overall_status": "error",
            "error": str(e),
            "message": "Could not retrieve system status",
        }


@router.get("/capabilities")
def gpt_capabilities() -> Dict[str, Any]:
    """
    GPT Developer Mode: List available capabilities
    
    Returns a complete list of what GPT can do with this MCP server.
    Useful for GPT to understand available actions.
    
    Returns:
        List of capabilities with descriptions and examples
    """
    return {
        "capabilities": [
            {
                "name": "orchestrate_workflow",
                "description": "Execute complex multi-step workflows",
                "example": "Create Linear task and GitHub issue for bug fix",
            },
            {
                "name": "create_task",
                "description": "Create Linear task with automatic linking",
                "example": "Create high-priority task for authentication bug",
            },
            {
                "name": "run_test",
                "description": "Execute browser or API tests",
                "example": "Test login flow end-to-end",
            },
            {
                "name": "check_status",
                "description": "Check system and service health",
                "example": "Verify all systems are operational",
            },
            {
                "name": "query_database",
                "description": "Query and verify database state",
                "example": "Check if user exists in database",
            },
        ],
        "integrations": ["Linear", "GitHub", "Supabase", "Browser Testing", "API Testing"],
        "gpt_optimized": True,
        "version": "0.2.0",
    }


# ==================== HELP & DOCUMENTATION ====================


@router.get("/help")
def gpt_help(topic: Optional[str] = None) -> Dict[str, Any]:
    """
    GPT Developer Mode: Get help and usage examples
    
    Args:
        topic: Specific topic to get help for (optional)
        
    Returns:
        Help documentation and usage examples
    """
    if topic == "workflows":
        return {
            "topic": "workflows",
            "description": "How to orchestrate complex workflows",
            "examples": [
                {
                    "scenario": "Bug fix workflow",
                    "command": "Create Linear task and GitHub issue for login bug",
                    "context": {"bug_description": "Users cannot login", "priority": "high"},
                },
                {
                    "scenario": "Feature development",
                    "command": "Plan and implement user profile feature",
                    "context": {"feature_description": "User profile page", "priority": "medium"},
                },
            ],
        }
    elif topic == "testing":
        return {
            "topic": "testing",
            "description": "How to run browser and API tests",
            "examples": [
                {
                    "test_type": "browser",
                    "scenario": "Login flow test",
                    "config": {
                        "test_name": "Login Test",
                        "url": "https://app.example.com/login",
                        "steps": [
                            {"action": "fill", "selector": "#email", "value": "test@example.com"},
                            {"action": "click", "selector": "button[type='submit']"},
                        ],
                    },
                },
                {
                    "test_type": "api",
                    "scenario": "Health check test",
                    "config": {
                        "method": "GET",
                        "url": "https://api.example.com/health",
                        "expected_status": 200,
                    },
                },
            ],
        }
    else:
        return {
            "topics": ["workflows", "testing", "tasks", "database"],
            "description": "MCP Server help documentation",
            "usage": "Use ?topic=<topic_name> to get specific help",
            "examples": [
                "/mcp/tools/gpt/help?topic=workflows",
                "/mcp/tools/gpt/help?topic=testing",
            ],
        }


@router.get("/examples")
def gpt_examples() -> Dict[str, Any]:
    """
    GPT Developer Mode: Get complete usage examples
    
    Returns comprehensive examples of all GPT endpoints and use cases.
    
    Returns:
        Collection of real-world usage examples
    """
    return {
        "examples": [
            {
                "category": "Workflow Orchestration",
                "examples": [
                    {
                        "name": "Bug Fix Workflow",
                        "endpoint": "/mcp/tools/gpt/orchestrate",
                        "request": {
                            "command": "Create Linear task and GitHub issue for login bug",
                            "context": {"bug_description": "Users cannot login", "priority": "high"},
                        },
                    },
                ],
            },
            {
                "category": "Task Management",
                "examples": [
                    {
                        "name": "Create Task",
                        "endpoint": "/mcp/tools/gpt/create_task",
                        "request": {
                            "title": "Fix authentication bug",
                            "description": "Users cannot login with email",
                            "priority": 1,
                            "labels": ["bug", "authentication"],
                        },
                    },
                ],
            },
            {
                "category": "Testing",
                "examples": [
                    {
                        "name": "API Test",
                        "endpoint": "/mcp/tools/gpt/test",
                        "request": {
                            "test_type": "api",
                            "config": {
                                "method": "GET",
                                "url": "https://api.example.com/health",
                                "expected_status": 200,
                            },
                        },
                    },
                ],
            },
        ],
        "message": "Use these examples as templates for GPT interactions",
    }
