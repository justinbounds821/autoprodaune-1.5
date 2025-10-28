from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from .clients import github_client, linear_client, supabase_client

router = APIRouter()

class DispatchRequest(BaseModel):
    target: str
    action: str
    payload: Dict[str, Any]

@router.post("/dispatch")
async def dispatch(request: DispatchRequest):
    if request.target == "github":
        if request.action == "create_issue":
            return await github_client.create_issue(**request.payload)
        elif request.action == "create_commit":
            return await github_client.create_commit(**request.payload)

    elif request.target == "linear":
        if request.action == "create_task":
            return await linear_client.create_task(**request.payload)

    elif request.target == "supabase":
        if request.action == "query":
            return await supabase_client.query_table(**request.payload)

    return {"error": "Unknown target or action"}
