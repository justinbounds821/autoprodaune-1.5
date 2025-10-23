"""
Workflow Orchestration Routes
Complex multi-step workflow orchestration via the orchestrator
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from clients.orchestrator_client import get_orchestrator_client

router = APIRouter(
    prefix="/mcp/workflows",
    tags=["Workflows"],
    responses={404: {"description": "Not found"}},
)


# ==================== MODELS ====================


class OrchestrateWorkflowRequest(BaseModel):
    command: str
    context: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None


# ==================== ROUTES ====================


@router.post("/orchestrate")
def orchestrate_workflow(req: OrchestrateWorkflowRequest) -> Dict[str, Any]:
    """
    Orchestrate a complete workflow using the orchestrator
    
    This is the main entry point for complex multi-step operations.
    The orchestrator will analyze the command, break it down into tasks,
    and execute them in the appropriate order.
    
    Args:
        req: OrchestrateWorkflowRequest with command, context, and options
        
    Returns:
        Workflow execution result with tasks, prompts, and status
        
    Raises:
        HTTPException: 500 if orchestration fails
        
    Example:
        ```json
        {
            "command": "Create Linear task and GitHub issue for bug fix",
            "context": {
                "bug_description": "Login page shows 404",
                "priority": "high"
            },
            "options": {
                "auto_execute": true
            }
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
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
def analyze_workflow(req: OrchestrateWorkflowRequest) -> Dict[str, Any]:
    """
    Analyze a workflow without executing it
    
    Returns what would happen if the workflow was executed,
    including task breakdown and estimated execution time.
    
    Args:
        req: OrchestrateWorkflowRequest with command and context
        
    Returns:
        Workflow analysis with task breakdown and estimates
    """
    try:
        orchestrator = get_orchestrator_client()
        # Add analyze-only option
        options = req.options or {}
        options["auto_execute"] = False
        options["analyze_only"] = True
        
        result = orchestrator.orchestrate_workflow(
            command=req.command,
            context=req.context,
            options=options,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{workflow_id}")
def workflow_status(workflow_id: str) -> Dict[str, Any]:
    """
    Get workflow execution status
    
    Args:
        workflow_id: Unique workflow identifier
        
    Returns:
        Workflow status and progress
        
    Note:
        This endpoint requires workflow tracking in the orchestrator
    """
    try:
        orchestrator = get_orchestrator_client()
        # This would require the orchestrator to implement workflow tracking
        return {
            "workflow_id": workflow_id,
            "status": "unknown",
            "message": "Workflow tracking not yet implemented in orchestrator",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
def list_workflow_templates() -> Dict[str, Any]:
    """
    List available workflow templates
    
    Returns:
        List of pre-defined workflow templates with descriptions
    """
    return {
        "templates": [
            {
                "id": "bug_fix_workflow",
                "name": "Bug Fix Workflow",
                "description": "Create Linear task, GitHub issue, and commit fix",
                "steps": ["linear_task", "github_issue", "github_commit", "supabase_verify"],
            },
            {
                "id": "feature_workflow",
                "name": "Feature Development Workflow",
                "description": "Plan feature, create tasks, implement, test, deploy",
                "steps": ["linear_task", "github_issue", "browser_test", "api_test"],
            },
            {
                "id": "test_workflow",
                "name": "Testing Workflow",
                "description": "Execute browser and API tests, verify database",
                "steps": ["browser_test", "api_test", "supabase_verify"],
            },
            {
                "id": "deployment_workflow",
                "name": "Deployment Workflow",
                "description": "Run tests, commit changes, create deployment",
                "steps": ["api_test", "github_commit", "system_health"],
            },
        ],
        "total": 4,
    }


@router.post("/template/{template_id}")
def execute_template(
    template_id: str,
    context: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Execute a pre-defined workflow template
    
    Args:
        template_id: Template identifier
        context: Template execution context
        options: Optional execution options
        
    Returns:
        Workflow execution result
    """
    templates = {
        "bug_fix_workflow": "Create Linear task and GitHub issue, then commit fix",
        "feature_workflow": "Plan and implement feature with testing",
        "test_workflow": "Execute comprehensive testing suite",
        "deployment_workflow": "Deploy after testing and verification",
    }
    
    if template_id not in templates:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
    
    try:
        orchestrator = get_orchestrator_client()
        result = orchestrator.orchestrate_workflow(
            command=templates[template_id],
            context=context,
            options=options,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
