"""Workflow Orchestration Routes"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from clients.orchestrator_client import get_orchestrator_client
from models import OrchestrateWorkflowRequest

router = APIRouter(prefix="/mcp/workflows", tags=["Workflows"])


@router.post("/orchestrate")
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
