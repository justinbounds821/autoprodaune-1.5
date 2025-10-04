from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .models import (
    ContentItem, ContentAsset, ContentStatus, ContentCategory,
    ContentValidationError
)
from ..social_poster import PostMetadata, ContentType
from .content_storage import ContentStorage
from .content_validator import ContentValidator
from .asset_processor import AssetProcessor

class ContentManager:
    def __init__(self, storage_dir: str = "content_storage"):
        base = Path(storage_dir)
        self.storage = ContentStorage(str(base))
        self.validator = ContentValidator()
        self.assets = AssetProcessor(str(base / "thumbnails"))

        self.content_items: Dict[str, ContentItem] = {}
        self.asset_registry: Dict[str, ContentAsset] = {}
        self._load_content()

    def create_content_item(
        self,
        title: str,
        description: str,
        category: ContentCategory,
        content_type: ContentType,
        assets: List[str],
        target_platforms: Optional[List[str]] = None,
        metadata: Optional[PostMetadata] = None,
        tags: Optional[List[str]] = None,
        hashtags: Optional[List[str]] = None,
        created_by: Optional[str] = None,
        notes: Optional[str] = None
    ) -> ContentItem:
        processed: List[ContentAsset] = []
        for path in assets:
            data = self.assets.process_asset(path)
            a = ContentAsset(
                id=self.storage.generate_asset_id(path),
                file_path=path,
                file_type=Path(path).suffix.lstrip("."),
                mime_type=data["mime_type"],
                file_size=data["file_size"],
                thumbnail_path=data.get("thumbnail_path"),
                duration=data["metadata"].get("duration"),
                dimensions=data["metadata"].get("dimensions"),
                metadata=data["metadata"] or {},
            )
            self.asset_registry[a.id] = a
            processed.append(a)

        item = ContentItem(
            id=self.storage.generate_content_id(title),
            title=title,
            description=description,
            category=category,
            content_type=content_type,
            assets=processed,
            metadata=metadata or PostMetadata(title=title, description=description),
            status=ContentStatus.DRAFT,
            tags=tags or [],
            hashtags=hashtags or [],
            target_platforms=target_platforms or [],
            created_by=created_by,
            notes=notes
        )

        errors = self.validator.validate_content(item)
        if errors:
            raise ContentValidationError(", ".join(errors))

        self.content_items[item.id] = item
        self._save_content()
        return item

    def list_content_items(
        self,
        status: Optional[ContentStatus] = None,
        category: Optional[ContentCategory] = None,
        platform: Optional[str] = None
    ) -> List[ContentItem]:
        items = list(self.content_items.values())
        if status:
            items = [i for i in items if i.status == status]
        if category:
            items = [i for i in items if i.category == category]
        if platform:
            items = [i for i in items if platform in (i.target_platforms or [])]
        return items

    def update_content_status(self, content_id: str, status: ContentStatus) -> bool:
        item = self.content_items.get(content_id)
        if not item:
            return False
        item.status = status
        item.updated_at = datetime.now()
        self._save_content()
        return True

    def _save_content(self) -> None:
        data = {"assets": {}, "content_items": {}}
        for aid, a in self.asset_registry.items():
            data["assets"][aid] = {
                "id": a.id, "file_path": a.file_path, "file_type": a.file_type,
                "mime_type": a.mime_type, "file_size": a.file_size,
                "thumbnail_path": a.thumbnail_path, "duration": a.duration,
                "dimensions": a.dimensions, "metadata": a.metadata,
                "created_at": a.created_at.isoformat(), "updated_at": a.updated_at.isoformat()
            }
        for cid, i in self.content_items.items():
            data["content_items"][cid] = {
                "id": i.id, "title": i.title, "description": i.description,
                "category": i.category.value, "content_type": i.content_type.value,
                "assets": [{"id": a.id} for a in i.assets],
                "metadata": {
                    "title": i.metadata.title, "description": i.metadata.description,
                    "hashtags": i.metadata.hashtags, "mentions": i.metadata.mentions,
                    "location": i.metadata.location,
                    "scheduled_at": i.metadata.scheduled_at.isoformat() if i.metadata.scheduled_at else None,
                    "privacy": i.metadata.privacy, "category": i.metadata.category,
                    "custom_data": i.metadata.custom_data
                },
                "status": i.status.value, "tags": i.tags, "hashtags": i.hashtags,
                "target_platforms": i.target_platforms,
                "scheduled_at": i.scheduled_at.isoformat() if i.scheduled_at else None,
                "published_at": i.published_at.isoformat() if i.published_at else None,
                "created_at": i.created_at.isoformat(), "updated_at": i.updated_at.isoformat(),
                "created_by": i.created_by, "notes": i.notes
            }
        self.storage.save_content_data(data)

    def _load_content(self) -> None:
        try:
            d = self.storage.load_content_data()
            # assets
            from datetime import datetime as _dt
            for aid, a in d.get("assets", {}).items():
                self.asset_registry[aid] = ContentAsset(
                    id=a["id"], file_path=a["file_path"], file_type=a["file_type"],
                    mime_type=a["mime_type"], file_size=a["file_size"],
                    thumbnail_path=a.get("thumbnail_path"),
                    duration=a.get("duration"), dimensions=a.get("dimensions"),
                    metadata=a.get("metadata", {}),
                    created_at=_dt.fromisoformat(a["created_at"]),
                    updated_at=_dt.fromisoformat(a["updated_at"])
                )
            # items
            for cid, i in d.get("content_items", {}).items():
                assets = [self.asset_registry[x["id"]] for x in i.get("assets", []) if x["id"] in self.asset_registry]
                meta = PostMetadata(
                    title=i["metadata"]["title"],
                    description=i["metadata"]["description"],
                    hashtags=i["metadata"]["hashtags"],
                    mentions=i["metadata"]["mentions"],
                    location=i["metadata"]["location"],
                    scheduled_at=_dt.fromisoformat(i["metadata"]["scheduled_at"]) if i["metadata"]["scheduled_at"] else None,
                    privacy=i["metadata"]["privacy"],
                    category=i["metadata"]["category"],
                    custom_data=i["metadata"]["custom_data"],
                )
                self.content_items[cid] = ContentItem(
                    id=i["id"], title=i["title"], description=i["description"],
                    category=ContentCategory(i["category"]),
                    content_type=ContentType(i["content_type"]),
                    assets=assets, metadata=meta, status=ContentStatus(i["status"]),
                    tags=i["tags"], hashtags=i["hashtags"], target_platforms=i["target_platforms"],
                    scheduled_at=_dt.fromisoformat(i["scheduled_at"]) if i["scheduled_at"] else None,
                    published_at=_dt.fromisoformat(i["published_at"]) if i["published_at"] else None,
                    created_at=_dt.fromisoformat(i["created_at"]),
                    updated_at=_dt.fromisoformat(i["updated_at"]),
                    created_by=i["created_by"], notes=i["notes"]
                )
        except Exception as e:
            import logging; logging.getLogger(__name__).warning("Load content failed: %s", e)

    def process_assets(self, item_id: str):
        from .asset_processor import process_image
        item = self.get_content_item(item_id)
        if not item:
            return {"error": "not_found"}

        results = []
        for asset in item.assets:
            # folosim funcția process_image pentru imagini
            results.append(process_image(asset.file_path))
        
        # atașează rezultatele la item
        item.process_info = {"assets": results}
        self._save_item(item)
        return results
