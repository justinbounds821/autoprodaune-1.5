# services/api/app/routes/content.py
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.content_manager import ContentManager, ContentCategory
from ..services.content import ContentType, PostMetadata

router = APIRouter(prefix="/api/content", tags=["content"])
cm = ContentManager("content_storage")

class CreateContentBody(BaseModel):
    title: str
    description: str = ""
    category: ContentCategory = ContentCategory.INFORMATIONAL
    content_type: ContentType = ContentType.IMAGE
    assets: List[str] = Field(default_factory=list)
    target_platforms: List[str] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None

@router.get("/", summary="List content items")
def list_items() -> List[Dict[str, Any]]:
    return [i.__dict__ for i in cm.list_content_items()]

@router.post("/", summary="Create content item")
def create_item(body: CreateContentBody) -> Dict[str, Any]:
    item = cm.create_content_item(
        title=body.title,
        description=body.description,
        category=body.category,
        content_type=body.content_type,
        assets=body.assets,
        target_platforms=body.target_platforms,
        metadata=PostMetadata(**(body.metadata or {})),
    )
    return {"id": item.id, "status": item.status, "item": item.__dict__}

@router.get("/{item_id}", summary="Get one content item")
def get_item(item_id: str) -> Dict[str, Any]:
    item = cm.get_content_item(item_id)
    if not item:
        raise HTTPException(404, "Not found")
    return item.__dict__

@router.post("/{item_id}/validate", summary="Validate item")
def validate_item(item_id: str) -> Dict[str, Any]:
    ok, errors = cm.validate_item(item_id)
    return {"valid": ok, "errors": errors}

@router.post("/{item_id}/process-assets", summary="Process assets (thumbs/metadata)")
def process_assets(item_id: str) -> Dict[str, Any]:
    result = cm.process_assets(item_id)
    return {"processed": True, "result": result}
