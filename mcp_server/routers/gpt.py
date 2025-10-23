"""GPT Developer Mode Routes"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from clients.orchestrator_client import get_orchestrator_client
from models import OrchestrateWorkflowRequest, LinearTaskRequest, GPTTestRequest

router = APIRouter(prefix="/mcp/tools/gpt", tags=["GPT Developer Mode"])


@router.post("/orchestrate")
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


@router.post("/create_task")
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


@router.post("/test")
def gpt_run_test(req: GPTTestRequest) -> Dict[str, Any]:
    """
    GPT Developer Mode: Run test (browser or API)
    Unified endpoint for all test types
    """
    try:
        orchestrator = get_orchestrator_client()

        if req.test_type == "browser":
            result = orchestrator.browser_test(**req.config)
        elif req.test_type == "api":
            result = orchestrator.api_test(**req.config)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown test type: {req.test_type}")

        if result.get("ok"):
            return {
                "success": True,
                "test_type": req.test_type,
                "results": result.get("results") or result.get("data"),
                "message": result.get("message", "Test completed"),
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
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
